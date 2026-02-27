from odoo import models, fields, api


class GarmentWorkerOutput(models.Model):
    _name = 'garment.worker.output'
    _description = 'Worker Daily Output'
    _order = 'date desc, employee_id'

    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Công Nhân',
        required=True,
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mã Hàng',
        required=True,
    )
    piece_rate_id = fields.Many2one(
        'garment.piece.rate',
        string='Đơn Giá',
        domain="[('style_id', '=', style_id)]",
    )
    operation = fields.Selection(
        related='piece_rate_id.operation',
        store=True,
        readonly=True,
    )
    quantity = fields.Integer(
        string='Số Lượng',
        required=True,
    )
    rate_per_piece = fields.Float(
        related='piece_rate_id.rate_per_piece',
        store=True,
        readonly=True,
        string='Đơn Giá/SP',
    )
    amount = fields.Float(
        string='Thành Tiền (VNĐ)',
        compute='_compute_amount',
        store=True,
        digits=(10, 0),
    )
    overtime_hours = fields.Float(
        string='Giờ Tăng Ca',
        digits=(10, 1),
    )
    notes = fields.Char(string='Ghi Chú')

    @api.depends('quantity', 'rate_per_piece')
    def _compute_amount(self):
        for record in self:
            record.amount = record.quantity * record.rate_per_piece
