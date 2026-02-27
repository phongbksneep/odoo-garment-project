from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentMaintenanceRequest(models.Model):
    _name = 'garment.maintenance.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    machine_id = fields.Many2one(
        'garment.machine',
        string='Máy',
        required=True,
    )
    request_type = fields.Selection([
        ('preventive', 'Bảo Trì Định Kỳ'),
        ('corrective', 'Sửa Chữa'),
        ('breakdown', 'Hư Hỏng Khẩn'),
    ], string='Loại', required=True, default='corrective')

    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình Thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn Cấp'),
    ], string='Ưu Tiên', default='1')

    request_date = fields.Datetime(
        string='Ngày Yêu Cầu',
        default=fields.Datetime.now,
    )
    scheduled_date = fields.Date(string='Ngày Dự Kiến')
    completion_date = fields.Datetime(string='Ngày Hoàn Thành')

    technician_id = fields.Many2one(
        'hr.employee',
        string='Kỹ Thuật Viên',
    )
    description = fields.Text(string='Mô Tả Sự Cố')
    action_taken = fields.Text(string='Xử Lý')

    # Spare parts
    spare_parts = fields.Text(
        string='Phụ Tùng Sử Dụng',
    )
    cost = fields.Float(
        string='Chi Phí',
        digits=(10, 2),
    )
    downtime_hours = fields.Float(
        string='Thời Gian Dừng (giờ)',
        digits=(10, 1),
    )

    state = fields.Selection([
        ('draft', 'Mới'),
        ('confirmed', 'Đã Tiếp Nhận'),
        ('in_progress', 'Đang Xử Lý'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.maintenance.request'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirmed'})
        if self.request_type == 'breakdown':
            self.machine_id.write({'status': 'broken'})
        else:
            self.machine_id.write({'status': 'maintenance'})

    def action_start(self):
        self.ensure_one()
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.ensure_one()
        self.write({
            'state': 'done',
            'completion_date': fields.Datetime.now(),
        })
        self.machine_id.write({
            'status': 'active',
            'last_maintenance_date': fields.Date.today(),
        })

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'done':
            raise UserError(_('Không thể hủy yêu cầu đã hoàn thành.'))
        self.write({'state': 'cancelled'})
        self.machine_id.write({'status': 'active'})
