from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GarmentPayment(models.Model):
    _name = 'garment.payment'
    _description = 'Phiếu Thanh Toán'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(
        string='Số Phiếu',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    invoice_id = fields.Many2one(
        'garment.invoice',
        string='Hóa Đơn',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Đối Tác',
        required=True,
    )
    payment_type = fields.Selection([
        ('inbound', 'Thu Tiền'),
        ('outbound', 'Chi Tiền'),
    ], string='Loại', required=True, default='inbound')

    payment_method = fields.Selection([
        ('cash', 'Tiền Mặt'),
        ('bank', 'Chuyển Khoản'),
        ('lc', 'L/C'),
        ('other', 'Khác'),
    ], string='Phương Thức', default='bank')

    date = fields.Date(
        string='Ngày Thanh Toán',
        required=True,
        default=fields.Date.today,
    )
    amount = fields.Float(
        string='Số Tiền',
        required=True,
        digits=(14, 0),
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        default=lambda self: self.env.company.currency_id,
    )
    reference = fields.Char(string='Số Tham Chiếu / UNC')
    notes = fields.Text(string='Ghi Chú')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_('Số tiền thanh toán phải lớn hơn 0.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.payment') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.residual < rec.amount:
                raise ValidationError(
                    _('Số tiền thanh toán (%s) vượt quá số còn nợ (%s) của hóa đơn %s.')
                    % (rec.amount, rec.invoice_id.residual, rec.invoice_id.name)
                )
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
