from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class WashOrder(models.Model):
    _name = 'garment.wash.order'
    _description = 'Lệnh Giặt (Wash Order)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Số Lệnh Giặt',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    order_type = fields.Selection([
        ('internal', 'Giặt Nội Bộ (Internal)'),
        ('external_in', 'Nhận Giặt Gia Công (External In)'),
    ], string='Loại Lệnh', required=True, default='internal', tracking=True)

    # Internal wash - linked to production
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
        tracking=True,
        help='Lệnh sản xuất nội bộ liên quan (nếu giặt nội bộ)',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
        related='production_order_id.garment_order_id',
        store=True,
        readonly=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
        tracking=True,
    )

    # External wash - client info
    client_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng / Công Ty Gửi Giặt',
        tracking=True,
        help='Công ty gửi hàng đến để giặt gia công',
    )
    client_po = fields.Char(
        string='PO Khách Gửi Giặt',
    )

    # Recipe & process
    recipe_id = fields.Many2one(
        'garment.wash.recipe',
        string='Công Thức Giặt',
        tracking=True,
    )
    wash_type = fields.Selection(
        related='recipe_id.wash_type',
        string='Loại Giặt',
        store=True,
    )

    # Quantities
    qty_received = fields.Integer(
        string='SL Nhận Giặt (pcs)',
        required=True,
        tracking=True,
    )
    weight_kg = fields.Float(
        string='Trọng Lượng (kg)',
        digits=(12, 2),
    )
    qty_washed = fields.Integer(
        string='SL Giặt Xong',
        tracking=True,
    )
    qty_rewash = fields.Integer(
        string='SL Giặt Lại (Re-wash)',
    )
    qty_reject = fields.Integer(
        string='SL Loại Bỏ',
    )

    # Machine & resource
    machine_name = fields.Char(
        string='Máy Giặt',
    )
    machine_capacity_kg = fields.Float(
        string='Công Suất Máy (kg)',
        digits=(8, 1),
    )

    # Water & energy tracking
    water_consumed = fields.Float(
        string='Nước Tiêu Thụ (lít)',
        digits=(12, 1),
    )
    energy_consumed = fields.Float(
        string='Điện Tiêu Thụ (kWh)',
        digits=(12, 2),
    )
    steam_consumed = fields.Float(
        string='Hơi Nước (kg steam)',
        digits=(12, 1),
    )

    # Dates
    date_received = fields.Date(
        string='Ngày Nhận Hàng',
        default=fields.Date.today,
        tracking=True,
    )
    date_start = fields.Datetime(
        string='Bắt Đầu Giặt',
    )
    date_end = fields.Datetime(
        string='Kết Thúc Giặt',
    )
    date_delivered = fields.Date(
        string='Ngày Giao Lại',
    )
    planned_delivery_date = fields.Date(
        string='Ngày Giao Dự Kiến',
    )

    # Costing
    unit_price = fields.Float(
        string='Đơn Giá Giặt (VNĐ/pcs)',
        digits=(12, 2),
    )
    total_cost = fields.Float(
        string='Tổng Chi Phí',
        compute='_compute_total_cost',
        store=True,
        digits=(16, 2),
    )
    chemical_cost = fields.Float(
        string='Chi Phí Hóa Chất',
        digits=(12, 2),
    )

    # Quality
    color_before = fields.Char(string='Màu Trước Giặt')
    color_after = fields.Char(string='Màu Sau Giặt')
    hand_feel = fields.Selection([
        ('soft', 'Mềm'),
        ('medium', 'Trung Bình'),
        ('stiff', 'Cứng'),
    ], string='Cảm Giác Tay (Hand Feel)')
    shrinkage_length = fields.Float(
        string='Co Dọc (%)',
        digits=(5, 2),
    )
    shrinkage_width = fields.Float(
        string='Co Ngang (%)',
        digits=(5, 2),
    )
    qc_passed = fields.Boolean(
        string='QC Đạt',
    )
    qc_notes = fields.Text(
        string='Ghi Chú QC',
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('washing', 'Đang Giặt'),
        ('qc', 'Kiểm Tra'),
        ('done', 'Hoàn Thành'),
        ('delivered', 'Đã Giao Lại'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Html(string='Ghi Chú')

    # Computed
    wash_pass_rate = fields.Float(
        string='Tỷ Lệ Đạt (%)',
        compute='_compute_wash_pass_rate',
    )
    rewash_rate = fields.Float(
        string='Tỷ Lệ Giặt Lại (%)',
        compute='_compute_rewash_rate',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('garment.wash.order') or 'New'
        return super().create(vals_list)

    @api.depends('qty_received', 'unit_price')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = order.qty_received * order.unit_price

    def _compute_wash_pass_rate(self):
        for order in self:
            if order.qty_received:
                order.wash_pass_rate = (order.qty_washed / order.qty_received) * 100
            else:
                order.wash_pass_rate = 0.0

    def _compute_rewash_rate(self):
        for order in self:
            if order.qty_received:
                order.rewash_rate = (order.qty_rewash / order.qty_received) * 100
            else:
                order.rewash_rate = 0.0

    @api.constrains('qty_washed', 'qty_received')
    def _check_qty(self):
        for order in self:
            if order.qty_washed > order.qty_received:
                raise ValidationError('Số lượng giặt xong không thể lớn hơn số lượng nhận!')

    def action_confirm(self):
        for order in self:
            if order.order_type == 'external_in' and not order.client_id:
                raise UserError('Phải chọn khách hàng gửi giặt cho lệnh giặt gia công!')
            if not order.recipe_id:
                raise UserError('Phải chọn công thức giặt!')
        self.write({'state': 'confirmed'})

    def action_start_washing(self):
        self.write({
            'state': 'washing',
            'date_start': fields.Datetime.now(),
        })

    def action_qc(self):
        for order in self:
            if order.qty_washed <= 0:
                raise UserError('Phải nhập số lượng giặt xong trước khi kiểm tra!')
        self.write({
            'state': 'qc',
            'date_end': fields.Datetime.now(),
        })

    def action_done(self):
        self.write({'state': 'done'})

    def action_delivered(self):
        self.write({
            'state': 'delivered',
            'date_delivered': fields.Date.today(),
        })

    def action_cancel(self):
        for order in self:
            if order.state == 'delivered':
                raise UserError('Không thể hủy lệnh đã giao hàng!')
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
