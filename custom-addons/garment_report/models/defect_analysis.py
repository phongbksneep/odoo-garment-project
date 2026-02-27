from odoo import models, fields, tools


class GarmentDefectAnalysis(models.Model):
    """SQL View for defect rate analysis per style/line."""
    _name = 'garment.defect.analysis'
    _description = 'Defect Rate Analysis'
    _auto = False
    _order = 'inspection_date desc'

    inspection_date = fields.Datetime(string='Ngày Kiểm', readonly=True)
    style_id = fields.Many2one(
        'garment.style', string='Mã Hàng', readonly=True,
    )
    production_order_id = fields.Many2one(
        'garment.production.order', string='Lệnh SX', readonly=True,
    )
    defect_type_id = fields.Many2one(
        'garment.defect.type', string='Loại Lỗi', readonly=True,
    )
    total_inspected = fields.Integer(
        string='Tổng Kiểm Tra', readonly=True,
    )
    total_defects = fields.Integer(
        string='Tổng Lỗi', readonly=True,
    )
    defect_rate = fields.Float(
        string='Tỷ Lệ Lỗi (%)', readonly=True, digits=(10, 2),
    )
    result = fields.Selection([
        ('pass', 'Đạt'),
        ('fail', 'Không Đạt'),
        ('rework', 'Sửa Lại'),
    ], string='Kết Quả', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    MIN(dl.id) AS id,
                    qi.inspection_date AS inspection_date,
                    qi.style_id AS style_id,
                    qi.production_order_id AS production_order_id,
                    dl.defect_type_id AS defect_type_id,
                    qi.inspected_qty AS total_inspected,
                    SUM(dl.quantity) AS total_defects,
                    CASE
                        WHEN COALESCE(qi.inspected_qty, 0) > 0
                        THEN SUM(dl.quantity)::float
                            / qi.inspected_qty * 100
                        ELSE 0
                    END AS defect_rate,
                    qi.result AS result
                FROM garment_qc_defect_line dl
                LEFT JOIN garment_qc_inspection qi
                    ON dl.inspection_id = qi.id
                GROUP BY
                    qi.inspection_date,
                    qi.style_id,
                    qi.production_order_id,
                    dl.defect_type_id,
                    qi.inspected_qty,
                    qi.result
            )
        """ % self._table)
