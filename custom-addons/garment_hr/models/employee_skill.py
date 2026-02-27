from odoo import models, fields


class GarmentEmployeeSkill(models.Model):
    _name = 'garment.employee.skill'
    _description = 'Tay Nghề Công Nhân'
    _order = 'employee_id, skill_type'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Công Nhân',
        required=True,
        ondelete='cascade',
    )
    skill_type = fields.Selection([
        ('sewing', 'May'),
        ('cutting', 'Cắt'),
        ('pressing', 'Ủi'),
        ('finishing', 'Hoàn Thiện'),
        ('qc', 'Kiểm Hàng'),
        ('packing', 'Đóng Gói'),
        ('embroidery', 'Thêu'),
        ('printing', 'In'),
        ('washing', 'Giặt'),
        ('pattern', 'Rập / Sơ Đồ'),
        ('mechanic', 'Thợ Máy'),
        ('driver', 'Lái Xe'),
        ('other', 'Khác'),
    ], string='Kỹ Năng', required=True)

    level = fields.Selection([
        ('beginner', 'Học Việc'),
        ('basic', 'Cơ Bản'),
        ('intermediate', 'Trung Bình'),
        ('advanced', 'Nâng Cao'),
        ('expert', 'Chuyên Gia'),
    ], string='Trình Độ', required=True, default='basic')

    detail = fields.Char(
        string='Chi Tiết',
        help='VD: May cổ áo sơ mi, may túi quần...',
    )
    certified = fields.Boolean(string='Có Chứng Chỉ')
    notes = fields.Char(string='Ghi Chú')
