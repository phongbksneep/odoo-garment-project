from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentWageCalculation(models.Model):
    _name = 'garment.wage.calculation'
    _description = 'Monthly Wage Calculation'
    _inherit = ['mail.thread', 'garment.audit.mixin']
    _order = 'month desc, employee_id'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Số phiếu lương phải là duy nhất!'),
    ]

    def _audit_tracked_fields(self):
        return ['state', 'base_salary', 'total_wage', 'net_pay',
                'bonus_amount', 'deduction']

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
    # Hai chế độ tính tăng ca:
    # 1. Theo luật (mặc định, ot_rate = 0): đơn giá giờ chuẩn × hệ số
    #    150% ngày thường / 200% ngày nghỉ tuần / 300% ngày lễ
    #    (Điều 98 Bộ luật Lao động 2019).
    # 2. Đơn giá thỏa thuận (ot_rate > 0): tiền OT = ot_rate × tổng giờ,
    #    giữ tương thích với cách trả khoán phổ biến ở xưởng may.
    total_ot_hours = fields.Float(
        string='Tổng Giờ Tăng Ca',
        compute='_compute_piece_totals',
        store=True,
        digits=(10, 1),
    )
    hourly_rate = fields.Float(
        string='Đơn Giá Giờ Chuẩn (VNĐ/h)',
        compute='_compute_hourly_rate',
        store=True,
        readonly=False,
        digits=(10, 0),
        help='Mặc định = lương cơ bản / ngày công / 8 giờ. '
             'Dùng để tính tăng ca theo hệ số luật định.',
    )
    ot_hours_weekend = fields.Float(
        string='Giờ TC Ngày Nghỉ Tuần (200%)',
        digits=(10, 1),
    )
    ot_hours_holiday = fields.Float(
        string='Giờ TC Ngày Lễ (300%)',
        digits=(10, 1),
    )
    ot_hours_weekday = fields.Float(
        string='Giờ TC Ngày Thường (150%)',
        compute='_compute_ot_hours_weekday',
        store=True,
        digits=(10, 1),
    )
    ot_rate = fields.Float(
        string='Đơn Giá OT Thỏa Thuận (VNĐ/h)',
        digits=(10, 0),
        help='Nếu > 0: tiền tăng ca = đơn giá này × tổng giờ (chế độ khoán). '
             'Nếu = 0: tính theo hệ số 150/200/300% trên đơn giá giờ chuẩn.',
    )
    ot_amount = fields.Float(
        string='Tiền Tăng Ca',
        compute='_compute_ot_amount',
        store=True,
        digits=(10, 0),
    )
    ot_exempt_amount = fields.Float(
        string='TC Miễn Thuế (Phần Phụ Trội)',
        compute='_compute_ot_amount',
        store=True,
        digits=(10, 0),
        help='Phần trả cao hơn đơn giá giờ làm việc bình thường được miễn '
             'thuế TNCN (Điều 4 Luật thuế TNCN).',
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
        compute='_compute_insurance_base',
        store=True,
        readonly=False,
        digits=(10, 0),
        help='Mức lương đóng BHXH (mặc định = lương cơ bản). '
             'BHXH/BHYT áp trần 20 lần lương cơ sở; BHTN áp trần '
             '20 lần lương tối thiểu vùng.',
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
    # Phần người sử dụng lao động đóng (không trừ vào lương,
    # dùng cho báo cáo chi phí nhân công)
    bhxh_employer = fields.Float(
        string='BHXH DN Đóng (17.5%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    bhyt_employer = fields.Float(
        string='BHYT DN Đóng (3%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    bhtn_employer = fields.Float(
        string='BHTN DN Đóng (1%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    union_fee_employer = fields.Float(
        string='Kinh Phí Công Đoàn (2%)',
        compute='_compute_insurance',
        store=True,
        digits=(10, 0),
    )
    total_employer_cost = fields.Float(
        string='Tổng Chi Phí Doanh Nghiệp',
        compute='_compute_total_wage',
        store=True,
        digits=(10, 0),
        help='Tổng thu nhập người lao động + các khoản DN đóng '
             '(BHXH/BHYT/BHTN + kinh phí công đoàn).',
    )

    # --- Tax ---
    personal_deduction = fields.Float(
        string='Giảm Trừ Bản Thân',
        digits=(10, 0),
        default=lambda self: self._param_float(
            'garment_payroll.personal_deduction', 15500000),
        help='15,5 triệu VNĐ/tháng từ kỳ tính thuế 2026 '
             '(Nghị quyết UBTVQH 10/2025). Cấu hình qua tham số hệ thống '
             'garment_payroll.personal_deduction.',
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
        help='6,2 triệu VNĐ/người/tháng từ kỳ tính thuế 2026.',
    )
    tax_exempt_allowance = fields.Float(
        string='Phụ Cấp Miễn Thuế',
        compute='_compute_tax',
        store=True,
        digits=(10, 0),
        help='Ăn trưa (tối đa mức trần, mặc định 730.000đ/tháng) '
             'và khoán điện thoại được miễn thuế TNCN.',
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
    paid_leave_days = fields.Float(
        string='Ngày Nghỉ Hưởng Lương',
        digits=(5, 1),
        help='Phép năm, kết hôn, tang lễ đã duyệt trong tháng — '
             'tự động lấy khi Tính Lương, được cộng vào ngày hưởng lương.',
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
    # Helpers
    # -------------------------------------------------------------------------
    @api.model
    def _param_float(self, key, default):
        """Đọc tham số hệ thống dạng số, có giá trị mặc định."""
        raw = self.env['ir.config_parameter'].sudo().get_param(key)
        try:
            return float(raw) if raw else default
        except (TypeError, ValueError):
            return default

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

    @api.constrains('base_salary', 'ot_rate', 'deduction', 'bonus_amount',
                    'actual_days', 'working_days')
    def _check_non_negative(self):
        for record in self:
            for field_name, label in [
                ('base_salary', 'Lương cơ bản'),
                ('ot_rate', 'Đơn giá tăng ca'),
                ('deduction', 'Khấu trừ'),
                ('bonus_amount', 'Thưởng'),
                ('actual_days', 'Ngày thực tế'),
                ('working_days', 'Ngày công'),
            ]:
                if record[field_name] < 0:
                    raise ValidationError(
                        _('%s không được âm.', label))

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('base_salary', 'working_days', 'actual_days',
                 'paid_leave_days')
    def _compute_base_amount(self):
        for record in self:
            if record.working_days > 0:
                paid_days = record.actual_days + record.paid_leave_days
                record.base_amount = (
                    record.base_salary / record.working_days * paid_days
                )
            else:
                record.base_amount = 0

    @api.depends('base_salary', 'working_days')
    def _compute_hourly_rate(self):
        for record in self:
            if record.working_days > 0:
                record.hourly_rate = record.base_salary / record.working_days / 8
            else:
                record.hourly_rate = 0

    @api.depends('total_ot_hours', 'ot_hours_weekend', 'ot_hours_holiday')
    def _compute_ot_hours_weekday(self):
        for record in self:
            record.ot_hours_weekday = max(
                record.total_ot_hours
                - record.ot_hours_weekend
                - record.ot_hours_holiday, 0)

    @api.depends('base_salary')
    def _compute_insurance_base(self):
        # Editable computed: mặc định theo lương cơ bản, cho phép sửa tay
        for record in self:
            record.insurance_base = record.insurance_base or record.base_salary

    def _period_start(self):
        self.ensure_one()
        return fields.Date.to_date(f'{self.year}-{self.month}-01')

    def _period_end(self):
        self.ensure_one()
        if int(self.month) == 12:
            return fields.Date.to_date(f'{self.year + 1}-01-01')
        next_month = str(int(self.month) + 1).zfill(2)
        return fields.Date.to_date(f'{self.year}-{next_month}-01')

    @api.depends('employee_id', 'month', 'year')
    def _compute_piece_totals(self):
        valid = self.filtered(
            lambda r: r.employee_id and r.month and r.year)
        for record in self - valid:
            record.total_pieces = 0
            record.piece_rate_amount = 0
            record.total_ot_hours = 0
        if not valid:
            return
        # Một truy vấn gộp cho cả batch thay vì search theo từng nhân viên
        date_from = min(rec._period_start() for rec in valid)
        date_to = max(rec._period_end() for rec in valid)
        groups = self.env['garment.worker.output']._read_group(
            domain=[
                ('employee_id', 'in', valid.employee_id.ids),
                ('date', '>=', date_from),
                ('date', '<', date_to),
            ],
            groupby=['employee_id', 'date:month'],
            aggregates=['quantity:sum', 'amount:sum', 'overtime_hours:sum'],
        )
        data = {}
        for employee, month_start, qty, amount, ot in groups:
            data[(employee.id, month_start.year, month_start.month)] = (
                qty or 0, amount or 0, ot or 0)
        for record in valid:
            key = (record.employee_id.id, record.year, int(record.month))
            qty, amount, ot = data.get(key, (0, 0, 0))
            record.total_pieces = qty
            record.piece_rate_amount = amount
            record.total_ot_hours = ot

    @api.depends('total_ot_hours', 'ot_rate', 'hourly_rate',
                 'ot_hours_weekday', 'ot_hours_weekend', 'ot_hours_holiday')
    def _compute_ot_amount(self):
        for record in self:
            hourly = record.hourly_rate
            if record.ot_rate:
                # Chế độ đơn giá thỏa thuận (khoán)
                record.ot_amount = record.total_ot_hours * record.ot_rate
                # Phần vượt trên đơn giá giờ chuẩn được miễn thuế
                record.ot_exempt_amount = max(
                    record.ot_amount - hourly * record.total_ot_hours, 0)
            else:
                # Chế độ luật định: 150% / 200% / 300% (Điều 98 BLLĐ 2019)
                record.ot_amount = hourly * (
                    1.5 * record.ot_hours_weekday
                    + 2.0 * record.ot_hours_weekend
                    + 3.0 * record.ot_hours_holiday
                )
                # Phần phụ trội so với đơn giá giờ chuẩn miễn thuế TNCN
                record.ot_exempt_amount = hourly * (
                    0.5 * record.ot_hours_weekday
                    + 1.0 * record.ot_hours_weekend
                    + 2.0 * record.ot_hours_holiday
                )

    @api.depends(
        'base_amount', 'piece_rate_amount', 'ot_amount',
        'total_allowance', 'bonus_amount',
        'total_insurance', 'pit_amount', 'deduction',
        'bhxh_employer', 'bhyt_employer', 'bhtn_employer',
        'union_fee_employer',
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
            record.net_pay = (gross - record.total_insurance
                              - record.pit_amount - record.deduction)
            record.total_employer_cost = (
                gross
                + record.bhxh_employer
                + record.bhyt_employer
                + record.bhtn_employer
                + record.union_fee_employer
            )

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
        # Trần đóng: BHXH/BHYT = 20 lần lương cơ sở;
        # BHTN = 20 lần lương tối thiểu vùng.
        luong_co_so = self._param_float(
            'garment_payroll.luong_co_so', 2340000)
        luong_toi_thieu_vung = self._param_float(
            'garment_payroll.luong_toi_thieu_vung', 4960000)
        cap_bhxh = 20 * luong_co_so
        cap_bhtn = 20 * luong_toi_thieu_vung
        for record in self:
            base_bhxh = min(record.insurance_base, cap_bhxh)
            base_bhtn = min(record.insurance_base, cap_bhtn)
            # Người lao động đóng: 8% + 1.5% + 1%
            record.bhxh_employee = base_bhxh * 0.08
            record.bhyt_employee = base_bhxh * 0.015
            record.bhtn_employee = base_bhtn * 0.01
            record.total_insurance = (
                record.bhxh_employee
                + record.bhyt_employee
                + record.bhtn_employee
            )
            # Doanh nghiệp đóng: 17.5% + 3% + 1% + 2% công đoàn
            record.bhxh_employer = base_bhxh * 0.175
            record.bhyt_employer = base_bhxh * 0.03
            record.bhtn_employer = base_bhtn * 0.01
            record.union_fee_employer = base_bhxh * 0.02

    @api.depends(
        'total_wage', 'total_insurance',
        'personal_deduction', 'dependent_count',
        'allowance_lunch', 'allowance_phone', 'ot_exempt_amount',
    )
    def _compute_tax(self):
        per_dependent = self._param_float(
            'garment_payroll.dependent_deduction', 6200000)
        lunch_cap = self._param_float(
            'garment_payroll.lunch_allowance_cap', 730000)
        for record in self:
            record.dependent_deduction = (
                record.dependent_count * per_dependent)
            # Miễn thuế: ăn trưa tới mức trần + khoán điện thoại
            # + phần phụ trội tăng ca
            record.tax_exempt_allowance = (
                min(record.allowance_lunch, lunch_cap)
                + record.allowance_phone
            )
            taxable = (
                record.total_wage
                - record.total_insurance
                - record.tax_exempt_allowance
                - record.ot_exempt_amount
                - record.personal_deduction
                - record.dependent_deduction
            )
            record.taxable_income = max(taxable, 0)
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
    # Loại nghỉ doanh nghiệp trả lương (ốm/thai sản do BHXH chi trả,
    # việc riêng/không lương không hưởng)
    _PAID_LEAVE_TYPES = ('annual', 'marriage', 'funeral')

    def _get_paid_leave_days(self):
        """Số ngày nghỉ hưởng lương đã duyệt nằm trong tháng tính lương."""
        self.ensure_one()
        date_from = self._period_start()
        date_to = self._period_end()
        leaves = self.env['garment.leave'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'approved'),
            ('leave_type', 'in', self._PAID_LEAVE_TYPES),
            ('date_from', '<', date_to),
            ('date_to', '>=', date_from),
        ])
        total = 0.0
        one_day = timedelta(days=1)
        for leave in leaves:
            start = max(leave.date_from, date_from)
            end = min(leave.date_to, date_to - one_day)
            overlap_days = (end - start).days + 1
            if overlap_days > 0:
                total += overlap_days
        return total

    def action_calculate(self):
        """Trigger recalculation — also pull attendance data."""
        self.ensure_one()
        if self.state not in ('draft', 'calculated'):
            raise UserError(_(
                'Chỉ phiếu lương Nháp hoặc Đã Tính mới được tính lại.'))
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
        self.paid_leave_days = self._get_paid_leave_days()
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
        if self.state != 'calculated':
            raise UserError(_('Phải tính lương trước khi xác nhận.'))
        self.write({'state': 'confirmed'})

    def action_pay(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Phải xác nhận trước khi trả lương.'))
        self.write({'state': 'paid'})

    def action_reset_draft(self):
        self.ensure_one()
        if self.state == 'paid':
            raise UserError(_(
                'Không thể đưa phiếu lương đã trả về Nháp.'))
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state == 'paid':
                raise UserError(_(
                    'Không thể xóa phiếu lương %s đã trả.', rec.name))
        return super().unlink()
