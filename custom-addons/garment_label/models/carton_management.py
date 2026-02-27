from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentCartonBox(models.Model):
    _name = 'garment.carton.box'
    _description = 'Thùng Hàng (Carton Box)'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Mã Thùng',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        index=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng May')
    packing_list_id = fields.Many2one(
        'garment.packing.list', string='Packing List')
    pallet_id = fields.Many2one(
        'garment.pallet', string='Pallet')

    # --- Content ---
    style_code = fields.Char(string='Mã Hàng')
    color = fields.Char(string='Màu')
    size = fields.Char(string='Size')
    quantity = fields.Integer(string='Số Lượng (Cái)', required=True)

    # --- Dimensions ---
    length_cm = fields.Float(string='Dài (cm)', digits=(10, 1))
    width_cm = fields.Float(string='Rộng (cm)', digits=(10, 1))
    height_cm = fields.Float(string='Cao (cm)', digits=(10, 1))
    gross_weight = fields.Float(
        string='Trọng Lượng Gross (kg)',
        digits=(10, 2),
    )
    net_weight = fields.Float(
        string='Trọng Lượng Net (kg)',
        digits=(10, 2),
    )
    cbm = fields.Float(
        string='CBM (m³)',
        compute='_compute_cbm',
        store=True,
        digits=(10, 4),
    )

    location = fields.Char(string='Vị Trí Kho')

    qr_label_id = fields.Many2one(
        'garment.label', string='Tem QR')

    notes = fields.Text(string='Ghi Chú')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('packed', 'Đã Đóng'),
        ('on_pallet', 'Trên Pallet'),
        ('shipped', 'Đã Xuất'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.carton.box'
                ) or 'New'
        return super().create(vals_list)

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for box in self:
            box.cbm = (
                box.length_cm * box.width_cm * box.height_cm
            ) / 1_000_000

    def action_pack(self):
        self.write({'state': 'packed'})

    def action_put_on_pallet(self):
        for box in self:
            if not box.pallet_id:
                raise UserError(_('Phải chọn pallet trước!'))
            if box.state != 'packed':
                raise UserError(_('Thùng phải ở trạng thái Đã Đóng!'))
        self.write({'state': 'on_pallet'})

    def action_ship(self):
        self.write({'state': 'shipped'})

    def action_cancel(self):
        for box in self:
            if box.state == 'shipped':
                raise UserError(_('Không thể hủy thùng đã xuất!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft', 'pallet_id': False})

    def action_merge_cartons(self):
        """Merge multiple cartons into one."""
        if len(self) < 2:
            raise UserError(_('Cần chọn ít nhất 2 thùng để gộp!'))
        for box in self:
            if box.state not in ('draft', 'packed'):
                raise UserError(_(
                    'Chỉ gộp được thùng ở trạng thái Nháp hoặc Đã Đóng!'
                ))
        target = self[0]
        total_qty = sum(self.mapped('quantity'))
        total_gross = sum(self.mapped('gross_weight'))
        total_net = sum(self.mapped('net_weight'))
        for box in self[1:]:
            box.write({'state': 'cancelled'})
        target.write({
            'quantity': total_qty,
            'gross_weight': total_gross,
            'net_weight': total_net,
            'state': 'packed',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'garment.carton.box',
            'res_id': target.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_split_carton(self):
        """Split a carton into two equal parts."""
        self.ensure_one()
        if self.state not in ('draft', 'packed'):
            raise UserError(_(
                'Chỉ tách được thùng ở trạng thái Nháp hoặc Đã Đóng!'
            ))
        if self.quantity < 2:
            raise UserError(_('Thùng phải có ít nhất 2 cái để tách!'))

        half_qty = self.quantity // 2
        remaining = self.quantity - half_qty
        half_weight_gross = (self.gross_weight / self.quantity * half_qty) if self.quantity else 0
        half_weight_net = (self.net_weight / self.quantity * half_qty) if self.quantity else 0

        new_box = self.copy({
            'quantity': half_qty,
            'gross_weight': half_weight_gross,
            'net_weight': half_weight_net,
            'state': 'packed',
            'pallet_id': False,
        })
        self.write({
            'quantity': remaining,
            'gross_weight': self.gross_weight - half_weight_gross,
            'net_weight': self.net_weight - half_weight_net,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Thùng Mới Từ Tách'),
            'res_model': 'garment.carton.box',
            'res_id': new_box.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_generate_label(self):
        """Generate QR label for this carton."""
        self.ensure_one()
        if self.qr_label_id:
            raise UserError(_('Thùng này đã có tem QR!'))
        label = self.env['garment.label'].create({
            'label_type': 'carton',
            'garment_order_id': self.garment_order_id.id,
            'carton_id': self.id,
            'packing_list_id': self.packing_list_id.id,
            'quantity': self.quantity,
            'description': '%s | %s | %s | %d pcs' % (
                self.style_code or '', self.color or '',
                self.size or '', self.quantity,
            ),
        })
        self.qr_label_id = label
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'garment.label',
            'res_id': label.id,
            'view_mode': 'form',
            'target': 'current',
        }
