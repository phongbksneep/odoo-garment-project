from odoo import models, fields, api


class GarmentPieceRate(models.Model):
    _name = 'garment.piece.rate'
    _description = 'Piece Rate Configuration'
    _order = 'style_id, operation'

    style_id = fields.Many2one(
        'garment.style',
        string='Mã Hàng',
        required=True,
    )
    operation = fields.Selection([
        ('sewing', 'May'),
        ('cutting', 'Cắt'),
        ('finishing', 'Hoàn Tất'),
        ('pressing', 'Ủi'),
        ('packing', 'Đóng Gói'),
        ('qc', 'Kiểm Hàng'),
        ('other', 'Khác'),
    ], string='Công Đoạn', required=True, default='sewing')

    operation_detail = fields.Char(
        string='Chi Tiết Công Đoạn',
        help='VD: May cổ, may tay, may thân...',
    )
    rate_per_piece = fields.Float(
        string='Đơn Giá/Sản Phẩm (VNĐ)',
        required=True,
        digits=(10, 0),
    )
    smv = fields.Float(
        string='SMV',
        digits=(10, 2),
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        default=lambda self: self.env.company.currency_id,
    )
    active = fields.Boolean(default=True)
    notes = fields.Char(string='Ghi Chú')

    _rate_positive = models.Constraint(
        'CHECK(rate_per_piece >= 0)',
        'Đơn giá phải >= 0!',
    )
