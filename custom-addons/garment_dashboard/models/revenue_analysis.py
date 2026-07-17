from odoo import fields, models, tools


class GarmentRevenueAnalysis(models.Model):
    """Phân tích doanh thu theo khách hàng / mã hàng / tháng
    (đơn hàng đã xác nhận trở đi)."""
    _name = 'garment.revenue.analysis'
    _description = 'Phân Tích Doanh Thu'
    _auto = False
    _order = 'order_month desc'

    order_month = fields.Date(string='Tháng', readonly=True)
    customer_id = fields.Many2one(
        'res.partner', string='Khách Hàng', readonly=True)
    style_id = fields.Many2one(
        'garment.style', string='Mã Hàng', readonly=True)
    state = fields.Selection([
        ('confirmed', 'Đã Xác Nhận'), ('material', 'Chuẩn Bị NL'),
        ('cutting', 'Đang Cắt'), ('sewing', 'Đang May'),
        ('finishing', 'Hoàn Thiện'), ('qc', 'Kiểm Tra'),
        ('packing', 'Đóng Gói'), ('shipped', 'Đã Giao'),
        ('done', 'Hoàn Thành'),
    ], string='Trạng Thái', readonly=True)
    order_count = fields.Integer(string='Số Đơn', readonly=True)
    total_qty = fields.Integer(string='Tổng SL (sp)', readonly=True)
    total_amount = fields.Float(string='Doanh Thu', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    MIN(o.id) AS id,
                    DATE_TRUNC('month', o.order_date)::date AS order_month,
                    o.customer_id AS customer_id,
                    o.style_id AS style_id,
                    o.state AS state,
                    COUNT(*) AS order_count,
                    SUM(o.total_qty) AS total_qty,
                    SUM(o.total_amount) AS total_amount
                FROM garment_order o
                WHERE o.state NOT IN ('draft', 'cancelled')
                GROUP BY
                    DATE_TRUNC('month', o.order_date),
                    o.customer_id, o.style_id, o.state
            )
        """ % self._table)
