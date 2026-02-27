from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentDeliveryOrder(models.Model):
    _name = 'garment.delivery.order'
    _description = 'Phiếu Giao Hàng'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(
        string='Số Phiếu',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    delivery_type = fields.Selection([
        ('customer', 'Giao Cho Khách Hàng'),
        ('subcontract', 'Giao Cho Gia Công'),
        ('internal', 'Chuyển Nội Bộ'),
        ('return', 'Trả Hàng'),
    ], string='Loại Giao Hàng', required=True, default='customer')

    date = fields.Date(
        string='Ngày Giao',
        required=True,
        default=fields.Date.today,
    )
    expected_date = fields.Date(string='Ngày Dự Kiến Đến')

    partner_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng / Đối Tác',
        required=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
    )
    packing_list_id = fields.Many2one(
        'garment.packing.list',
        string='Packing List',
    )
    vehicle_id = fields.Many2one(
        'garment.vehicle',
        string='Phương Tiện',
    )
    driver_id = fields.Many2one(
        'hr.employee',
        string='Tài Xế',
    )

    # Shipping Info
    ship_from = fields.Char(string='Nơi Gửi', default='Nhà Máy')
    ship_to = fields.Text(string='Nơi Nhận', required=True)
    shipping_method = fields.Selection([
        ('road', 'Đường Bộ'),
        ('sea', 'Đường Biển'),
        ('air', 'Đường Hàng Không'),
        ('rail', 'Đường Sắt'),
        ('courier', 'Chuyển Phát Nhanh'),
    ], string='Phương Thức Vận Chuyển', default='road')

    # Cargo Details
    total_cartons = fields.Integer(string='Tổng Số Thùng')
    total_pcs = fields.Integer(string='Tổng Số Cái')
    gross_weight = fields.Float(string='Trọng Lượng Gross (Kg)')
    net_weight = fields.Float(string='Trọng Lượng Net (Kg)')
    volume_cbm = fields.Float(string='Thể Tích (CBM)')

    # For export
    container_no = fields.Char(string='Số Container')
    seal_no = fields.Char(string='Số Seal')
    bl_number = fields.Char(string='Số B/L')
    invoice_number = fields.Char(string='Số Invoice')

    line_ids = fields.One2many(
        'garment.delivery.line',
        'delivery_id',
        string='Chi Tiết Hàng Giao',
    )
    total_qty = fields.Integer(
        string='Tổng SL Giao',
        compute='_compute_total_qty',
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('loading', 'Đang Xếp Hàng'),
        ('in_transit', 'Đang Vận Chuyển'),
        ('delivered', 'Đã Giao'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi Chú')
    proof_of_delivery = fields.Binary(string='Ảnh Giao Hàng')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('garment.delivery.order')
                    or _('New')
                )
        return super().create(vals_list)

    @api.depends('line_ids.quantity')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.line_ids.mapped('quantity'))

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Phải có ít nhất 1 dòng chi tiết hàng giao!'))
        self.write({'state': 'confirmed'})

    def action_loading(self):
        self.write({'state': 'loading'})

    def action_in_transit(self):
        self.write({'state': 'in_transit'})

    def action_delivered(self):
        self.write({'state': 'delivered'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'delivered':
                raise UserError(_('Không thể hủy phiếu đã giao hàng!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentDeliveryLine(models.Model):
    _name = 'garment.delivery.line'
    _description = 'Chi Tiết Hàng Giao'
    _order = 'sequence, id'

    delivery_id = fields.Many2one(
        'garment.delivery.order',
        string='Phiếu Giao',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    style_code = fields.Char(string='Mã Hàng', required=True)
    color = fields.Char(string='Màu')
    size = fields.Char(string='Size')
    quantity = fields.Integer(string='Số Lượng', required=True)
    carton_qty = fields.Integer(string='Số Thùng')
    pcs_per_carton = fields.Integer(string='Số Cái / Thùng')
    gross_weight = fields.Float(string='Trọng Lượng (Kg)')
    notes = fields.Char(string='Ghi Chú')
