from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentInventory(models.Model):
    _name = 'garment.inventory'
    _description = 'Phiếu Kiểm Kê Kho'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Số Phiếu',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        index=True,
    )
    date = fields.Date(
        string='Ngày Kiểm Kê',
        required=True,
        default=fields.Date.today,
    )
    warehouse_type = fields.Selection([
        ('material', 'Kho Nguyên Phụ Liệu'),
        ('wip', 'Kho Bán Thành Phẩm'),
        ('finished', 'Kho Thành Phẩm'),
        ('accessory', 'Kho Phụ Liệu'),
        ('all', 'Toàn Bộ Kho'),
    ], string='Kho Kiểm Kê', required=True, default='finished')

    responsible_id = fields.Many2one(
        'hr.employee',
        string='Người Phụ Trách',
    )
    team_member_ids = fields.Many2many(
        'hr.employee',
        'garment_inventory_team_rel',
        'inventory_id',
        'employee_id',
        string='Nhóm Kiểm Kê',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng (nếu kiểm theo ĐH)',
    )
    line_ids = fields.One2many(
        'garment.inventory.line',
        'inventory_id',
        string='Chi Tiết Kiểm Kê',
    )

    total_expected_qty = fields.Float(
        string='Tổng SL Sổ Sách',
        compute='_compute_totals',
        store=True,
    )
    total_actual_qty = fields.Float(
        string='Tổng SL Thực Tế',
        compute='_compute_totals',
        store=True,
    )
    total_diff_qty = fields.Float(
        string='Tổng Chênh Lệch',
        compute='_compute_totals',
        store=True,
    )
    diff_count = fields.Integer(
        string='Số Dòng Chênh Lệch',
        compute='_compute_totals',
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang Kiểm Kê'),
        ('done', 'Hoàn Thành'),
        ('validated', 'Đã Xác Nhận'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    adjustment_move_id = fields.Many2one(
        'garment.stock.move',
        string='Phiếu Điều Chỉnh',
        readonly=True,
    )
    notes = fields.Text(string='Ghi Chú')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.inventory'
                ) or 'New'
        return super().create(vals_list)

    @api.depends('line_ids.expected_qty', 'line_ids.actual_qty',
                 'line_ids.diff_qty')
    def _compute_totals(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_expected_qty = sum(lines.mapped('expected_qty'))
            rec.total_actual_qty = sum(lines.mapped('actual_qty'))
            rec.total_diff_qty = sum(lines.mapped('diff_qty'))
            rec.diff_count = len(lines.filtered(
                lambda l: l.diff_qty != 0
            ))

    def action_start(self):
        """Start inventory counting."""
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Phải thêm ít nhất 1 dòng kiểm kê!'))
        self.write({'state': 'in_progress'})

    def action_done(self):
        """Complete counting."""
        self.write({'state': 'done'})

    def action_validate(self):
        """Validate and optionally create adjustment."""
        for rec in self:
            if rec.state != 'done':
                raise UserError(_(
                    'Phiếu phải ở trạng thái Hoàn Thành trước khi xác nhận!'
                ))
            if rec.diff_count > 0 and not rec.adjustment_move_id:
                rec._create_adjustment_move()
        self.write({'state': 'validated'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'validated':
                raise UserError(_(
                    'Không thể hủy phiếu kiểm kê đã xác nhận!'
                ))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_scan_qr(self):
        """Action triggered by QR scan — searches for label and adds/updates
        an inventory line. In real deployment, the QR scanner calls this
        endpoint with the scanned data. For now we provide the action
        placeholder."""
        # Placeholder: in production, this would be called via RPC
        # with the QR content from a scanning device or mobile app.
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quét QR Nhập Hàng'),
            'res_model': 'garment.inventory.scan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_inventory_id': self.id},
        }

    def _create_adjustment_move(self):
        """Create a stock adjustment move for differences found."""
        self.ensure_one()
        diff_lines = self.line_ids.filtered(lambda l: l.diff_qty != 0)
        if not diff_lines:
            return

        # Map inventory item_type to stock move product_type
        type_map = {
            'fabric': 'fabric',
            'accessory': 'accessory',
            'wip': 'wip',
            'finished': 'finished',
            'other': 'other',
        }
        move = self.env['garment.stock.move'].create({
            'move_type': 'in',  # adjustment
            'warehouse_type': self.warehouse_type if self.warehouse_type != 'all' else 'finished',
            'reason': 'adjustment',
            'garment_order_id': self.garment_order_id.id if self.garment_order_id else False,
            'notes': _('Điều chỉnh từ kiểm kê %s') % self.name,
            'line_ids': [(0, 0, {
                'product_type': type_map.get(line.item_type, 'other'),
                'description': '%s [%s]' % (line.item_name, line.item_code) if line.item_code else line.item_name,
                'quantity': abs(line.diff_qty),
                'unit': line.unit,
                'notes': _('Chênh lệch: %+.2f') % line.diff_qty,
            }) for line in diff_lines],
        })
        move.action_confirm()
        self.adjustment_move_id = move


class GarmentInventoryLine(models.Model):
    _name = 'garment.inventory.line'
    _description = 'Chi Tiết Kiểm Kê'
    _order = 'sequence, id'

    inventory_id = fields.Many2one(
        'garment.inventory',
        string='Phiếu Kiểm Kê',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)

    item_type = fields.Selection([
        ('fabric', 'Vải'),
        ('accessory', 'Phụ Liệu'),
        ('product', 'Thành Phẩm'),
        ('wip', 'Bán Thành Phẩm'),
        ('carton', 'Thùng Hàng'),
        ('other', 'Khác'),
    ], string='Loại Hàng', required=True, default='product')

    item_name = fields.Char(string='Tên Hàng', required=True)
    item_code = fields.Char(string='Mã Hàng')
    style_code = fields.Char(string='Mã Style')
    color = fields.Char(string='Màu')
    size = fields.Char(string='Size')
    location = fields.Char(string='Vị Trí Kho')
    unit = fields.Char(string='Đơn Vị', default='pcs')

    label_id = fields.Many2one(
        'garment.label',
        string='Tem QR (nếu quét)',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng',
    )

    expected_qty = fields.Float(string='SL Sổ Sách', digits=(14, 2))
    actual_qty = fields.Float(string='SL Thực Tế', digits=(14, 2))
    diff_qty = fields.Float(
        string='Chênh Lệch',
        compute='_compute_diff',
        store=True,
        digits=(14, 2),
    )
    diff_percent = fields.Float(
        string='% Chênh Lệch',
        compute='_compute_diff',
        store=True,
        digits=(10, 2),
    )
    status = fields.Selection([
        ('ok', 'Khớp'),
        ('surplus', 'Thừa'),
        ('deficit', 'Thiếu'),
    ], string='Kết Quả', compute='_compute_diff', store=True)

    notes = fields.Char(string='Ghi Chú')

    @api.depends('expected_qty', 'actual_qty')
    def _compute_diff(self):
        for line in self:
            line.diff_qty = line.actual_qty - line.expected_qty
            if line.expected_qty:
                line.diff_percent = (
                    line.diff_qty / line.expected_qty * 100
                )
            else:
                line.diff_percent = 0
            if line.diff_qty > 0:
                line.status = 'surplus'
            elif line.diff_qty < 0:
                line.status = 'deficit'
            else:
                line.status = 'ok'


class GarmentInventoryScanWizard(models.TransientModel):
    _name = 'garment.inventory.scan.wizard'
    _description = 'Wizard Quét QR Kiểm Kê'

    inventory_id = fields.Many2one(
        'garment.inventory',
        string='Phiếu Kiểm Kê',
        required=True,
    )
    qr_content = fields.Char(
        string='Nội Dung QR',
        required=True,
        help='Quét hoặc nhập mã QR code',
    )
    actual_qty = fields.Float(
        string='Số Lượng Thực Tế',
        default=1,
        required=True,
    )

    def action_scan(self):
        """Process scanned QR code and add to inventory."""
        self.ensure_one()
        qr = self.qr_content.strip()
        if not qr:
            raise UserError(_('Vui lòng nhập mã QR!'))

        # Try to find label by code or qr_content
        label = self.env['garment.label'].search([
            '|', ('code', '=', qr), ('qr_content', '=', qr)
        ], limit=1)

        vals = {
            'inventory_id': self.inventory_id.id,
            'actual_qty': self.actual_qty,
        }

        if label:
            vals.update({
                'label_id': label.id,
                'item_code': label.code,
                'item_name': label.style_id.name if label.style_id else label.code,
                'style_code': label.style_id.code if label.style_id else '',
                'color': label.color_id.name if label.color_id else '',
                'size': label.size_id.name if label.size_id else '',
                'garment_order_id': label.garment_order_id.id if label.garment_order_id else False,
                'location': label.location or '',
            })
            if label.label_type == 'carton':
                vals['item_type'] = 'carton'
            elif label.label_type in ('product',):
                vals['item_type'] = 'product'
            else:
                vals['item_type'] = 'other'
            # Update last scan on label
            label.action_scan()
        else:
            # Manual entry — just store the QR content
            vals.update({
                'item_code': qr,
                'item_name': qr,
                'item_type': 'other',
            })

        # Check if line already exists for this item
        existing = self.inventory_id.line_ids.filtered(
            lambda l: l.item_code == vals.get('item_code')
        )
        if existing:
            existing[0].actual_qty += self.actual_qty
        else:
            self.env['garment.inventory.line'].create(vals)

        # Return wizard again for continuous scanning
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quét QR Nhập Hàng'),
            'res_model': 'garment.inventory.scan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_inventory_id': self.inventory_id.id},
        }
