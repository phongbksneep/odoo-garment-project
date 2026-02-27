from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentInvoice(models.Model):
    _name = 'garment.invoice'
    _description = 'Hóa Đơn May Mặc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Số Hóa Đơn',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    invoice_type = fields.Selection([
        ('sale', 'Hóa Đơn Bán (Doanh Thu)'),
        ('purchase', 'Hóa Đơn Mua (Chi Phí)'),
    ], string='Loại HĐ', required=True, default='sale')

    partner_id = fields.Many2one(
        'res.partner',
        string='Đối Tác',
        required=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
        help='Liên kết đơn hàng may (nếu có)',
    )
    date = fields.Date(
        string='Ngày Hóa Đơn',
        required=True,
        default=fields.Date.today,
    )
    due_date = fields.Date(
        string='Hạn Thanh Toán',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        default=lambda self: self.env.company.currency_id,
    )

    line_ids = fields.One2many(
        'garment.invoice.line',
        'invoice_id',
        string='Chi Tiết Hóa Đơn',
    )

    # --- Tax ---
    tax_type = fields.Selection([
        ('0', '0% (Xuất Khẩu)'),
        ('5', '5%'),
        ('8', '8%'),
        ('10', '10%'),
        ('none', 'Không Thuế'),
    ], string='Thuế GTGT', default='10')

    subtotal = fields.Float(
        string='Tiền Hàng',
        compute='_compute_totals',
        store=True,
        digits=(14, 0),
    )
    tax_amount = fields.Float(
        string='Tiền Thuế GTGT',
        compute='_compute_totals',
        store=True,
        digits=(14, 0),
    )
    total_amount = fields.Float(
        string='Tổng Thanh Toán',
        compute='_compute_totals',
        store=True,
        digits=(14, 0),
    )
    paid_amount = fields.Float(
        string='Đã Thanh Toán',
        compute='_compute_paid',
        store=True,
        digits=(14, 0),
    )
    residual = fields.Float(
        string='Còn Nợ',
        compute='_compute_paid',
        store=True,
        digits=(14, 0),
    )

    payment_ids = fields.One2many(
        'garment.payment',
        'invoice_id',
        string='Thanh Toán',
    )

    # --- Classification ---
    expense_type = fields.Selection([
        ('material', 'Nguyên Phụ Liệu'),
        ('subcontract', 'Gia Công'),
        ('transport', 'Vận Chuyển'),
        ('salary', 'Lương'),
        ('utility', 'Điện / Nước'),
        ('rent', 'Thuê Nhà Xưởng'),
        ('equipment', 'Thiết Bị / Máy Móc'),
        ('other', 'Chi Phí Khác'),
    ], string='Phân Loại Chi Phí',
       help='Chỉ áp dụng cho hóa đơn mua',
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('paid', 'Đã Thanh Toán'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi Chú')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                inv_type = vals.get('invoice_type', 'sale')
                code = 'garment.invoice.sale' if inv_type == 'sale' else 'garment.invoice.purchase'
                vals['name'] = self.env['ir.sequence'].next_by_code(code) or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.subtotal', 'tax_type')
    def _compute_totals(self):
        for rec in self:
            rec.subtotal = sum(rec.line_ids.mapped('subtotal'))
            rate = int(rec.tax_type) / 100 if rec.tax_type and rec.tax_type != 'none' else 0
            rec.tax_amount = rec.subtotal * rate
            rec.total_amount = rec.subtotal + rec.tax_amount

    @api.depends('payment_ids.amount', 'total_amount')
    def _compute_paid(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_ids.filtered(
                lambda p: p.state == 'confirmed'
            ).mapped('amount'))
            rec.residual = rec.total_amount - rec.paid_amount

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Phải có ít nhất 1 dòng chi tiết!'))
        self.write({'state': 'confirmed'})

    def action_paid(self):
        self.write({'state': 'paid'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'paid':
                raise UserError(_('Không thể hủy hóa đơn đã thanh toán!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentInvoiceLine(models.Model):
    _name = 'garment.invoice.line'
    _description = 'Chi Tiết Hóa Đơn'
    _order = 'sequence, id'

    invoice_id = fields.Many2one(
        'garment.invoice',
        string='Hóa Đơn',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    description = fields.Char(
        string='Mô Tả',
        required=True,
    )
    quantity = fields.Float(
        string='Số Lượng',
        required=True,
        default=1,
    )
    unit = fields.Selection([
        ('pcs', 'Cái'),
        ('m', 'Mét'),
        ('kg', 'Kg'),
        ('yard', 'Yard'),
        ('set', 'Bộ'),
        ('lot', 'Lô'),
        ('month', 'Tháng'),
        ('other', 'Khác'),
    ], string='Đơn Vị', default='pcs')
    unit_price = fields.Float(
        string='Đơn Giá',
        required=True,
        digits=(12, 2),
    )
    subtotal = fields.Float(
        string='Thành Tiền',
        compute='_compute_subtotal',
        store=True,
        digits=(14, 0),
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
