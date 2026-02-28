from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentShippingInstruction(models.Model):
    _name = 'garment.shipping.instruction'
    _description = 'Shipping Instruction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Số SI',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    packing_list_id = fields.Many2one(
        'garment.packing.list',
        string='Packing List',
        required=True,
        tracking=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng',
        related='packing_list_id.garment_order_id',
        store=True,
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        related='packing_list_id.buyer_id',
        store=True,
    )
    date = fields.Date(
        string='Ngày Tạo SI',
        default=fields.Date.today,
    )

    # --- Shipper / Consignee ---
    shipper_name = fields.Char(
        string='Shipper (Người Gửi)',
        default=lambda self: self.env.company.name,
    )
    shipper_address = fields.Text(string='Địa Chỉ Shipper')
    consignee_name = fields.Char(string='Consignee (Người Nhận)')
    consignee_address = fields.Text(string='Địa Chỉ Consignee')
    notify_party = fields.Text(string='Notify Party')

    # --- Shipment Details ---
    port_of_loading = fields.Char(string='Cảng Xếp Hàng (Port of Loading)')
    port_of_discharge = fields.Char(
        string='Cảng Dỡ Hàng (Port of Discharge)',
        related='packing_list_id.destination_port',
        store=True,
        readonly=False,
    )
    ship_mode = fields.Selection(
        related='packing_list_id.ship_mode',
        store=True,
    )
    vessel_name = fields.Char(
        string='Tên Tàu / Chuyến Bay',
        related='packing_list_id.vessel_name',
        store=True,
        readonly=False,
    )
    etd = fields.Date(
        string='ETD',
        related='packing_list_id.etd',
        store=True,
        readonly=False,
    )
    eta = fields.Date(
        string='ETA',
        related='packing_list_id.eta',
        store=True,
        readonly=False,
    )

    # --- Cargo Details ---
    cargo_description = fields.Text(string='Mô Tả Hàng Hóa')
    total_cartons = fields.Integer(
        string='Tổng Số Thùng',
        related='packing_list_id.total_cartons',
        store=True,
    )
    total_pieces = fields.Integer(
        string='Tổng Số SP',
        related='packing_list_id.total_pieces',
        store=True,
    )
    total_gross_weight = fields.Float(
        string='Tổng Trọng Lượng (kg)',
        related='packing_list_id.total_gross_weight',
        store=True,
    )
    total_cbm = fields.Float(
        string='Tổng Thể Tích (m³)',
        related='packing_list_id.total_cbm',
        store=True,
    )

    # --- Payment / Terms ---
    payment_term = fields.Selection([
        ('tt', 'T/T (Telegraphic Transfer)'),
        ('lc', 'L/C (Letter of Credit)'),
        ('da', 'D/A (Documents Against Acceptance)'),
        ('dp', 'D/P (Documents Against Payment)'),
    ], string='Điều Khoản Thanh Toán')
    incoterm = fields.Selection([
        ('fob', 'FOB'),
        ('cif', 'CIF'),
        ('cfr', 'CFR'),
        ('exw', 'EXW'),
        ('dap', 'DAP'),
        ('ddp', 'DDP'),
    ], string='Incoterm', default='fob')
    lc_number = fields.Char(string='Số L/C')

    # --- Documents Required ---
    doc_commercial_invoice = fields.Boolean(
        string='Commercial Invoice',
        default=True,
    )
    doc_packing_list = fields.Boolean(
        string='Packing List',
        default=True,
    )
    doc_bill_of_lading = fields.Boolean(
        string='Bill of Lading',
        default=True,
    )
    doc_certificate_of_origin = fields.Boolean(
        string='Certificate of Origin',
        default=True,
    )
    doc_fumigation = fields.Boolean(string='Fumigation Certificate')
    doc_inspection = fields.Boolean(string='Inspection Certificate')
    doc_others = fields.Text(string='Chứng Từ Khác')

    special_instructions = fields.Text(string='Hướng Dẫn Đặc Biệt')
    notes = fields.Text(string='Ghi Chú')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('sent', 'Đã Gửi Hãng Tàu'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.shipping.instruction'
                ) or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_send(self):
        self.write({'state': 'sent'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        if self.state == 'done':
            raise UserError(_('Không thể hủy SI đã hoàn thành.'))
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})

    @api.onchange('packing_list_id')
    def _onchange_packing_list(self):
        if self.packing_list_id:
            buyer = self.packing_list_id.buyer_id
            if buyer:
                self.consignee_name = buyer.name
                addr_parts = [
                    buyer.street, buyer.street2,
                    buyer.city, buyer.state_id.name if buyer.state_id else '',
                    buyer.zip, buyer.country_id.name if buyer.country_id else '',
                ]
                self.consignee_address = ', '.join(
                    p for p in addr_parts if p
                )
            company = self.env.company
            addr_parts = [
                company.street, company.street2,
                company.city, company.state_id.name if company.state_id else '',
                company.zip, company.country_id.name if company.country_id else '',
            ]
            self.shipper_address = ', '.join(
                p for p in addr_parts if p
            )
