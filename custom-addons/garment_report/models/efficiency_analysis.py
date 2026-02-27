from odoo import models, fields, tools


class GarmentEfficiencyAnalysis(models.Model):
    """SQL View for sewing line efficiency analysis."""
    _name = 'garment.efficiency.analysis'
    _description = 'Sewing Line Efficiency Analysis'
    _auto = False
    _order = 'date desc'

    date = fields.Date(string='Ngày', readonly=True)
    sewing_line_id = fields.Many2one(
        'garment.sewing.line', string='Chuyền May', readonly=True,
    )
    production_order_id = fields.Many2one(
        'garment.production.order', string='Lệnh SX', readonly=True,
    )
    style_id = fields.Many2one(
        'garment.style', string='Mã Hàng', readonly=True,
    )
    worker_count = fields.Integer(string='Số Công Nhân', readonly=True)
    total_output = fields.Integer(string='Tổng Sản Lượng', readonly=True)
    smv = fields.Float(string='SAM', readonly=True, digits=(10, 2))
    working_minutes = fields.Float(
        string='Phút Làm Việc', readonly=True, digits=(10, 1),
    )
    earned_minutes = fields.Float(
        string='Phút Kiếm Được', readonly=True, digits=(10, 1),
    )
    efficiency = fields.Float(
        string='Hiệu Suất (%)', readonly=True, digits=(10, 2),
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    dout.id AS id,
                    dout.date AS date,
                    dout.sewing_line_id AS sewing_line_id,
                    dout.production_order_id AS production_order_id,
                    po.style_id AS style_id,
                    sl.worker_count AS worker_count,
                    dout.output_qty AS total_output,
                    COALESCE(gs.sam, 0) AS smv,
                    COALESCE(sl.worker_count * 480, 0) AS working_minutes,
                    COALESCE(dout.output_qty * gs.sam, 0) AS earned_minutes,
                    CASE
                        WHEN COALESCE(sl.worker_count, 0) > 0
                            AND COALESCE(gs.sam, 0) > 0
                        THEN (dout.output_qty * gs.sam)
                            / (sl.worker_count * 480.0) * 100
                        ELSE 0
                    END AS efficiency
                FROM garment_daily_output dout
                LEFT JOIN garment_production_order po
                    ON dout.production_order_id = po.id
                LEFT JOIN garment_style gs
                    ON po.style_id = gs.id
                LEFT JOIN garment_sewing_line sl
                    ON dout.sewing_line_id = sl.id
            )
        """ % self._table)
