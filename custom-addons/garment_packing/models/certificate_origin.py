from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentCertificateOrigin(models.Model):
    _name = 'garment.certificate.origin'
    _description = 'Certificate of Origin'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Số C/O',
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
        string='Ngày Cấp',
        default=fields.Date.today,
    )

    # --- Exporter / Importer ---
    exporter_name = fields.Char(
        string='Người Xuất Khẩu (Exporter)',
        default=lambda self: self.env.company.name,
    )
    exporter_address = fields.Text(string='Địa Chỉ Exporters')
    importer_name = fields.Char(string='Người Nhập Khẩu (Importer)')
    importer_address = fields.Text(string='Địa Chỉ Importer')

    # --- Goods / Origin ---
    co_type = fields.Selection([
        ('form_a', 'Form A (GSP)'),
        ('form_b', 'Form B'),
        ('form_d', 'Form D (ASEAN/ATIGA)'),
        ('form_e', 'Form E (ASEAN-China)'),
        ('form_ak', 'Form AK (ASEAN-Korea)'),
        ('form_aj', 'Form AJ (ASEAN-Japan)'),
        ('form_ai', 'Form AI (ASEAN-India)'),
        ('form_aanz', 'Form AANZ (ASEAN-ANZ)'),
        ('form_vc', 'Form VC (Vietnam-Chile)'),
        ('form_vk', 'Form VK (Vietnam-Korea)'),
        ('eur1', 'EUR.1 (EVFTA)'),
        ('cptpp', 'CPTPP'),
        ('rcep', 'RCEP'),
        ('non_preferential', 'Non-Preferential'),
    ], string='Loại C/O', required=True, tracking=True)
    country_of_origin = fields.Char(
        string='Nước Xuất Xứ',
        default='Vietnam',
    )
    destination_country = fields.Char(string='Nước Đến')
    transport_means = fields.Char(string='Phương Tiện Vận Tải')
    port_of_loading = fields.Char(string='Cảng Xếp Hàng')
    port_of_discharge = fields.Char(
        string='Cảng Dỡ Hàng',
        related='packing_list_id.destination_port',
        store=True,
        readonly=False,
    )

    # --- Line Items ---
    line_ids = fields.One2many(
        'garment.certificate.origin.line',
        'certificate_id',
        string='Chi Tiết Hàng Hóa',
    )

    # --- Certification ---
    issuing_authority = fields.Char(
        string='Cơ Quan Cấp',
        default='Phòng Thương Mại & Công Nghiệp Việt Nam (VCCI)',
    )
    reference_no = fields.Char(string='Số Tham Chiếu VCCI')
    invoice_number = fields.Char(string='Số Invoice')
    invoice_date = fields.Date(string='Ngày Invoice')

    notes = fields.Text(string='Ghi Chú')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('applied', 'Đã Nộp Hồ Sơ'),
        ('approved', 'Đã Duyệt'),
        ('issued', 'Đã Cấp'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.certificate.origin'
                ) or _('New')
        return super().create(vals_list)

    def action_apply(self):
        self.write({'state': 'applied'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_issue(self):
        self.write({'state': 'issued'})

    def action_cancel(self):
        if self.state == 'issued':
            raise UserError(_('Không thể hủy C/O đã cấp.'))
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})

    @api.onchange('packing_list_id')
    def _onchange_packing_list(self):
        if self.packing_list_id:
            buyer = self.packing_list_id.buyer_id
            if buyer:
                self.importer_name = buyer.name
                addr_parts = [
                    buyer.street, buyer.street2,
                    buyer.city, buyer.state_id.name if buyer.state_id else '',
                    buyer.zip, buyer.country_id.name if buyer.country_id else '',
                ]
                self.importer_address = ', '.join(
                    p for p in addr_parts if p
                )
                if buyer.country_id:
                    self.destination_country = buyer.country_id.name
            company = self.env.company
            addr_parts = [
                company.street, company.street2,
                company.city, company.state_id.name if company.state_id else '',
                company.zip, company.country_id.name if company.country_id else '',
            ]
            self.exporter_address = ', '.join(
                p for p in addr_parts if p
            )


class GarmentCertificateOriginLine(models.Model):
    _name = 'garment.certificate.origin.line'
    _description = 'Certificate of Origin Line'
    _order = 'sequence'

    certificate_id = fields.Many2one(
        'garment.certificate.origin',
        string='Chứng Nhận Xuất Xứ',
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    description = fields.Text(string='Mô Tả Hàng Hóa', required=True)
    hs_code = fields.Char(string='Mã HS')
    quantity = fields.Float(string='Số Lượng')
    uom = fields.Char(string='Đơn Vị', default='PCS')
    weight = fields.Float(string='Trọng Lượng (kg)')
    fob_value = fields.Float(string='Trị Giá FOB (USD)')
    origin_criteria = fields.Selection([
        ('wh', 'WO - Wholly Obtained'),
        ('pe', 'PE - Produced Entirely'),
        ('rvc', 'RVC - Regional Value Content'),
        ('ctc', 'CTC - Change in Tariff Classification'),
        ('sp', 'SP - Specific Process'),
    ], string='Tiêu Chí Xuất Xứ')
