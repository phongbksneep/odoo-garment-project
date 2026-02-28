from odoo import models, fields, tools


class GarmentCostAnalysis(models.Model):
    """SQL View: Cost vs Actual analysis per production order.

    Compares planned costs (from cost sheets) with actual production output
    to identify cost variances and profitability.
    """
    _name = 'garment.cost.analysis'
    _description = 'Cost vs Actual Analysis'
    _auto = False
    _order = 'variance_pct desc'

    # --- Dimensions ---
    production_order_id = fields.Many2one(
        'garment.production.order', string='Lệnh Sản Xuất', readonly=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng', readonly=True,
    )
    style_id = fields.Many2one(
        'garment.style', string='Mã Hàng', readonly=True,
    )
    customer_id = fields.Many2one(
        'res.partner', string='Khách Hàng', readonly=True,
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line', string='Chuyền May', readonly=True,
    )
    state = fields.Char(string='Trạng Thái LSX', readonly=True)

    # --- Planned (from cost sheet) ---
    cost_sheet_id = fields.Many2one(
        'garment.cost.sheet', string='Bảng Giá Thành', readonly=True,
    )
    planned_qty = fields.Integer(string='SL Kế Hoạch', readonly=True)
    cost_per_pc = fields.Float(
        string='Giá Thành / SP (Kế Hoạch)',
        readonly=True,
        digits=(10, 4),
    )
    selling_price = fields.Float(
        string='Giá Bán / SP',
        readonly=True,
        digits=(10, 4),
    )
    planned_material_cost = fields.Float(
        string='NVL / SP (Kế Hoạch)',
        readonly=True,
        digits=(10, 4),
    )
    planned_cm_cost = fields.Float(
        string='Gia Công / SP (Kế Hoạch)',
        readonly=True,
        digits=(10, 4),
    )
    planned_total_cost = fields.Float(
        string='Tổng Chi Phí Kế Hoạch',
        readonly=True,
        digits=(10, 2),
    )
    planned_revenue = fields.Float(
        string='Doanh Thu Kế Hoạch',
        readonly=True,
        digits=(10, 2),
    )

    # --- Actual (from production orders) ---
    completed_qty = fields.Integer(
        string='SL Thực Tế', readonly=True,
    )
    defect_qty = fields.Integer(
        string='SL Lỗi', readonly=True,
    )
    completion_rate = fields.Float(
        string='Tỷ Lệ Hoàn Thành (%)',
        readonly=True,
        digits=(10, 2),
    )
    actual_total_cost = fields.Float(
        string='Chi Phí Thực Tế (Ước Tính)',
        readonly=True,
        digits=(10, 2),
    )
    actual_revenue = fields.Float(
        string='Doanh Thu Thực Tế',
        readonly=True,
        digits=(10, 2),
    )

    # --- Variance ---
    cost_variance = fields.Float(
        string='Chênh Lệch Chi Phí',
        readonly=True,
        digits=(10, 2),
    )
    variance_pct = fields.Float(
        string='Chênh Lệch (%)',
        readonly=True,
        digits=(10, 2),
    )
    profit_planned = fields.Float(
        string='Lợi Nhuận Kế Hoạch',
        readonly=True,
        digits=(10, 2),
    )
    profit_actual = fields.Float(
        string='Lợi Nhuận Thực Tế (Ước Tính)',
        readonly=True,
        digits=(10, 2),
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    po.id AS id,
                    po.id AS production_order_id,
                    po.garment_order_id AS garment_order_id,
                    po.style_id AS style_id,
                    po.customer_id AS customer_id,
                    po.sewing_line_id AS sewing_line_id,
                    po.state AS state,

                    -- Cost Sheet link (latest approved for same style)
                    cs.id AS cost_sheet_id,

                    -- Planned
                    po.planned_qty AS planned_qty,
                    COALESCE(cs.cost_price, 0) AS cost_per_pc,
                    COALESCE(cs.selling_price, 0) AS selling_price,
                    COALESCE(cs.total_material_cost, 0) AS planned_material_cost,
                    COALESCE(cs.cm_cost, 0) AS planned_cm_cost,
                    COALESCE(cs.cost_price, 0) * po.planned_qty
                        AS planned_total_cost,
                    COALESCE(cs.selling_price, 0) * po.planned_qty
                        AS planned_revenue,

                    -- Actual
                    po.completed_qty AS completed_qty,
                    po.defect_qty AS defect_qty,
                    CASE
                        WHEN po.planned_qty > 0
                        THEN po.completed_qty * 100.0 / po.planned_qty
                        ELSE 0
                    END AS completion_rate,
                    COALESCE(cs.cost_price, 0) * po.completed_qty
                        AS actual_total_cost,
                    COALESCE(cs.selling_price, 0) * po.completed_qty
                        AS actual_revenue,

                    -- Variance (planned - actual, positive = under budget)
                    COALESCE(cs.cost_price, 0) * (po.planned_qty - po.completed_qty)
                        AS cost_variance,
                    CASE
                        WHEN po.planned_qty > 0
                        THEN (po.planned_qty - po.completed_qty) * 100.0
                             / po.planned_qty
                        ELSE 0
                    END AS variance_pct,

                    -- Profit
                    (COALESCE(cs.selling_price, 0) - COALESCE(cs.cost_price, 0))
                        * po.planned_qty AS profit_planned,
                    (COALESCE(cs.selling_price, 0) - COALESCE(cs.cost_price, 0))
                        * po.completed_qty AS profit_actual

                FROM garment_production_order po
                LEFT JOIN LATERAL (
                    SELECT cs2.*
                    FROM garment_cost_sheet cs2
                    WHERE cs2.style_id = po.style_id
                      AND cs2.state = 'approved'
                    ORDER BY cs2.revision DESC, cs2.id DESC
                    LIMIT 1
                ) cs ON TRUE
            )
        """ % self._table)
