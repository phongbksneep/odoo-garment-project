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
    partner_tax_code = fields.Char(
        string='Mã Số Thuế',
        help='MST đối tác (bắt buộc trên hóa đơn GTGT theo NĐ 123/2020)',
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
    payment_term = fields.Selection([
        ('immediate', 'Thanh Toán Ngay'),
        ('cod', 'COD - Giao Hàng Thu Tiền'),
        ('30days', '30 Ngày'),
        ('60days', '60 Ngày'),
        ('90days', '90 Ngày'),
        ('lc', 'L/C - Thư Tín Dụng'),
        ('tt', 'T/T - Điện Chuyển Tiền'),
        ('dp', 'D/P - Nhờ Thu'),
        ('other', 'Khác'),
    ], string='Điều Khoản TT',
       help='Điều khoản thanh toán phổ biến trong ngành may xuất khẩu',
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

    payment_status = fields.Selection([
        ('not_paid', 'Chưa Thanh Toán'),
        ('partial', 'Thanh Toán Một Phần'),
        ('paid', 'Đã Thanh Toán Đủ'),
    ], string='Tình Trạng TT',
       compute='_compute_paid',
       store=True,
    )
    is_overdue = fields.Boolean(
        string='Quá Hạn TT',
        compute='_compute_is_overdue',
        store=True,
    )
    overdue_days = fields.Integer(
        string='Số Ngày Quá Hạn',
        compute='_compute_is_overdue',
        store=True,
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

    @api.constrains('due_date', 'date')
    def _check_due_date(self):
        for rec in self:
            if rec.due_date and rec.date and rec.due_date < rec.date:
                raise ValidationError(_('Hạn thanh toán phải sau ngày hóa đơn.'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.vat:
            self.partner_tax_code = self.partner_id.vat

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

    @api.depends('payment_ids.amount', 'payment_ids.state', 'total_amount')
    def _compute_paid(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_ids.filtered(
                lambda p: p.state == 'confirmed'
            ).mapped('amount'))
            rec.residual = rec.total_amount - rec.paid_amount
            if rec.total_amount <= 0 or rec.paid_amount <= 0:
                rec.payment_status = 'not_paid'
            elif rec.paid_amount >= rec.total_amount:
                rec.payment_status = 'paid'
            else:
                rec.payment_status = 'partial'

    @api.depends('due_date', 'state', 'residual')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.due_date and rec.state == 'confirmed' and rec.residual > 0:
                delta = (today - rec.due_date).days
                rec.is_overdue = delta > 0
                rec.overdue_days = max(delta, 0)
            else:
                rec.is_overdue = False
                rec.overdue_days = 0

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

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Số lượng phải lớn hơn 0.'))

    @api.constrains('unit_price')
    def _check_unit_price(self):
        for line in self:
            if line.unit_price < 0:
                raise ValidationError(_('Đơn giá không được âm.'))

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
