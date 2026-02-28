from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentBOM(models.Model):
    """Bill of Materials for garment styles.

    Defines the exact material requirements (fabric, accessories, packing)
    for producing one unit of a garment style.  Used by the Costing module
    to auto-populate cost-sheet lines and by Material Allocation to
    calculate required quantities.
    """
    _name = 'garment.bom'
    _description = 'Định Mức Nguyên Phụ Liệu (BOM)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'style_id, version desc'
    _check_company_auto = True

    name = fields.Char(
        string='Mã BOM',
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
    style_id = fields.Many2one(
        'garment.style',
        string='Mã Hàng / Style',
        required=True,
        tracking=True,
    )
    version = fields.Integer(
        string='Phiên Bản',
        default=1,
        tracking=True,
    )
    date = fields.Date(
        string='Ngày Tạo',
        default=fields.Date.today,
        required=True,
    )
    active = fields.Boolean(default=True)

    line_ids = fields.One2many(
        'garment.bom.line',
        'bom_id',
        string='Chi Tiết BOM',
        copy=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('approved', 'Đã Duyệt'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi Chú')

    total_fabric_consumption = fields.Float(
        string='Tổng ĐM Vải (m)',
        compute='_compute_totals',
        store=True,
        digits=(12, 4),
    )
    total_material_cost = fields.Float(
        string='Tổng CP NL / SP',
        compute='_compute_totals',
        store=True,
        digits=(14, 2),
    )
    total_lines = fields.Integer(
        string='Số Dòng',
        compute='_compute_totals',
        store=True,
    )

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    _bom_style_version_unique = models.Constraint(
        'UNIQUE(style_id, version, company_id)',
        'Mỗi Style chỉ có 1 BOM cho mỗi phiên bản!',
    )

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.bom'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('line_ids.consumption', 'line_ids.material_type',
                 'line_ids.unit_price', 'line_ids.wastage_pct')
    def _compute_totals(self):
        for bom in self:
            fabric_lines = bom.line_ids.filtered(
                lambda l: l.material_type in ('fabric', 'lining')
            )
            bom.total_fabric_consumption = sum(fabric_lines.mapped('consumption'))
            bom.total_material_cost = sum(bom.line_ids.mapped('amount_per_pc'))
            bom.total_lines = len(bom.line_ids)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('BOM phải có ít nhất 1 dòng chi tiết!'))
        self.write({'state': 'confirmed'})

    def action_approve(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError(_('Chỉ BOM đã xác nhận mới được duyệt!'))
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_new_version(self):
        """Create a new version of this BOM."""
        self.ensure_one()
        new_version = self.version + 1
        new_bom = self.copy({
            'version': new_version,
            'state': 'draft',
            'date': fields.Date.today(),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'garment.bom',
            'res_id': new_bom.id,
            'view_mode': 'form',
            'target': 'current',
        }


class GarmentBOMLine(models.Model):
    _name = 'garment.bom.line'
    _description = 'Chi Tiết BOM'
    _order = 'material_type, sequence, id'

    bom_id = fields.Many2one(
        'garment.bom',
        string='BOM',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)

    material_type = fields.Selection([
        ('fabric', 'Vải Chính'),
        ('lining', 'Vải Lót'),
        ('interlining', 'Mex / Keo Dựng'),
        ('thread', 'Chỉ May'),
        ('zipper', 'Khóa Kéo'),
        ('button', 'Nút / Cúc'),
        ('label', 'Nhãn Mác'),
        ('elastic', 'Thun / Dây'),
        ('packing', 'Đóng Gói'),
        ('other', 'Khác'),
    ], string='Loại NL', required=True, default='fabric')

    description = fields.Char(
        string='Mô Tả',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Sản Phẩm',
    )
    fabric_id = fields.Many2one(
        'garment.fabric',
        string='Vải',
        help='Chọn vải (nếu loại NL là vải)',
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Màu',
    )

    uom = fields.Selection([
        ('m', 'Mét'),
        ('yard', 'Yard'),
        ('kg', 'Kg'),
        ('pcs', 'Cái'),
        ('set', 'Bộ'),
        ('cone', 'Cuộn Chỉ'),
        ('roll', 'Cuộn'),
        ('other', 'Khác'),
    ], string='Đơn Vị', default='m', required=True)

    consumption = fields.Float(
        string='Định Mức / SP',
        digits=(12, 4),
        required=True,
        help='Số lượng nguyên liệu cần cho 1 sản phẩm',
    )
    wastage_pct = fields.Float(
        string='Hao Hụt (%)',
        default=3.0,
        digits=(5, 2),
    )
    unit_price = fields.Float(
        string='Đơn Giá',
        digits=(12, 4),
    )
    amount_per_pc = fields.Float(
        string='Thành Tiền / SP',
        compute='_compute_amount',
        store=True,
        digits=(14, 4),
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Nhà Cung Cấp',
        domain=[('supplier_rank', '>', 0)],
    )
    notes = fields.Char(string='Ghi Chú')

    @api.depends('consumption', 'unit_price', 'wastage_pct')
    def _compute_amount(self):
        for line in self:
            consumption_with_wastage = line.consumption * (
                1.0 + line.wastage_pct / 100.0
            )
            line.amount_per_pc = consumption_with_wastage * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.standard_price

    @api.onchange('fabric_id')
    def _onchange_fabric_id(self):
        if self.fabric_id and not self.description:
            self.description = self.fabric_id.name
