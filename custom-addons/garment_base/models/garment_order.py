from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentOrder(models.Model):
    _name = 'garment.order'
    _description = 'Đơn Hàng May'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'garment.audit.mixin']
    _order = 'create_date desc'

    _name_uniq = models.Constraint(
        'UNIQUE(name)', 'Số đơn hàng phải là duy nhất!')

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
        index=True,
        ondelete='restrict',
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
        index=True,
        ondelete='restrict',
        tracking=True,
    )
    order_date = fields.Date(
        string='Ngày Đặt Hàng',
        default=fields.Date.today,
        tracking=True,
    )
    delivery_date = fields.Date(
        string='Ngày Giao Hàng',
        index=True,
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
    ], string='Trạng Thái', default='draft', index=True, tracking=True)

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
    # Thứ tự pipeline; cancel/reset xử lý riêng. Cho phép đi tới (kể cả bỏ
    # qua giai đoạn — không phải đơn nào cũng qua đủ các bước), cấm đi lùi.
    _STATE_FLOW = ['draft', 'confirmed', 'material', 'cutting', 'sewing',
                   'finishing', 'qc', 'packing', 'shipped', 'done']

    def _check_forward(self, new_state):
        flow = self._STATE_FLOW
        for order in self:
            if order.state in ('done', 'cancelled'):
                raise UserError(_(
                    'Đơn hàng %s đã kết thúc, không thể chuyển trạng thái.',
                    order.name))
            if order.state == 'draft':
                raise UserError(_(
                    'Đơn hàng %s phải được xác nhận trước.', order.name))
            if flow.index(new_state) <= flow.index(order.state):
                raise UserError(_(
                    'Không thể chuyển đơn hàng %s lùi về trạng thái trước đó.',
                    order.name))
        self.write({'state': new_state})

    def action_confirm(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(
                    _('Chỉ đơn hàng Nháp mới được xác nhận.'))
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
        self._check_forward('material')

    def action_cutting(self):
        self._check_forward('cutting')

    def action_sewing(self):
        self._check_forward('sewing')

    def action_finishing(self):
        self._check_forward('finishing')

    def action_qc(self):
        self._check_forward('qc')

    def action_packing(self):
        self._check_forward('packing')

    def action_shipped(self):
        self._check_forward('shipped')

    def action_done(self):
        self._check_forward('done')

    # Trạng thái coi là "đã kết thúc" ở chứng từ con — không chặn hủy đơn
    _CHILD_TERMINAL_STATES = ('done', 'cancelled', 'delivered', 'shipped',
                              'paid')

    def _get_open_child_documents(self):
        """Liệt kê chứng từ con đang mở tham chiếu đơn hàng này.

        Quét mọi model thường có trường ``garment_order_id`` (Many2one tới
        garment.order) kèm trường ``state`` — module mới thêm sau sẽ tự
        được bảo vệ mà không cần đăng ký gì thêm.
        """
        self.ensure_one()
        blocking = []
        for model_name in self.env.registry:
            model = self.env[model_name]
            if model._transient or not model._auto or model._abstract:
                continue
            field = model._fields.get('garment_order_id')
            state = model._fields.get('state')
            if (not field or field.type != 'many2one'
                    or field.comodel_name != 'garment.order'
                    or field.related
                    or not state or state.type != 'selection'):
                continue
            count = model.sudo().search_count([
                ('garment_order_id', '=', self.id),
                ('state', 'not in', list(self._CHILD_TERMINAL_STATES)),
            ])
            if count:
                blocking.append('- %s: %d' % (model._description, count))
        return blocking

    def action_cancel(self):
        for order in self:
            if order.state in ('shipped', 'done'):
                raise UserError(_(
                    'Không thể hủy đơn hàng %s đã giao/hoàn thành.',
                    order.name))
            blocking = order._get_open_child_documents()
            if blocking:
                raise UserError(_(
                    'Không thể hủy đơn hàng %s khi còn chứng từ liên quan '
                    'đang mở. Hãy hủy/hoàn tất các chứng từ sau trước:\n%s',
                    order.name, '\n'.join(blocking)))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        for order in self:
            if order.state not in ('confirmed', 'cancelled'):
                raise UserError(_(
                    'Chỉ đơn hàng Đã Xác Nhận hoặc Đã Hủy mới được đưa về '
                    'Nháp.'))
        self.write({'state': 'draft'})

    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancelled'):
                raise UserError(_(
                    'Không thể xóa đơn hàng %s ở trạng thái hiện tại. '
                    'Hãy hủy đơn trước khi xóa.', order.name))
        return super().unlink()

    def write(self, vals):
        # Khóa dòng chi tiết và đơn giá sau khi rời trạng thái Nháp —
        # chứng từ con (sản xuất, cắt, phân bổ...) đã lấy số theo bản Nháp
        guarded = {'line_ids', 'unit_price'}
        if (guarded & set(vals)
                and not self.env.context.get('install_mode')
                and any(order.state != 'draft' for order in self)):
            raise UserError(_(
                'Chỉ đơn hàng Nháp mới được sửa chi tiết size/màu hoặc '
                'đơn giá. Hãy đưa đơn về Nháp trước khi sửa.'))
        return super().write(vals)


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

    _unique_order_color_size = models.Constraint(
        'UNIQUE(order_id, color_id, size_id)',
        'Mỗi kết hợp Màu/Size chỉ được nhập 1 lần trong đơn hàng.')

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

    def _check_order_editable(self):
        if self.env.context.get('install_mode'):
            return  # nạp dữ liệu demo/module
        for line in self:
            if line.order_id.state != 'draft':
                raise UserError(_(
                    'Không thể thêm/sửa/xóa dòng của đơn hàng %s đã xác '
                    'nhận. Hãy đưa đơn về Nháp trước.', line.order_id.name))

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_order_editable()
        return lines

    def write(self, vals):
        # Cho phép hệ thống cập nhật trường liên quan (unit_price related)
        if not set(vals) <= {'subtotal', 'unit_price'}:
            self._check_order_editable()
        return super().write(vals)

    def unlink(self):
        self._check_order_editable()
        return super().unlink()
