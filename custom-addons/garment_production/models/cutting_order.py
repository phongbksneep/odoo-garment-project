from odoo import models, fields, api


class GarmentCuttingOrder(models.Model):
    _name = 'garment.cutting.order'
    _description = 'Lệnh Cắt'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Số Lệnh Cắt',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
        required=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng',
        related='production_order_id.garment_order_id',
        store=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
        related='production_order_id.style_id',
        store=True,
    )
    fabric_id = fields.Many2one(
        'garment.fabric',
        string='Loại Vải',
        required=True,
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Màu',
    )
    planned_qty = fields.Integer(
        string='Số Lượng Cắt (sp)',
        required=True,
    )
    layers = fields.Integer(
        string='Số Lớp Vải',
        help='Số lớp vải xếp chồng khi cắt',
        default=1,
    )
    fabric_length = fields.Float(
        string='Chiều Dài Vải Sử Dụng (m)',
        digits=(12, 2),
    )
    fabric_width = fields.Float(
        string='Khổ Vải (cm)',
        related='fabric_id.width',
    )
    fabric_consumption = fields.Float(
        string='Định Mức Vải / SP (m)',
        related='style_id.fabric_consumption',
    )
    total_fabric = fields.Float(
        string='Tổng Vải Cần (m)',
        compute='_compute_total_fabric',
        store=True,
        digits=(12, 2),
    )
    waste_percentage = fields.Float(
        string='Hao Hụt (%)',
        default=5.0,
    )
    cutting_date = fields.Date(
        string='Ngày Cắt',
        default=fields.Date.today,
    )
    cutter_id = fields.Many2one(
        'hr.employee',
        string='Người Cắt',
    )
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('cutting', 'Đang Cắt'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi Chú')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('garment.cutting.order') or 'New'
        return super().create(vals_list)

    @api.depends('planned_qty', 'fabric_consumption', 'waste_percentage')
    def _compute_total_fabric(self):
        for order in self:
            base = order.planned_qty * order.fabric_consumption
            waste = base * (order.waste_percentage / 100)
            order.total_fabric = base + waste

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start_cutting(self):
        self.write({'state': 'cutting'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
