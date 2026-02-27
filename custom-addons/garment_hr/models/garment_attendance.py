from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GarmentAttendance(models.Model):
    _name = 'garment.attendance'
    _description = 'Chấm Công Hàng Ngày'
    _order = 'date desc, employee_id'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        required=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    status = fields.Selection([
        ('present', 'Đi Làm'),
        ('absent', 'Vắng'),
        ('late', 'Đi Muộn'),
        ('early_leave', 'Về Sớm'),
        ('half_day', 'Nửa Ngày'),
        ('business_trip', 'Công Tác'),
        ('holiday', 'Nghỉ Lễ'),
    ], string='Trạng Thái', required=True, default='present')

    check_in = fields.Float(
        string='Giờ Vào',
        help='VD: 7.5 = 7:30',
    )
    check_out = fields.Float(
        string='Giờ Ra',
        help='VD: 17.0 = 17:00',
    )
    work_hours = fields.Float(
        string='Giờ Làm Việc',
        compute='_compute_work_hours',
        store=True,
    )
    overtime_hours = fields.Float(
        string='Giờ Tăng Ca',
        default=0,
    )
    shift = fields.Selection([
        ('day', 'Ca Ngày'),
        ('night', 'Ca Đêm'),
        ('overtime', 'Tăng Ca'),
    ], string='Ca', default='day')

    notes = fields.Char(string='Ghi Chú')

    _unique_employee_date = models.Constraint(
        'UNIQUE(employee_id, date)',
        'Mỗi nhân viên chỉ có 1 bản ghi chấm công/ngày!',
    )

    @api.depends('check_in', 'check_out', 'status')
    def _compute_work_hours(self):
        for rec in self:
            if rec.status in ('absent', 'holiday'):
                rec.work_hours = 0
            elif rec.status == 'half_day':
                rec.work_hours = 4
            elif rec.check_in and rec.check_out and rec.check_out > rec.check_in:
                raw = rec.check_out - rec.check_in
                # Subtract 1h lunch break if > 5 hours
                rec.work_hours = raw - 1 if raw > 5 else raw
            else:
                rec.work_hours = 8 if rec.status == 'present' else 0


class GarmentAttendanceSummary(models.Model):
    _name = 'garment.attendance.summary'
    _description = 'Tổng Hợp Công Tháng'
    _order = 'year desc, month desc, employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        required=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    month = fields.Selection([
        ('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
        ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
        ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng', required=True)
    year = fields.Integer(
        string='Năm',
        required=True,
        default=lambda self: fields.Date.today().year,
    )

    total_work_days = fields.Float(string='Tổng Ngày Công', digits=(5, 1))
    present_days = fields.Integer(string='Ngày Đi Làm')
    absent_days = fields.Integer(string='Ngày Vắng')
    late_days = fields.Integer(string='Số Lần Đi Muộn')
    half_days = fields.Integer(string='Ngày Nửa Ca')
    total_ot_hours = fields.Float(string='Tổng Giờ Tăng Ca', digits=(6, 1))
    total_work_hours = fields.Float(string='Tổng Giờ Làm', digits=(6, 1))

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
    ], string='Trạng Thái', default='draft')

    _unique_emp_period = models.Constraint(
        'UNIQUE(employee_id, month, year)',
        'Mỗi nhân viên chỉ có 1 bản tổng hợp/tháng!',
    )

    def action_calculate(self):
        """Tổng hợp chấm công từ dữ liệu hàng ngày."""
        for rec in self:
            date_from = fields.Date.to_date(f'{rec.year}-{rec.month}-01')
            if int(rec.month) == 12:
                date_to = fields.Date.to_date(f'{rec.year + 1}-01-01')
            else:
                next_m = str(int(rec.month) + 1).zfill(2)
                date_to = fields.Date.to_date(f'{rec.year}-{next_m}-01')

            attendances = self.env['garment.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('date', '>=', date_from),
                ('date', '<', date_to),
            ])
            rec.present_days = len(attendances.filtered(
                lambda a: a.status in ('present', 'late', 'early_leave', 'business_trip')))
            rec.absent_days = len(attendances.filtered(
                lambda a: a.status == 'absent'))
            rec.late_days = len(attendances.filtered(
                lambda a: a.status == 'late'))
            rec.half_days = len(attendances.filtered(
                lambda a: a.status == 'half_day'))
            rec.total_work_days = rec.present_days + rec.half_days * 0.5
            rec.total_ot_hours = sum(attendances.mapped('overtime_hours'))
            rec.total_work_hours = sum(attendances.mapped('work_hours'))
            rec.state = 'confirmed'
