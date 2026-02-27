from odoo import models, fields, api


class GarmentColor(models.Model):
    _name = 'garment.color'
    _description = 'Bảng Màu'
    _order = 'sequence, name'

    name = fields.Char(
        string='Tên Màu',
        required=True,
    )
    code = fields.Char(
        string='Mã Màu',
        required=True,
    )
    html_color = fields.Char(
        string='Mã Màu HTML',
        help='Mã màu HEX, VD: #FF0000',
    )
    pantone_code = fields.Char(
        string='Mã Pantone',
        help='Mã màu Pantone tiêu chuẩn',
    )
    sequence = fields.Integer(
        string='Thứ Tự',
        default=10,
    )
    active = fields.Boolean(
        string='Đang Sử Dụng',
        default=True,
    )

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã màu phải là duy nhất!',
    )
