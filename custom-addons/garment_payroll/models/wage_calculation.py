from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentWageCalculation(models.Model):
    _name = 'garment.wage.calculation'
    _description = 'Monthly Wage Calculation'
    _inherit = ['mail.thread']
    _order = 'month desc, employee_id'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Công Nhân',
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

    # --- Base Salary ---
    base_salary = fields.Float(
        string='Lương Cơ Bản (VNĐ)',
        digits=(10, 0),
    )
    working_days = fields.Integer(
        string='Ngày Công',
        default=26,
    )
    actual_days = fields.Integer(
        string='Ngày Thực Tế',
    )
    base_amount = fields.Float(
        string='Lương Ngày Công',
        compute='_compute_base_amount',
        store=True,
        digits=(10, 0),
    )

    # --- Piece Rate ---
    total_pieces = fields.Integer(
        string='Tổng SL Sản Phẩm',
        compute='_compute_piece_totals',
        store=True,
    )
    piece_rate_amount = fields.Float(
        string='Tiền Khoán (VNĐ)',
        compute='_compute_piece_totals',
        store=True,
        digits=(10, 0),
    )

    # --- Overtime ---
    total_ot_hours = fields.Float(
        string='Tổng Giờ Tăng Ca',
        compute='_compute_piece_totals',
        store=True,
        digits=(10, 1),
    )
    ot_rate = fields.Float(
        string='Đơn Giá OT (VNĐ/h)',
        digits=(10, 0),
    )
    ot_amount = fields.Float(
        string='Tiền Tăng Ca',
        compute='_compute_ot_amount',
        store=True,
        digits=(10, 0),
    )

    # --- Allowances & Deductions ---
    allowance_attendance = fields.Float(
        string='Phụ Cấp Chuyên Cần',
        digits=(10, 0),
        help='Thưởng đi làm đầy đủ trong tháng',
    )
    allowance_lunch = fields.Float(
        string='Phụ Cấp Ăn Trưa',
        digits=(10, 0),
    )
    allowance_transport = fields.Float(
        string='Phụ Cấp Xăng Xe',
        digits=(10, 0),
    )
    allowance_phone = fields.Float(
        string='Phụ Cấp Điện Thoại',
        digits=(10, 0),
    )
    allowance = fields.Float(
        string='Phụ Cấp Khác',
        digits=(10, 0),
    )
    total_allowance = fields.Float(
        string='Tổng Phụ Cấp',
        compute='_compute_total_allowance',
        store=True,
        digits=(10, 0),
    )

    # --- Social Insurance ---
    insurance_base = fields.Float(
        string='Mức Đóng BHXH',
        digits=(10, 0),
        help='Mức lương đóng BHXH (thường = lương cơ bản)',
    )
    bhxh_employee = fields.Float(
        string='BHXH (8%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    bhyt_employee = fields.Float(
        string='BHYT (1.5%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    bhtn_employee = fields.Float(
        string='BHTN (1%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    total_insurance = fields.Float(
        string='Tổng BHXH-BHYT-BHTN (10.5%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )

    # --- Tax ---
    personal_deduction = fields.Float(
        string='Giảm Trừ Bản Thân',
        digits=(10, 0),
        default=11000000,
        help='11 triệu VNĐ/tháng theo quy định',
    )
    dependent_count = fields.Integer(
        string='Số Người Phụ Thuộc',
        default=0,
    )
    dependent_deduction = fields.Float(
        string='Giảm Trừ Phụ Thuộc',
        compute='_compute_tax',
        store=True,
        digits=(10, 0),
    )
    taxable_income = fields.Float(
        string='Thu Nhập Chịu Thuế',
        compute='_compute_tax',
        store=True,
        digits=(10, 0),
    )
    pit_amount = fields.Float(
        string='Thuế TNCN',
        compute='_compute_tax',
        store=True,
        digits=(10, 0),
    )

    # --- Bonus ---
    bonus_amount = fields.Float(
        string='Tiền Thưởng Tháng',
        digits=(10, 0),
    )

    deduction = fields.Float(
        string='Khấu Trừ Khác',
        digits=(10, 0),
    )

    # --- Attendance link ---
    attendance_days = fields.Float(
        string='Ngày Công (Chấm Công)',
        digits=(5, 1),
        help='Lấy từ Tổng Hợp Công Tháng',
    )
    attendance_ot_hours = fields.Float(
        string='Giờ TC (Chấm Công)',
        digits=(5, 1),
    )

    # --- Net Pay ---
    total_wage = fields.Float(
        string='Tổng Thu Nhập',
        compute='_compute_total_wage',
        store=True,
        digits=(10, 0),
    )
    net_pay = fields.Float(
        string='Thực Lĩnh',
        compute='_compute_total_wage',
        store=True,
        digits=(10, 0),
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('calculated', 'Đã Tính'),
        ('confirmed', 'Đã Xác Nhận'),
        ('paid', 'Đã Trả'),
    ], string='Trạng Thái', default='draft', tracking=True)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.wage.calculation'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('base_salary', 'working_days', 'actual_days')
    def _compute_base_amount(self):
        for record in self:
            if record.working_days > 0:
                record.base_amount = (
                    record.base_salary / record.working_days * record.actual_days
                )
            else:
                record.base_amount = 0

    @api.depends('employee_id', 'month', 'year')
    def _compute_piece_totals(self):
        for record in self:
            if not record.employee_id or not record.month or not record.year:
                record.total_pieces = 0
                record.piece_rate_amount = 0
                record.total_ot_hours = 0
                continue
            # Compute date range for the month
            date_from = fields.Date.to_date(
                f'{record.year}-{record.month}-01'
            )
            if int(record.month) == 12:
                date_to = fields.Date.to_date(
                    f'{record.year + 1}-01-01'
                )
            else:
                next_month = str(int(record.month) + 1).zfill(2)
                date_to = fields.Date.to_date(
                    f'{record.year}-{next_month}-01'
                )
            outputs = self.env['garment.worker.output'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '>=', date_from),
                ('date', '<', date_to),
            ])
            record.total_pieces = sum(outputs.mapped('quantity'))
            record.piece_rate_amount = sum(outputs.mapped('amount'))
            record.total_ot_hours = sum(outputs.mapped('overtime_hours'))

    @api.depends('total_ot_hours', 'ot_rate')
    def _compute_ot_amount(self):
        for record in self:
            record.ot_amount = record.total_ot_hours * record.ot_rate

    @api.depends(
        'base_amount', 'piece_rate_amount', 'ot_amount',
        'total_allowance', 'bonus_amount',
        'total_insurance', 'pit_amount', 'deduction',
    )
    def _compute_total_wage(self):
        for record in self:
            gross = (
                record.base_amount
                + record.piece_rate_amount
                + record.ot_amount
                + record.total_allowance
                + record.bonus_amount
            )
            record.total_wage = gross
            record.net_pay = gross - record.total_insurance - record.pit_amount - record.deduction

    @api.depends(
        'allowance_attendance', 'allowance_lunch',
        'allowance_transport', 'allowance_phone', 'allowance',
    )
    def _compute_total_allowance(self):
        for record in self:
            record.total_allowance = (
                record.allowance_attendance
                + record.allowance_lunch
                + record.allowance_transport
                + record.allowance_phone
                + record.allowance
            )

    @api.depends('insurance_base')
    def _compute_insurance(self):
        for record in self:
            base = record.insurance_base
            record.bhxh_employee = base * 0.08
            record.bhyt_employee = base * 0.015
            record.bhtn_employee = base * 0.01
            record.total_insurance = base * 0.105

    @api.depends(
        'total_wage', 'total_insurance',
        'personal_deduction', 'dependent_count',
    )
    def _compute_tax(self):
        for record in self:
            record.dependent_deduction = record.dependent_count * 4400000
            taxable = (
                record.total_wage
                - record.total_insurance
                - record.personal_deduction
                - record.dependent_deduction
            )
            record.taxable_income = max(taxable, 0)
            # Simplified PIT: 5% for first 5M, 10% for 5-10M, etc.
            record.pit_amount = record._calc_pit(record.taxable_income)

    @staticmethod
    def _calc_pit(taxable):
        """Calculate Vietnam Personal Income Tax (progressive)."""
        if taxable <= 0:
            return 0
        brackets = [
            (5000000, 0.05),
            (5000000, 0.10),
            (8000000, 0.15),
            (14000000, 0.20),
            (20000000, 0.25),
            (28000000, 0.30),
            (float('inf'), 0.35),
        ]
        tax = 0
        remaining = taxable
        for bracket_size, rate in brackets:
            if remaining <= 0:
                break
            taxed = min(remaining, bracket_size)
            tax += taxed * rate
            remaining -= taxed
        return tax

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_calculate(self):
        """Trigger recalculation — also pull attendance data."""
        self.ensure_one()
        # Pull attendance summary if available
        summary = self.env['garment.attendance.summary'].search([
            ('employee_id', '=', self.employee_id.id),
            ('month', '=', self.month),
            ('year', '=', self.year),
        ], limit=1)
        if summary:
            self.attendance_days = summary.total_work_days
            self.attendance_ot_hours = summary.total_ot_hours
            if not self.actual_days:
                self.actual_days = int(summary.total_work_days)
        self._compute_piece_totals()
        self._compute_base_amount()
        self._compute_ot_amount()
        self._compute_total_allowance()
        self._compute_insurance()
        self._compute_total_wage()
        self._compute_tax()
        self.write({'state': 'calculated'})

    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirmed'})

    def action_pay(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Phải xác nhận trước khi trả lương.'))
        self.write({'state': 'paid'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})
