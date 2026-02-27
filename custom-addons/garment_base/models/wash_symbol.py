from odoo import models, fields


class GarmentWashSymbol(models.Model):
    _name = 'garment.wash.symbol'
    _description = 'Ký Hiệu Giặt Ủi (Wash Care Symbol)'
    _order = 'category, sequence'

    name = fields.Char(
        string='Tên Ký Hiệu',
        required=True,
    )
    code = fields.Char(
        string='Mã',
        required=True,
    )
    category = fields.Selection([
        ('wash', 'Giặt (Washing)'),
        ('bleach', 'Tẩy (Bleaching)'),
        ('dry', 'Sấy (Drying)'),
        ('iron', 'Ủi (Ironing)'),
        ('dryclean', 'Giặt Khô (Dry Cleaning)'),
    ], string='Phân Loại', required=True)

    instruction = fields.Char(
        string='Hướng Dẫn',
        help='VD: Giặt máy ở 30°C, Không tẩy, Ủi nhiệt độ thấp',
    )
    icon = fields.Binary(string='Biểu Tượng')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
