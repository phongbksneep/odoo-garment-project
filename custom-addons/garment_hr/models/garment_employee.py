from odoo import models, fields, api


class GarmentEmployee(models.Model):
    _inherit = 'hr.employee'

    # --- Garment-specific fields ---
    employee_code = fields.Char(
        string='Mã Nhân Viên',
        index=True,
        help='Mã nội bộ công ty may',
    )
    garment_role = fields.Selection([
        ('worker', 'Công Nhân'),
        ('team_leader', 'Tổ Trưởng'),
        ('line_leader', 'Chuyền Trưởng'),
        ('supervisor', 'Giám Sát'),
        ('dept_manager', 'Trưởng Phòng'),
        ('director', 'Giám Đốc'),
        ('admin', 'Hành Chính'),
        ('accountant', 'Kế Toán'),
        ('mechanic', 'Thợ Máy'),
        ('driver', 'Lái Xe'),
        ('qc', 'Nhân Viên QC'),
        ('other', 'Khác'),
    ], string='Chức Vụ May', default='worker')

    contract_type = fields.Selection([
        ('probation', 'Thử Việc'),
        ('definite', 'Có Thời Hạn'),
        ('indefinite', 'Không Thời Hạn'),
        ('seasonal', 'Thời Vụ'),
        ('parttime', 'Bán Thời Gian'),
    ], string='Loại Hợp Đồng', default='definite')

    join_date = fields.Date(string='Ngày Vào Làm')
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
        help='Chuyền may hiện tại (nếu là công nhân may)',
        ondelete='set null',
    )

    id_number = fields.Char(string='Số CCCD/CMND', groups='hr.group_hr_user')
    insurance_number = fields.Char(string='Số Sổ BHXH', groups='hr.group_hr_user')
    tax_code = fields.Char(string='Mã Số Thuế', groups='hr.group_hr_user')

    bank_name = fields.Char(string='Ngân Hàng', groups='hr.group_hr_user')
    bank_account = fields.Char(string='Số Tài Khoản', groups='hr.group_hr_user')

    emergency_contact = fields.Char(string='Liên Hệ Khẩn Cấp')
    emergency_phone = fields.Char(string='SĐT Khẩn Cấp')

    skill_ids = fields.One2many(
        'garment.employee.skill',
        'employee_id',
        string='Tay Nghề',
    )
    skill_count = fields.Integer(
        string='Số Kỹ Năng',
        compute='_compute_skill_count',
    )

    attendance_ids = fields.One2many(
        'garment.attendance',
        'employee_id',
        string='Chấm Công',
    )
    # --- Số dư phép năm (Điều 113-114 BLLĐ 2019) ---
    annual_leave_entitlement = fields.Float(
        string='Phép Năm Được Hưởng',
        compute='_compute_annual_leave',
        digits=(5, 1),
        help='12 ngày/năm điều kiện bình thường + 1 ngày cho mỗi 5 năm '
             'thâm niên; nhân viên vào giữa năm tính tỷ lệ theo tháng.',
    )
    annual_leave_used = fields.Float(
        string='Phép Năm Đã Dùng',
        compute='_compute_annual_leave',
        digits=(5, 1),
    )
    annual_leave_remaining = fields.Float(
        string='Phép Năm Còn Lại',
        compute='_compute_annual_leave',
        digits=(5, 1),
    )

    @api.depends('join_date', 'leave_ids.state', 'leave_ids.days',
                 'leave_ids.leave_type')
    def _compute_annual_leave(self):
        today = fields.Date.today()
        year_start = today.replace(month=1, day=1)
        # Một truy vấn gộp: tổng phép năm đã duyệt trong năm hiện tại
        used_map = {}
        for employee, days in self.env['garment.leave']._read_group(
                [('employee_id', 'in', self.ids),
                 ('leave_type', '=', 'annual'),
                 ('state', '=', 'approved'),
                 ('date_from', '>=', year_start)],
                ['employee_id'], ['days:sum']):
            used_map[employee.id] = days or 0
        for emp in self:
            base = 12.0
            if emp.join_date:
                years = (today - emp.join_date).days // 365
                base += years // 5  # +1 ngày mỗi 5 năm thâm niên
                if emp.join_date > year_start:
                    # Vào làm giữa năm: tính tỷ lệ theo số tháng còn lại
                    months = 12 - emp.join_date.month + 1
                    base = base * months / 12
            emp.annual_leave_entitlement = round(base, 1)
            emp.annual_leave_used = used_map.get(emp.id, 0)
            emp.annual_leave_remaining = (
                emp.annual_leave_entitlement - emp.annual_leave_used)

    leave_ids = fields.One2many(
        'garment.leave',
        'employee_id',
        string='Đơn Nghỉ Phép',
    )

    notes_garment = fields.Text(string='Ghi Chú')

    @api.depends('skill_ids')
    def _compute_skill_count(self):
        for emp in self:
            emp.skill_count = len(emp.skill_ids)
