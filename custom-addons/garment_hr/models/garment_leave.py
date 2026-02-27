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
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
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
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.employee_id.id,
        })

    def action_refuse(self):
        self.write({'state': 'refused'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
