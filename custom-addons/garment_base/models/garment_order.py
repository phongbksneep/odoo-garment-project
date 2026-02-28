from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GarmentOrder(models.Model):
    _name = 'garment.order'
    _description = 'Đơn Hàng May'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'garment.audit.mixin']
    _order = 'create_date desc'

    def _audit_tracked_fields(self):
        return ['customer_id', 'customer_po', 'style_id', 'delivery_date',
                'unit_price', 'state', 'total_qty']

    name = fields.Char(
        string='Số Đơn Hàng',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng',
        required=True,
        tracking=True,
        domain=[('customer_rank', '>', 0)],
    )
    customer_po = fields.Char(
        string='PO Khách Hàng',
        tracking=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
        required=True,
        tracking=True,
    )
    order_date = fields.Date(
        string='Ngày Đặt Hàng',
        default=fields.Date.today,
        tracking=True,
    )
    delivery_date = fields.Date(
        string='Ngày Giao Hàng',
        tracking=True,
    )
    line_ids = fields.One2many(
        'garment.order.line',
        'order_id',
        string='Chi Tiết Đơn Hàng',
    )
    total_qty = fields.Integer(
        string='Tổng Số Lượng',
        compute='_compute_total_qty',
        store=True,
    )
    total_amount = fields.Float(
        string='Tổng Tiền',
        compute='_compute_total_amount',
        store=True,
        digits='Product Price',
    )
    unit_price = fields.Float(
        string='Đơn Giá FOB',
        digits='Product Price',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        default=lambda self: self.env.company.currency_id,
    )
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('material', 'Chuẩn Bị Nguyên Liệu'),
        ('cutting', 'Đang Cắt'),
        ('sewing', 'Đang May'),
        ('finishing', 'Hoàn Thiện'),
        ('qc', 'Kiểm Tra Chất Lượng'),
        ('packing', 'Đóng Gói'),
        ('shipped', 'Đã Giao'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    payment_term = fields.Selection([
        ('tt', 'T/T (Chuyển Khoản)'),
        ('lc', 'L/C (Thư Tín Dụng)'),
        ('dp', 'D/P'),
        ('da', 'D/A'),
    ], string='Phương Thức Thanh Toán')

    incoterm = fields.Selection([
        ('fob', 'FOB'),
        ('cif', 'CIF'),
        ('exw', 'EXW'),
        ('cfr', 'CFR'),
    ], string='Điều Kiện Giao Hàng', default='fob')

    destination_port = fields.Char(
        string='Cảng Đến',
    )
    shipping_mark = fields.Text(
        string='Shipping Mark',
    )
    notes = fields.Html(
        string='Ghi Chú',
    )

    # --- Delivery Progress ---
    is_on_time = fields.Boolean(
        string='Đúng Hạn',
        compute='_compute_delivery_status',
    )
    is_late = fields.Boolean(
        string='Trễ Hạn',
        compute='_compute_delivery_status',
        search='_search_is_late',
    )
    days_remaining = fields.Integer(
        string='Số Ngày Còn Lại',
        compute='_compute_delivery_status',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('garment.order') or 'New'
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains('delivery_date', 'order_date')
    def _check_delivery_date(self):
        for order in self:
            if order.delivery_date and order.order_date and order.delivery_date < order.order_date:
                raise ValidationError(
                    _('Ngày giao hàng (%s) không được trước ngày đặt hàng (%s).',
                      order.delivery_date, order.order_date)
                )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('line_ids.quantity')
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(order.line_ids.mapped('quantity'))

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(order.line_ids.mapped('subtotal'))

    def _compute_delivery_status(self):
        today = fields.Date.today()
        for order in self:
            if order.delivery_date:
                delta = (order.delivery_date - today).days
                order.days_remaining = delta
                order.is_on_time = delta >= 0 or order.state == 'done'
                order.is_late = (
                    delta < 0
                    and order.state not in ('done', 'cancelled')
                )
            else:
                order.days_remaining = 0
                order.is_on_time = True
                order.is_late = False

    def _search_is_late(self, operator, value):
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                '&',
                ('delivery_date', '<', today),
                ('state', 'not in', ['done', 'cancelled']),
            ]
        return [
            '|',
            ('delivery_date', '>=', today),
            ('delivery_date', '=', False),
        ]

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise ValidationError(
                    _('Đơn hàng %s chưa có chi tiết size/màu. '
                      'Vui lòng thêm ít nhất 1 dòng trước khi xác nhận.',
                      order.name)
                )
            if order.total_qty <= 0:
                raise ValidationError(
                    _('Tổng số lượng đơn hàng %s phải lớn hơn 0.', order.name)
                )
        self.write({'state': 'confirmed'})

    def action_material(self):
        self.write({'state': 'material'})

    def action_cutting(self):
        self.write({'state': 'cutting'})

    def action_sewing(self):
        self.write({'state': 'sewing'})

    def action_finishing(self):
        self.write({'state': 'finishing'})

    def action_qc(self):
        self.write({'state': 'qc'})

    def action_packing(self):
        self.write({'state': 'packing'})

    def action_shipped(self):
        self.write({'state': 'shipped'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentOrderLine(models.Model):
    _name = 'garment.order.line'
    _description = 'Chi Tiết Đơn Hàng May'
    _order = 'order_id, color_id, size_id'

    order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng',
        required=True,
        ondelete='cascade',
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Màu',
        required=True,
    )
    size_id = fields.Many2one(
        'garment.size',
        string='Size',
        required=True,
    )
    quantity = fields.Integer(
        string='Số Lượng',
        required=True,
        default=0,
    )
    unit_price = fields.Float(
        string='Đơn Giá',
        related='order_id.unit_price',
        store=True,
        digits='Product Price',
    )
    subtotal = fields.Float(
        string='Thành Tiền',
        compute='_compute_subtotal',
        store=True,
        digits='Product Price',
    )

    _sql_constraints = [
        ('unique_order_color_size',
         'UNIQUE(order_id, color_id, size_id)',
         'Mỗi kết hợp Màu/Size chỉ được nhập 1 lần trong đơn hàng.'),
    ]

    @api.constrains('order_id', 'color_id', 'size_id')
    def _check_unique_color_size(self):
        for line in self:
            duplicate = self.search_count([
                ('order_id', '=', line.order_id.id),
                ('color_id', '=', line.color_id.id),
                ('size_id', '=', line.size_id.id),
                ('id', '!=', line.id),
            ])
            if duplicate:
                raise ValidationError(
                    _('Màu %s / Size %s đã tồn tại trong đơn hàng.',
                      line.color_id.name, line.size_id.name)
                )

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(
                    _('Số lượng không được âm (dòng %s / %s).',
                      line.color_id.name, line.size_id.name)
                )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
