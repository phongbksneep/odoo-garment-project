from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentStockMove(models.Model):
    _name = 'garment.stock.move'
    _description = 'Phiếu Nhập/Xuất Kho'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(
        string='Số Phiếu',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    move_type = fields.Selection([
        ('in', 'Nhập Kho'),
        ('out', 'Xuất Kho'),
        ('transfer', 'Chuyển Kho'),
    ], string='Loại Phiếu', required=True, default='in')

    warehouse_type = fields.Selection([
        ('material', 'Kho Nguyên Phụ Liệu'),
        ('wip', 'Kho Bán Thành Phẩm'),
        ('finished', 'Kho Thành Phẩm'),
        ('accessory', 'Kho Phụ Liệu'),
    ], string='Kho', required=True, default='material')

    reason = fields.Selection([
        ('purchase', 'Mua Hàng'),
        ('production', 'Sản Xuất'),
        ('delivery', 'Giao Hàng'),
        ('return', 'Trả Hàng'),
        ('subcontract', 'Gia Công'),
        ('adjustment', 'Điều Chỉnh'),
        ('other', 'Khác'),
    ], string='Lý Do', required=True, default='purchase')

    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Đối Tác',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
    )
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
    )

    line_ids = fields.One2many(
        'garment.stock.move.line',
        'move_id',
        string='Chi Tiết',
    )
    total_qty = fields.Float(
        string='Tổng Số Lượng',
        compute='_compute_totals',
        store=True,
    )
    total_value = fields.Float(
        string='Tổng Giá Trị',
        compute='_compute_totals',
        store=True,
        digits=(14, 0),
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi Chú')
    responsible_id = fields.Many2one(
        'hr.employee',
        string='Người Phụ Trách',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                mt = vals.get('move_type', 'in')
                if mt == 'in':
                    code = 'garment.stock.move.in'
                elif mt == 'out':
                    code = 'garment.stock.move.out'
                else:
                    code = 'garment.stock.move.transfer'
                vals['name'] = self.env['ir.sequence'].next_by_code(code) or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.quantity', 'line_ids.value')
    def _compute_totals(self):
        for rec in self:
            rec.total_qty = sum(rec.line_ids.mapped('quantity'))
            rec.total_value = sum(rec.line_ids.mapped('value'))

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Phải có ít nhất 1 dòng chi tiết!'))
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Không thể hủy phiếu đã hoàn thành!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentStockMoveLine(models.Model):
    _name = 'garment.stock.move.line'
    _description = 'Chi Tiết Phiếu Kho'
    _order = 'sequence, id'

    move_id = fields.Many2one(
        'garment.stock.move',
        string='Phiếu Kho',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    product_type = fields.Selection([
        ('fabric', 'Vải'),
        ('accessory', 'Phụ Liệu'),
        ('thread', 'Chỉ'),
        ('button', 'Nút / Khóa'),
        ('label', 'Nhãn / Tag'),
        ('packaging', 'Bao Bì / Thùng'),
        ('wip', 'Bán Thành Phẩm'),
        ('finished', 'Thành Phẩm'),
        ('other', 'Khác'),
    ], string='Loại Hàng', required=True, default='fabric')

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
        ('kg', 'Kg'),
        ('yard', 'Yard'),
        ('pcs', 'Cái'),
        ('roll', 'Cuộn'),
        ('box', 'Hộp / Thùng'),
        ('set', 'Bộ'),
        ('other', 'Khác'),
    ], string='Đơn Vị', default='m')

    quantity = fields.Float(
        string='Số Lượng',
        required=True,
    )
    unit_price = fields.Float(
        string='Đơn Giá',
        digits=(12, 2),
    )
    value = fields.Float(
        string='Giá Trị',
        compute='_compute_value',
        store=True,
        digits=(14, 0),
    )
    lot_number = fields.Char(string='Số Lô')
    notes = fields.Char(string='Ghi Chú')

    @api.depends('quantity', 'unit_price')
    def _compute_value(self):
        for line in self:
            line.value = line.quantity * line.unit_price
