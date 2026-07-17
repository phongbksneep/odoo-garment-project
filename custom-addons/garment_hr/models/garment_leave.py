from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GarmentLeave(models.Model):
    _name = 'garment.leave'
    _description = 'Đơn Nghỉ Phép'
    _inherit = ['mail.thread']
    _order = 'date_from desc'

    name = fields.Char(
        string='Mã Đơn',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        required=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Phòng Ban',
        compute='_compute_department_snapshot',
        store=True,
        readonly=False,
        help='Chốt theo phòng ban của nhân viên tại thời điểm ghi nhận — '
             'chuyển phòng ban sau này không viết lại lịch sử.',
    )

    @api.depends('employee_id')
    def _compute_department_snapshot(self):
        for record in self:
            record.department_id = record.employee_id.department_id
    leave_type = fields.Selection([
        ('annual', 'Phép Năm'),
        ('sick', 'Nghỉ Ốm'),
        ('maternity', 'Thai Sản'),
        ('personal', 'Việc Riêng'),
        ('marriage', 'Kết Hôn'),
        ('funeral', 'Tang Lễ'),
        ('unpaid', 'Nghỉ Không Lương'),
        ('other', 'Khác'),
    ], string='Loại Nghỉ', required=True, default='annual')

    date_from = fields.Date(string='Từ Ngày', required=True)
    date_to = fields.Date(string='Đến Ngày', required=True)
    days = fields.Float(
        string='Số Ngày',
        compute='_compute_days',
        store=True,
    )
    reason = fields.Text(string='Lý Do')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã Gửi'),
        ('approved', 'Đã Duyệt'),
        ('refused', 'Từ Chối'),
    ], string='Trạng Thái', default='draft', tracking=True)

    approved_by = fields.Many2one(
        'hr.employee',
        string='Người Duyệt',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.leave') or _('New')
        return super().create(vals_list)

    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                delta = (rec.date_to - rec.date_from).days + 1
                rec.days = max(delta, 0)
            else:
                rec.days = 0

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(_('Ngày kết thúc phải >= ngày bắt đầu!'))

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(
                    _('Chỉ đơn nghỉ Nháp mới được gửi duyệt.'))
        self.write({'state': 'submitted'})

    def _check_wage_not_locked(self):
        """Chặn duyệt/từ chối phép khi lương tháng liên quan đã chốt —
        ngày nghỉ hưởng lương đã được tính vào phiếu lương."""
        if 'garment.wage.calculation' not in self.env:
            return  # garment_payroll chưa cài
        Wage = self.env['garment.wage.calculation']
        for rec in self:
            for d in {rec.date_from, rec.date_to}:
                if not d:
                    continue
                locked = Wage.search_count([
                    ('employee_id', '=', rec.employee_id.id),
                    ('month', '=', '%02d' % d.month),
                    ('year', '=', d.year),
                    ('state', 'in', ('confirmed', 'paid')),
                ])
                if locked:
                    raise ValidationError(_(
                        'Không thể thay đổi đơn nghỉ: phiếu lương tháng '
                        '%02d/%d của %s đã được xác nhận/trả.',
                        d.month, d.year, rec.employee_id.name))

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise ValidationError(
                    _('Chỉ đơn nghỉ Đã Gửi mới được duyệt.'))
            if rec.leave_type == 'annual':
                remaining = rec.employee_id.annual_leave_remaining
                if rec.days > remaining:
                    raise ValidationError(_(
                        'Nhân viên %s chỉ còn %.1f ngày phép năm, '
                        'không thể duyệt đơn nghỉ %.1f ngày.',
                        rec.employee_id.name, remaining, rec.days))
        self._check_wage_not_locked()
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.employee_id.id,
        })

    def action_refuse(self):
        for rec in self:
            if rec.state not in ('submitted', 'approved'):
                raise ValidationError(
                    _('Chỉ đơn nghỉ Đã Gửi hoặc Đã Duyệt mới được từ chối.'))
        # Từ chối đơn ĐÃ DUYỆT sau khi lương chốt → lương sai — chặn
        self.filtered(
            lambda r: r.state == 'approved')._check_wage_not_locked()
        self.write({'state': 'refused'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
