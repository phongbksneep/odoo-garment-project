from odoo import models, fields, api


class GarmentVehicle(models.Model):
    _name = 'garment.vehicle'
    _description = 'Phương Tiện Vận Chuyển'
    _order = 'name'

    name = fields.Char(
        string='Tên Phương Tiện',
        required=True,
    )
    plate_number = fields.Char(
        string='Biển Số',
        required=True,
    )
    vehicle_type = fields.Selection([
        ('truck_small', 'Xe Tải Nhỏ (< 2.5T)'),
        ('truck_medium', 'Xe Tải Trung (2.5 - 8T)'),
        ('truck_large', 'Xe Tải Lớn (> 8T)'),
        ('container_20', 'Container 20ft'),
        ('container_40', 'Container 40ft'),
        ('van', 'Xe Van'),
        ('motorbike', 'Xe Máy'),
        ('other', 'Khác'),
    ], string='Loại Xe', required=True, default='truck_small')

    driver_id = fields.Many2one(
        'hr.employee',
        string='Tài Xế Chính',
    )
    max_weight = fields.Float(
        string='Tải Trọng Tối Đa (Kg)',
    )
    max_volume = fields.Float(
        string='Thể Tích Tối Đa (m³)',
    )

    state = fields.Selection([
        ('available', 'Sẵn Sàng'),
        ('in_use', 'Đang Sử Dụng'),
        ('maintenance', 'Bảo Trì'),
        ('retired', 'Ngừng Sử Dụng'),
    ], string='Trạng Thái', default='available')

    registration_date = fields.Date(string='Ngày Đăng Ký')
    insurance_expiry = fields.Date(string='Hạn Bảo Hiểm')
    notes = fields.Text(string='Ghi Chú')

    delivery_ids = fields.One2many(
        'garment.delivery.order',
        'vehicle_id',
        string='Lịch Sử Giao Hàng',
    )
    delivery_count = fields.Integer(
        string='Số Chuyến',
        compute='_compute_delivery_count',
    )

    @api.depends('delivery_ids')
    def _compute_delivery_count(self):
        for rec in self:
            rec.delivery_count = len(rec.delivery_ids)

    _plate_unique = models.Constraint(
        'UNIQUE(plate_number)',
        'Biển số xe phải là duy nhất!',
    )
