from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentMaterialReceipt(models.Model):
    _name = 'garment.material.receipt'
    _description = 'Phiếu Nhập Nguyên Liệu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _check_company_auto = True

    name = fields.Char(
        string='Số Phiếu',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    company_id = fields.Many2one(
        'res.company',
        string='Công Ty',
        default=lambda self: self.env.company,
        required=True,
    )

    # --- Receipt Type ---
    receipt_type = fields.Selection([
        ('purchase', 'Mua Hàng (Purchase)'),
        ('buyer_supplied', 'Khách Gửi (Buyer-Supplied / CMT)'),
        ('return', 'NL Trả Về Từ SX'),
        ('subcontract', 'NL Từ Gia Công'),
    ], string='Loại Nhập', required=True, default='purchase', tracking=True)

    # --- Parties ---
    supplier_id = fields.Many2one(
        'res.partner',
        string='Nhà Cung Cấp',
        tracking=True,
        domain=[('supplier_rank', '>', 0)],
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng Gửi NL',
        tracking=True,
        domain=[('customer_rank', '>', 0)],
        help='Chỉ dùng cho loại "Khách Gửi" — buyer gửi nguyên liệu để gia công',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
        tracking=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
    )

    # --- Dates ---
    date = fields.Date(
        string='Ngày Nhập',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    expected_date = fields.Date(
        string='Ngày Dự Kiến',
        help='Ngày dự kiến NL về theo PO / buyer thông báo',
    )
    is_late = fields.Boolean(
        string='Trễ Hạn',
        compute='_compute_is_late',
        store=True,
    )

    # --- Document Info ---
    po_number = fields.Char(
        string='Số PO Mua Hàng',
        help='PO cho NCC hoặc số chứng từ buyer gửi',
    )
    invoice_number = fields.Char(
        string='Số Hóa Đơn / Packing List',
    )
    transport_info = fields.Char(
        string='Thông Tin Vận Chuyển',
        help='Số cont, BL, xe, courier...',
    )

    # --- Warehouse ---
    warehouse_type = fields.Selection([
        ('material', 'Kho Nguyên Liệu'),
        ('accessory', 'Kho Phụ Liệu'),
        ('both', 'NL + PL'),
    ], string='Kho Nhập', default='material', required=True)

    # --- Lines ---
    line_ids = fields.One2many(
        'garment.material.receipt.line',
        'receipt_id',
        string='Chi Tiết Nguyên Liệu',
    )

    # --- Totals ---
    total_lines = fields.Integer(
        string='Số Dòng',
        compute='_compute_totals',
        store=True,
    )
    total_qty = fields.Float(
        string='Tổng SL',
        compute='_compute_totals',
        store=True,
    )
    total_value = fields.Float(
        string='Tổng Giá Trị',
        compute='_compute_totals',
        store=True,
        digits=(14, 0),
    )

    # --- QC ---
    qc_status = fields.Selection([
        ('pending', 'Chưa Kiểm'),
        ('pass', 'Đạt'),
        ('partial', 'Đạt Một Phần'),
        ('fail', 'Không Đạt'),
    ], string='Kết Quả QC', default='pending', tracking=True)
    qc_notes = fields.Text(
        string='Ghi Chú QC',
    )

    # --- State ---
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('inspecting', 'Đang Kiểm Tra'),
        ('done', 'Đã Nhập Kho'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Html(string='Ghi Chú')
    responsible_id = fields.Many2one(
        'hr.employee',
        string='Thủ Kho Nhận',
    )

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                rt = vals.get('receipt_type', 'purchase')
                if rt == 'buyer_supplied':
                    code = 'garment.material.receipt.buyer'
                else:
                    code = 'garment.material.receipt'
                vals['name'] = self.env['ir.sequence'].next_by_code(code) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains('receipt_type', 'supplier_id', 'buyer_id')
    def _check_partner(self):
        for rec in self:
            if rec.receipt_type == 'purchase' and not rec.supplier_id:
                raise ValidationError(
                    _('Phiếu nhập "Mua Hàng" phải có Nhà Cung Cấp!')
                )
            if rec.receipt_type == 'buyer_supplied' and not rec.buyer_id:
                raise ValidationError(
                    _('Phiếu nhập "Khách Gửi" phải có Khách Hàng!')
                )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('line_ids.quantity', 'line_ids.value')
    def _compute_totals(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_lines = len(lines)
            rec.total_qty = sum(lines.mapped('quantity'))
            rec.total_value = sum(lines.mapped('value'))

    @api.depends('date', 'expected_date')
    def _compute_is_late(self):
        for rec in self:
            if rec.expected_date and rec.date:
                rec.is_late = rec.date > rec.expected_date
            else:
                rec.is_late = False

    # -------------------------------------------------------------------------
    # Onchange
    # -------------------------------------------------------------------------
    @api.onchange('garment_order_id')
    def _onchange_garment_order(self):
        if self.garment_order_id:
            self.style_id = self.garment_order_id.style_id
            if self.receipt_type == 'buyer_supplied':
                self.buyer_id = self.garment_order_id.customer_id

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Phải có ít nhất 1 dòng nguyên liệu!'))
        self.write({'state': 'confirmed'})

    def action_inspect(self):
        self.write({'state': 'inspecting'})

    def action_done(self):
        for rec in self:
            if rec.state == 'inspecting' and rec.qc_status == 'pending':
                raise UserError(
                    _('Vui lòng cập nhật Kết Quả QC trước khi hoàn thành!')
                )
        self.write({'state': 'done'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(
                    _('Không thể hủy phiếu đã nhập kho!')
                )
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_pass_qc(self):
        self.write({'qc_status': 'pass'})

    def action_fail_qc(self):
        self.write({'qc_status': 'fail'})


class GarmentMaterialReceiptLine(models.Model):
    _name = 'garment.material.receipt.line'
    _description = 'Chi Tiết Phiếu Nhập Nguyên Liệu'
    _order = 'material_type, sequence, id'

    receipt_id = fields.Many2one(
        'garment.material.receipt',
        string='Phiếu Nhập',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)

    material_type = fields.Selection([
        ('fabric', 'Vải'),
        ('lining', 'Vải Lót'),
        ('interlining', 'Mex / Keo'),
        ('thread', 'Chỉ'),
        ('zipper', 'Khóa Kéo'),
        ('button', 'Nút / Cúc'),
        ('label', 'Nhãn / Tag'),
        ('elastic', 'Thun / Dây'),
        ('packaging', 'Bao Bì'),
        ('other', 'Khác'),
    ], string='Loại NL', required=True, default='fabric')

    fabric_id = fields.Many2one(
        'garment.fabric',
        string='Vải',
        help='Liên kết vải từ danh mục (nếu là vải)',
    )
    description = fields.Char(
        string='Mô Tả',
        required=True,
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Màu',
    )
    lot_number = fields.Char(
        string='Số Lô / Roll No.',
    )

    # --- Quantity ---
    unit = fields.Selection([
        ('m', 'Mét'),
        ('yard', 'Yard'),
        ('kg', 'Kg'),
        ('roll', 'Cuộn'),
        ('pcs', 'Cái'),
        ('set', 'Bộ'),
        ('box', 'Hộp'),
        ('cone', 'Cuộn Chỉ'),
        ('other', 'Khác'),
    ], string='Đơn Vị', default='m', required=True)
    quantity_ordered = fields.Float(
        string='SL Đặt',
        digits=(12, 2),
    )
    quantity = fields.Float(
        string='SL Nhận Thực Tế',
        required=True,
        digits=(12, 2),
    )
    quantity_accepted = fields.Float(
        string='SL Đạt QC',
        digits=(12, 2),
    )
    quantity_rejected = fields.Float(
        string='SL Lỗi',
        digits=(12, 2),
        default=0,
    )
    shortage = fields.Float(
        string='Thiếu Hụt',
        compute='_compute_shortage',
        store=True,
        digits=(12, 2),
    )

    # --- Price ---
    unit_price = fields.Float(
        string='Đơn Giá',
        digits=(12, 4),
    )
    value = fields.Float(
        string='Giá Trị',
        compute='_compute_value',
        store=True,
        digits=(14, 0),
    )

    # --- QC ---
    width = fields.Float(
        string='Khổ Vải (cm)',
        digits=(10, 1),
        help='Khổ vải thực tế đo được',
    )
    weight_gsm = fields.Float(
        string='Trọng Lượng (GSM)',
        digits=(10, 1),
    )
    qc_result = fields.Selection([
        ('pass', 'Đạt'),
        ('fail', 'Không Đạt'),
        ('conditional', 'Đạt Có Điều Kiện'),
    ], string='KQ Kiểm')
    qc_notes = fields.Char(string='Ghi Chú QC')

    notes = fields.Char(string='Ghi Chú')

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('quantity_ordered', 'quantity')
    def _compute_shortage(self):
        for line in self:
            if line.quantity_ordered > 0:
                line.shortage = line.quantity_ordered - line.quantity
            else:
                line.shortage = 0

    @api.depends('quantity', 'unit_price')
    def _compute_value(self):
        for line in self:
            line.value = line.quantity * line.unit_price

    @api.onchange('fabric_id')
    def _onchange_fabric_id(self):
        if self.fabric_id:
            self.description = self.fabric_id.name
            if self.fabric_id.width:
                self.width = self.fabric_id.width
