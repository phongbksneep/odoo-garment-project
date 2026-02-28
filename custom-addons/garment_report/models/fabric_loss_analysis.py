from odoo import models, fields, tools


class GarmentFabricLossAnalysis(models.Model):
    """SQL View: Fabric loss / variance analysis per cutting order.

    Compares planned fabric consumption (marker length × layers) with actual
    fabric used to identify waste, variance, and cutting efficiency.
    """
    _name = 'garment.fabric.loss.analysis'
    _description = 'Fabric Loss Analysis'
    _auto = False
    _order = 'loss_pct desc'

    # --- Dimensions ---
    cutting_order_id = fields.Many2one(
        'garment.cutting.order.adv', string='Lệnh Cắt', readonly=True,
    )
    production_order_id = fields.Many2one(
        'garment.production.order', string='Lệnh Sản Xuất', readonly=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng', readonly=True,
    )
    style_id = fields.Many2one(
        'garment.style', string='Mã Hàng', readonly=True,
    )
    fabric_id = fields.Many2one(
        'garment.fabric', string='Vải', readonly=True,
    )
    cutter_id = fields.Many2one(
        'hr.employee', string='Thợ Cắt', readonly=True,
    )
    date = fields.Date(string='Ngày Cắt', readonly=True)
    state = fields.Char(string='Trạng Thái', readonly=True)

    # --- Marker & Spreading ---
    marker_length = fields.Float(
        string='Dài Sơ Đồ (m)', readonly=True, digits=(10, 2),
    )
    marker_efficiency = fields.Float(
        string='Hiệu Suất Sơ Đồ (%)', readonly=True, digits=(5, 2),
    )
    total_layers = fields.Integer(string='Số Lớp Trải', readonly=True)

    # --- Consumption ---
    planned_fabric = fields.Float(
        string='Vải Kế Hoạch (m)',
        readonly=True,
        digits=(10, 2),
        help='marker_length × total_layers',
    )
    actual_fabric = fields.Float(
        string='Vải Thực Tế (m)',
        readonly=True,
        digits=(10, 2),
        help='Tổng chiều dài các lớp trải thực tế',
    )
    fabric_variance = fields.Float(
        string='Chênh Lệch Vải (m)',
        readonly=True,
        digits=(10, 2),
        help='Thực tế - Kế hoạch (dương = dùng nhiều hơn)',
    )
    loss_pct = fields.Float(
        string='Hao Hụt (%)',
        readonly=True,
        digits=(10, 2),
        help='(Thực tế - Kế hoạch) / Kế hoạch × 100',
    )

    # --- Output & Quality ---
    total_pieces_cut = fields.Integer(
        string='SL Cắt', readonly=True,
    )
    defective_pieces = fields.Integer(
        string='SL Lỗi Cắt', readonly=True,
    )
    wastage_kg = fields.Float(
        string='Phế Liệu (kg)', readonly=True, digits=(10, 2),
    )
    good_cut_rate = fields.Float(
        string='Tỷ Lệ Cắt Đạt (%)',
        readonly=True,
        digits=(10, 2),
    )
    fabric_per_piece = fields.Float(
        string='Vải / SP (m)',
        readonly=True,
        digits=(10, 4),
        help='Actual fabric / pieces cut',
    )

    # --- Layer Quality ---
    total_defects = fields.Integer(
        string='Lỗi Vải (Lớp)', readonly=True,
    )
    total_splices = fields.Integer(
        string='Mối Nối', readonly=True,
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    co.id AS id,
                    co.id AS cutting_order_id,
                    co.production_order_id AS production_order_id,
                    co.garment_order_id AS garment_order_id,
                    co.style_id AS style_id,
                    co.fabric_id AS fabric_id,
                    co.cutter_id AS cutter_id,
                    co.date AS date,
                    co.state AS state,

                    -- Marker & Spreading
                    co.marker_length AS marker_length,
                    co.marker_efficiency AS marker_efficiency,
                    co.total_layers AS total_layers,

                    -- Consumption
                    CASE
                        WHEN co.marker_length > 0 AND co.total_layers > 0
                        THEN co.marker_length * co.total_layers
                        ELSE 0
                    END AS planned_fabric,
                    co.total_fabric_used AS actual_fabric,
                    co.total_fabric_used - (
                        CASE
                            WHEN co.marker_length > 0 AND co.total_layers > 0
                            THEN co.marker_length * co.total_layers
                            ELSE 0
                        END
                    ) AS fabric_variance,
                    CASE
                        WHEN co.marker_length > 0 AND co.total_layers > 0
                        THEN (co.total_fabric_used
                              - co.marker_length * co.total_layers)
                             * 100.0
                             / (co.marker_length * co.total_layers)
                        ELSE 0
                    END AS loss_pct,

                    -- Output & Quality
                    co.total_pieces_cut AS total_pieces_cut,
                    co.defective_pieces AS defective_pieces,
                    co.wastage_kg AS wastage_kg,
                    CASE
                        WHEN co.total_pieces_cut > 0
                        THEN (co.total_pieces_cut - co.defective_pieces)
                             * 100.0 / co.total_pieces_cut
                        ELSE 0
                    END AS good_cut_rate,
                    CASE
                        WHEN co.total_pieces_cut > 0
                        THEN co.total_fabric_used / co.total_pieces_cut
                        ELSE 0
                    END AS fabric_per_piece,

                    -- Layer quality aggregated
                    layer_agg.total_defects AS total_defects,
                    layer_agg.total_splices AS total_splices

                FROM garment_cutting_order_adv co
                LEFT JOIN LATERAL (
                    SELECT
                        COALESCE(SUM(cl.defects_found), 0) AS total_defects,
                        COALESCE(SUM(cl.splice_count), 0) AS total_splices
                    FROM garment_cutting_layer cl
                    WHERE cl.cutting_order_id = co.id
                ) layer_agg ON TRUE
            )
        """ % self._table)
