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

    id_number = fields.Char(string='Số CCCD/CMND')
    insurance_number = fields.Char(string='Số Sổ BHXH')
    tax_code = fields.Char(string='Mã Số Thuế')

    bank_name = fields.Char(string='Ngân Hàng')
    bank_account = fields.Char(string='Số Tài Khoản')

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
