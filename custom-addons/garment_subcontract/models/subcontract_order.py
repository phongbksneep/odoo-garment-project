from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class SubcontractOrder(models.Model):
    _name = 'garment.subcontract.order'
    _description = 'Đơn Hàng Gia Công'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Số Đơn Gia Công',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    direction = fields.Selection([
        ('outgoing', 'Gửi Gia Công (Outsource)'),
        ('incoming', 'Nhận Gia Công (Insource)'),
    ], string='Loại', required=True, default='outgoing', tracking=True)

    work_type = fields.Selection([
        ('cmt', 'CMT (Cắt - May - Hoàn Thiện)'),
        ('sewing', 'May (Sewing Only)'),
        ('cutting', 'Cắt (Cutting Only)'),
        ('washing', 'Giặt (Washing)'),
        ('embroidery', 'Thêu (Embroidery)'),
        ('printing', 'In (Printing)'),
        ('finishing', 'Hoàn Thiện (Finishing)'),
        ('packing', 'Đóng Gói (Packing)'),
        ('other', 'Khác'),
    ], string='Loại Công Việc', required=True, tracking=True)

    # Partner
    partner_id = fields.Many2one(
        'res.partner',
        string='Đối Tác Gia Công',
        required=True,
        tracking=True,
    )
    partner_po = fields.Char(
        string='PO Đối Tác',
    )

    # Internal references
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May Gốc',
        tracking=True,
        help='Đơn hàng may nội bộ liên quan',
    )
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
    )

    # Lines
    line_ids = fields.One2many(
        'garment.subcontract.order.line',
        'order_id',
        string='Chi Tiết Gia Công',
    )

    # Quantities
    total_qty = fields.Integer(
        string='Tổng SL Gia Công',
        compute='_compute_totals',
        store=True,
    )
    total_received = fields.Integer(
        string='Tổng SL Đã Nhận Lại',
        compute='_compute_totals',
        store=True,
    )
    total_rejected = fields.Integer(
        string='Tổng SL Lỗi/Từ Chối',
        compute='_compute_totals',
        store=True,
    )
    completion_rate = fields.Float(
        string='Tiến Độ (%)',
        compute='_compute_totals',
        store=True,
    )

    # Materials sent/received
    material_sent = fields.Text(
        string='Nguyên Liệu Gửi Đi',
        help='Chi tiết vải, phụ liệu gửi cho đối tác gia công',
    )
    material_returned = fields.Text(
        string='Nguyên Liệu Trả Lại',
        help='Nguyên liệu dư trả lại sau gia công',
    )

    # Dates
    date_order = fields.Date(
        string='Ngày Đặt',
        default=fields.Date.today,
        tracking=True,
    )
    date_sent = fields.Date(
        string='Ngày Giao Hàng/NL',
        help='Ngày gửi hàng hoặc nguyên liệu cho đối tác',
    )
    date_expected = fields.Date(
        string='Ngày Nhận Dự Kiến',
        tracking=True,
    )
    date_received = fields.Date(
        string='Ngày Nhận Thực Tế',
    )

    # Costing
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        default=lambda self: self.env.company.currency_id,
    )
    unit_price = fields.Float(
        string='Đơn Giá GC (VNĐ/pcs)',
        digits=(12, 2),
        tracking=True,
    )
    total_cost = fields.Float(
        string='Tổng Chi Phí GC',
        compute='_compute_total_cost',
        store=True,
        digits=(16, 2),
    )
    payment_status = fields.Selection([
        ('unpaid', 'Chưa Thanh Toán'),
        ('partial', 'Thanh Toán Một Phần'),
        ('paid', 'Đã Thanh Toán'),
    ], string='Thanh Toán', default='unpaid', tracking=True)
    amount_paid = fields.Float(
        string='Đã Thanh Toán',
        digits=(16, 2),
    )

    # Quality
    qc_required = fields.Boolean(
        string='Yêu Cầu Kiểm Hàng',
        default=True,
    )
    qc_passed = fields.Boolean(
        string='QC Đạt',
    )
    qc_notes = fields.Text(
        string='Ghi Chú Kiểm Hàng',
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('sent', 'Đã Gửi Hàng'),
        ('in_progress', 'Đang Gia Công'),
        ('partial_received', 'Nhận Một Phần'),
        ('received', 'Đã Nhận Hàng'),
        ('qc', 'Kiểm Tra'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Html(string='Ghi Chú')

    # Computed
    is_overdue = fields.Boolean(
        string='Trễ Hạn',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                seq_code = 'garment.subcontract.order'
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or 'New'
        return super().create(vals_list)

    @api.depends('line_ids.qty_ordered', 'line_ids.qty_received', 'line_ids.qty_rejected')
    def _compute_totals(self):
        for order in self:
            lines = order.line_ids
            order.total_qty = sum(lines.mapped('qty_ordered'))
            order.total_received = sum(lines.mapped('qty_received'))
            order.total_rejected = sum(lines.mapped('qty_rejected'))
            if order.total_qty:
                order.completion_rate = (order.total_received / order.total_qty) * 100
            else:
                order.completion_rate = 0.0

    @api.depends('total_qty', 'unit_price')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = order.total_qty * order.unit_price

    def _compute_is_overdue(self):
        today = fields.Date.today()
        for order in self:
            if order.date_expected and order.state not in ('done', 'cancelled'):
                order.is_overdue = today > order.date_expected
            else:
                order.is_overdue = False

    def _search_is_overdue(self, operator, value):
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                ('date_expected', '<', today),
                ('state', 'not in', ['done', 'cancelled']),
            ]
        return [
            '|',
            ('date_expected', '>=', today),
            ('date_expected', '=', False),
        ]

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError('Phải có ít nhất một dòng chi tiết gia công!')
        self.write({'state': 'confirmed'})

    def action_send(self):
        self.write({
            'state': 'sent',
            'date_sent': fields.Date.today(),
        })

    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_partial_received(self):
        self.write({'state': 'partial_received'})

    def action_received(self):
        self.write({
            'state': 'received',
            'date_received': fields.Date.today(),
        })

    def action_qc(self):
        self.write({'state': 'qc'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        for order in self:
            if order.state == 'done':
                raise UserError('Không thể hủy đơn đã hoàn thành!')
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class SubcontractOrderLine(models.Model):
    _name = 'garment.subcontract.order.line'
    _description = 'Chi Tiết Đơn Gia Công'
    _order = 'order_id, id'

    order_id = fields.Many2one(
        'garment.subcontract.order',
        string='Đơn Gia Công',
        required=True,
        ondelete='cascade',
    )
    description = fields.Char(
        string='Mô Tả Công Việc',
        required=True,
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Màu',
    )
    size_id = fields.Many2one(
        'garment.size',
        string='Size',
    )
    qty_ordered = fields.Integer(
        string='SL Đặt GC',
        required=True,
    )
    qty_received = fields.Integer(
        string='SL Nhận Lại',
    )
    qty_rejected = fields.Integer(
        string='SL Lỗi/Từ Chối',
    )
    qty_accepted = fields.Integer(
        string='SL Đạt',
        compute='_compute_qty_accepted',
        store=True,
    )
    unit_price = fields.Float(
        string='Đơn Giá',
        digits=(12, 2),
    )
    subtotal = fields.Float(
        string='Thành Tiền',
        compute='_compute_subtotal',
        store=True,
        digits=(16, 2),
    )
    notes = fields.Char(string='Ghi Chú')

    @api.depends('qty_received', 'qty_rejected')
    def _compute_qty_accepted(self):
        for line in self:
            line.qty_accepted = line.qty_received - line.qty_rejected

    @api.depends('qty_ordered', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty_ordered * line.unit_price

    @api.constrains('qty_received', 'qty_ordered')
    def _check_qty(self):
        for line in self:
            if line.qty_received > line.qty_ordered:
                raise ValidationError(
                    'Số lượng nhận lại không được lớn hơn số lượng đặt gia công!'
                )
