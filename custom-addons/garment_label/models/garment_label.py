from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentLabel(models.Model):
    _name = 'garment.label'
    _description = 'Tem / Nhãn (QR Code)'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _rec_name = 'code'

    code = fields.Char(
        string='Mã Tem',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        index=True,
    )
    qr_content = fields.Char(
        string='Nội Dung QR',
        compute='_compute_qr_content',
        store=True,
    )
    label_type = fields.Selection([
        ('product', 'Tem Sản Phẩm'),
        ('carton', 'Tem Thùng Hàng'),
        ('pallet', 'Tem Pallet'),
        ('location', 'Tem Vị Trí Kho'),
    ], string='Loại Tem', required=True, default='product', tracking=True)

    # --- Product info ---
    garment_order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng May')
    style_id = fields.Many2one(
        'garment.style', string='Mẫu May')
    color_id = fields.Many2one(
        'garment.color', string='Màu')
    size_id = fields.Many2one(
        'garment.size', string='Size')

    # --- Carton / Pallet reference ---
    pallet_id = fields.Many2one(
        'garment.pallet', string='Pallet')
    carton_id = fields.Many2one(
        'garment.carton.box', string='Thùng Hàng')
    packing_list_id = fields.Many2one(
        'garment.packing.list', string='Packing List')

    # --- Location tracking ---
    location = fields.Char(string='Vị Trí Hiện Tại')
    warehouse_zone = fields.Selection([
        ('material', 'Kho Nguyên Liệu'),
        ('wip', 'Kho Bán Thành Phẩm'),
        ('finished', 'Kho Thành Phẩm'),
        ('shipping', 'Khu Xuất Hàng'),
    ], string='Khu Vực Kho')

    quantity = fields.Integer(string='Số Lượng', default=1)
    print_count = fields.Integer(string='Số Lần In', default=0)
    last_print_date = fields.Datetime(string='Lần In Cuối')
    last_scan_date = fields.Datetime(string='Lần Quét Cuối')

    description = fields.Text(string='Mô Tả')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('printed', 'Đã In'),
        ('applied', 'Đã Dán'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                label_type = vals.get('label_type', 'product')
                prefix_map = {
                    'product': 'garment.label.product',
                    'carton': 'garment.label.carton',
                    'pallet': 'garment.label.pallet',
                    'location': 'garment.label.location',
                }
                seq_code = prefix_map.get(label_type, 'garment.label.product')
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    seq_code
                ) or 'New'
        return super().create(vals_list)

    @api.depends('code', 'label_type', 'garment_order_id', 'style_id',
                 'color_id', 'size_id', 'quantity')
    def _compute_qr_content(self):
        for label in self:
            parts = [label.code or '']
            if label.label_type:
                parts.append(label.label_type)
            if label.garment_order_id:
                parts.append(label.garment_order_id.name or '')
            if label.style_id:
                parts.append(label.style_id.code or '')
            if label.color_id:
                parts.append(label.color_id.name or '')
            if label.size_id:
                parts.append(label.size_id.name or '')
            if label.quantity:
                parts.append(str(label.quantity))
            label.qr_content = '|'.join(parts)

    def action_print(self):
        """Mark label as printed and increment print count."""
        for label in self:
            label.write({
                'state': 'printed',
                'print_count': label.print_count + 1,
                'last_print_date': fields.Datetime.now(),
            })

    def action_apply(self):
        for label in self:
            if label.state != 'printed':
                raise UserError(_('Tem phải được in trước khi dán!'))
        self.write({'state': 'applied'})

    def action_scan(self):
        """Simulate QR scan - update last_scan_date."""
        self.write({'last_scan_date': fields.Datetime.now()})

    def action_cancel(self):
        for label in self:
            if label.state == 'applied':
                raise UserError(_('Không thể hủy tem đã dán!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
