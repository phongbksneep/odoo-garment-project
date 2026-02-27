from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentPallet(models.Model):
    _name = 'garment.pallet'
    _description = 'Pallet'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Mã Pallet',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        index=True,
    )
    pallet_type = fields.Selection([
        ('standard', 'Pallet Chuẩn'),
        ('euro', 'Euro Pallet'),
        ('custom', 'Kích Thước Đặc Biệt'),
    ], string='Loại Pallet', default='standard')

    garment_order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng May')
    packing_list_id = fields.Many2one(
        'garment.packing.list', string='Packing List')

    # --- Dimensions ---
    length_cm = fields.Float(string='Dài (cm)', default=120)
    width_cm = fields.Float(string='Rộng (cm)', default=100)
    height_cm = fields.Float(string='Cao (cm)', default=150)
    max_weight = fields.Float(
        string='Trọng Tải Tối Đa (kg)',
        default=1000,
    )

    # --- Carton boxes on this pallet ---
    carton_box_ids = fields.One2many(
        'garment.carton.box',
        'pallet_id',
        string='Thùng Hàng Trên Pallet',
    )
    carton_count = fields.Integer(
        string='Số Thùng',
        compute='_compute_totals',
        store=True,
    )
    total_pcs = fields.Integer(
        string='Tổng Số Cái',
        compute='_compute_totals',
        store=True,
    )
    total_weight = fields.Float(
        string='Tổng Trọng Lượng (kg)',
        compute='_compute_totals',
        store=True,
        digits=(10, 2),
    )

    location = fields.Char(string='Vị Trí Kho')
    warehouse_zone = fields.Selection([
        ('finished', 'Kho Thành Phẩm'),
        ('shipping', 'Khu Xuất Hàng'),
        ('staging', 'Khu Tập Kết'),
    ], string='Khu Vực')

    notes = fields.Text(string='Ghi Chú')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('open', 'Đang Xếp'),
        ('closed', 'Đã Đóng'),
        ('shipped', 'Đã Xuất'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.pallet'
                ) or 'New'
        return super().create(vals_list)

    @api.depends('carton_box_ids', 'carton_box_ids.quantity',
                 'carton_box_ids.gross_weight')
    def _compute_totals(self):
        for pallet in self:
            boxes = pallet.carton_box_ids
            pallet.carton_count = len(boxes)
            pallet.total_pcs = sum(boxes.mapped('quantity'))
            pallet.total_weight = sum(boxes.mapped('gross_weight'))

    def action_open(self):
        self.write({'state': 'open'})

    def action_close(self):
        for pallet in self:
            if not pallet.carton_box_ids:
                raise UserError(_('Pallet phải có ít nhất 1 thùng hàng!'))
        self.write({'state': 'closed'})

    def action_ship(self):
        for pallet in self:
            if pallet.state != 'closed':
                raise UserError(_('Pallet phải đóng trước khi xuất!'))
        self.write({'state': 'shipped'})

    def action_cancel(self):
        for pallet in self:
            if pallet.state == 'shipped':
                raise UserError(_('Không thể hủy pallet đã xuất!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_merge_pallets(self):
        """Merge multiple pallets into one (self must have at least 2)."""
        if len(self) < 2:
            raise UserError(_('Cần chọn ít nhất 2 pallet để gộp!'))
        for pallet in self:
            if pallet.state not in ('draft', 'open'):
                raise UserError(_(
                    'Chỉ gộp được pallet ở trạng thái Nháp hoặc Đang Xếp!'
                ))
        target = self[0]
        for pallet in self[1:]:
            pallet.carton_box_ids.write({'pallet_id': target.id})
            pallet.write({'state': 'cancelled'})
        target.write({'state': 'open'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'garment.pallet',
            'res_id': target.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_split_pallet(self):
        """Split pallet: create a new pallet and move half the cartons."""
        self.ensure_one()
        if self.state not in ('draft', 'open'):
            raise UserError(_('Chỉ tách được pallet ở trạng thái Nháp hoặc Đang Xếp!'))
        boxes = self.carton_box_ids
        if len(boxes) < 2:
            raise UserError(_('Pallet phải có ít nhất 2 thùng để tách!'))

        half = len(boxes) // 2
        boxes_to_move = boxes[half:]

        new_pallet = self.copy({
            'carton_box_ids': False,
            'state': 'open',
        })
        boxes_to_move.write({'pallet_id': new_pallet.id})
        self.write({'state': 'open'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pallet Mới Từ Tách'),
            'res_model': 'garment.pallet',
            'res_id': new_pallet.id,
            'view_mode': 'form',
            'target': 'current',
        }
