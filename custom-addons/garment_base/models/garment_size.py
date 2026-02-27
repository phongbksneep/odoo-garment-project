from odoo import models, fields, api


class GarmentSize(models.Model):
    _name = 'garment.size'
    _description = 'Bảng Size'
    _order = 'sequence, name'

    name = fields.Char(
        string='Tên Size',
        required=True,
    )
    code = fields.Char(
        string='Mã Size',
        required=True,
    )
    size_type = fields.Selection([
        ('letter', 'Chữ (S, M, L, XL...)'),
        ('number', 'Số (38, 39, 40...)'),
        ('age', 'Tuổi (1-2, 3-4...)'),
        ('custom', 'Tùy Chỉnh'),
    ], string='Loại Size', required=True, default='letter')

    chest = fields.Float(string='Ngực (cm)')
    waist = fields.Float(string='Eo (cm)')
    hip = fields.Float(string='Hông (cm)')
    length = fields.Float(string='Dài (cm)')
    shoulder = fields.Float(string='Vai (cm)')
    sleeve = fields.Float(string='Tay (cm)')
    inseam = fields.Float(string='Dài Đáy (cm)')

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
        'Mã size phải là duy nhất!',
    )
