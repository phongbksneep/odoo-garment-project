from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentMaterialAllocation(models.Model):
    _name = 'garment.material.allocation'
    _description = 'Phân Bổ Nguyên Liệu Cho Đơn Hàng'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Số Phiếu',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    date = fields.Date(
        string='Ngày Phân Bổ',
        required=True,
        default=fields.Date.today,
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
        required=True,
        tracking=True,
    )
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
        related='garment_order_id.style_id',
        store=True,
    )

    line_ids = fields.One2many(
        'garment.material.allocation.line',
        'allocation_id',
        string='Chi Tiết Phân Bổ',
    )
    total_items = fields.Integer(
        string='Số Mục',
        compute='_compute_totals',
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('issued', 'Đã Xuất Kho'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    issued_by = fields.Many2one(
        'hr.employee',
        string='Thủ Kho Xuất',
    )
    received_by = fields.Many2one(
        'hr.employee',
        string='Người Nhận',
    )
    notes = fields.Text(string='Ghi Chú')

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.material.allocation'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('line_ids')
    def _compute_totals(self):
        for rec in self:
            rec.total_items = len(rec.line_ids)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Phải có ít nhất 1 dòng phân bổ!'))
        self.write({'state': 'confirmed'})

    def action_issue(self):
        self.write({'state': 'issued'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'issued':
                raise UserError(_('Không thể hủy phiếu đã xuất kho!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentMaterialAllocationLine(models.Model):
    _name = 'garment.material.allocation.line'
    _description = 'Chi Tiết Phân Bổ NL'
    _order = 'sequence, id'

    allocation_id = fields.Many2one(
        'garment.material.allocation',
        string='Phiếu Phân Bổ',
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
        ('other', 'Khác'),
    ], string='Loại NL', required=True, default='fabric')

    description = fields.Char(
        string='Mô Tả',
        required=True,
    )
    fabric_id = fields.Many2one(
        'garment.fabric',
        string='Vải',
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Màu',
    )
    unit = fields.Selection([
        ('m', 'Mét'),
        ('yard', 'Yard'),
        ('kg', 'Kg'),
        ('roll', 'Cuộn'),
        ('pcs', 'Cái'),
        ('set', 'Bộ'),
        ('cone', 'Cuộn Chỉ'),
        ('other', 'Khác'),
    ], string='Đơn Vị', default='m', required=True)

    quantity_required = fields.Float(
        string='SL Yêu Cầu',
        digits=(12, 2),
        help='Số lượng cần theo BOM / định mức',
    )
    quantity_issued = fields.Float(
        string='SL Xuất',
        required=True,
        digits=(12, 2),
    )
    lot_number = fields.Char(string='Số Lô')
    receipt_id = fields.Many2one(
        'garment.material.receipt',
        string='Phiếu Nhập Gốc',
        help='Phiếu nhập NL nguồn gốc',
    )
    notes = fields.Char(string='Ghi Chú')
