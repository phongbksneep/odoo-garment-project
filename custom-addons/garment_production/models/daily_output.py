from odoo import models, fields, api


class GarmentDailyOutput(models.Model):
    _name = 'garment.daily.output'
    _description = 'Sản Lượng Hàng Ngày'
    _order = 'date desc, sewing_line_id'

    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
        required=True,
        ondelete='cascade',
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
        related='production_order_id.sewing_line_id',
        store=True,
    )
    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    shift = fields.Selection([
        ('morning', 'Ca Sáng'),
        ('afternoon', 'Ca Chiều'),
        ('night', 'Ca Tối'),
        ('overtime', 'Tăng Ca'),
    ], string='Ca Làm Việc', required=True, default='morning')

    target_qty = fields.Integer(
        string='Mục Tiêu (sp)',
        help='Số lượng mục tiêu trong ca',
    )
    output_qty = fields.Integer(
        string='Sản Lượng Đạt (sp)',
        required=True,
    )
    defect_qty = fields.Integer(
        string='Số Lượng Lỗi (sp)',
        default=0,
    )
    rework_qty = fields.Integer(
        string='Sửa Lại (sp)',
        default=0,
    )
    worker_count = fields.Integer(
        string='Số CN Làm Việc',
    )
    working_hours = fields.Float(
        string='Giờ Làm Việc',
        default=8.0,
    )
    efficiency = fields.Float(
        string='Hiệu Suất (%)',
        compute='_compute_efficiency',
        store=True,
    )
    defect_rate = fields.Float(
        string='Tỷ Lệ Lỗi (%)',
        compute='_compute_defect_rate',
        store=True,
    )
    notes = fields.Text(
        string='Ghi Chú / Nguyên Nhân',
    )

    @api.depends('target_qty', 'output_qty')
    def _compute_efficiency(self):
        for record in self:
            if record.target_qty:
                record.efficiency = (record.output_qty / record.target_qty) * 100
            else:
                record.efficiency = 0.0

    @api.depends('output_qty', 'defect_qty')
    def _compute_defect_rate(self):
        for record in self:
            total = record.output_qty + record.defect_qty
            if total:
                record.defect_rate = (record.defect_qty / total) * 100
            else:
                record.defect_rate = 0.0
