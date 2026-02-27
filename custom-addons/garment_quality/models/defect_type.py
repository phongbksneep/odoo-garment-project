from odoo import models, fields


class GarmentDefectType(models.Model):
    _name = 'garment.defect.type'
    _description = 'Loại Lỗi May'
    _order = 'sequence, name'

    name = fields.Char(
        string='Tên Lỗi',
        required=True,
    )
    code = fields.Char(
        string='Mã Lỗi',
        required=True,
    )
    category = fields.Selection([
        ('fabric', 'Lỗi Vải'),
        ('sewing', 'Lỗi May'),
        ('cutting', 'Lỗi Cắt'),
        ('pressing', 'Lỗi Ủi'),
        ('finishing', 'Lỗi Hoàn Thiện'),
        ('measurement', 'Lỗi Đo'),
        ('color', 'Lỗi Màu'),
        ('stain', 'Vết Bẩn'),
        ('other', 'Khác'),
    ], string='Phân Loại', required=True)

    severity = fields.Selection([
        ('minor', 'Nhẹ (Minor)'),
        ('major', 'Nặng (Major)'),
        ('critical', 'Nghiêm Trọng (Critical)'),
    ], string='Mức Độ', required=True, default='minor')

    description = fields.Text(
        string='Mô Tả',
    )
    corrective_action = fields.Text(
        string='Biện Pháp Khắc Phục',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã lỗi phải là duy nhất!',
    )
