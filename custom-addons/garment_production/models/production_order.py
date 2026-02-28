from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GarmentProductionOrder(models.Model):
    _name = 'garment.production.order'
    _description = 'Lệnh Sản Xuất May'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'garment.audit.mixin']
    _order = 'create_date desc'

    def _audit_tracked_fields(self):
        return ['garment_order_id', 'sewing_line_id', 'state', 'planned_qty']

    name = fields.Char(
        string='Số Lệnh SX',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
        required=True,
        tracking=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
        related='garment_order_id.style_id',
        store=True,
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng',
        related='garment_order_id.customer_id',
        store=True,
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
        tracking=True,
    )
    planned_qty = fields.Integer(
        string='Số Lượng Kế Hoạch',
        required=True,
    )
    completed_qty = fields.Integer(
        string='Số Lượng Hoàn Thành',
        compute='_compute_completed_qty',
        store=True,
    )
    defect_qty = fields.Integer(
        string='Số Lượng Lỗi',
        compute='_compute_defect_qty',
        store=True,
    )
    completion_rate = fields.Float(
        string='Tỷ Lệ Hoàn Thành (%)',
        compute='_compute_completion_rate',
        store=True,
    )
    start_date = fields.Date(
        string='Ngày Bắt Đầu',
        tracking=True,
    )
    end_date = fields.Date(
        string='Ngày Kết Thúc Dự Kiến',
        tracking=True,
    )
    actual_end_date = fields.Date(
        string='Ngày Kết Thúc Thực Tế',
    )
    sam = fields.Float(
        string='SAM',
        related='style_id.sam',
    )
    daily_output_ids = fields.One2many(
        'garment.daily.output',
        'production_order_id',
        string='Sản Lượng Hàng Ngày',
    )
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('in_progress', 'Đang Sản Xuất'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Html(string='Ghi Chú')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('garment.production.order') or 'New'
        return super().create(vals_list)

    @api.depends('daily_output_ids.output_qty')
    def _compute_completed_qty(self):
        for order in self:
            order.completed_qty = sum(order.daily_output_ids.mapped('output_qty'))

    @api.depends('daily_output_ids.defect_qty')
    def _compute_defect_qty(self):
        for order in self:
            order.defect_qty = sum(order.daily_output_ids.mapped('defect_qty'))

    @api.depends('planned_qty', 'completed_qty')
    def _compute_completion_rate(self):
        for order in self:
            if order.planned_qty:
                order.completion_rate = (order.completed_qty / order.planned_qty) * 100
            else:
                order.completion_rate = 0.0

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({
            'state': 'in_progress',
            'start_date': fields.Date.today(),
        })

    def action_done(self):
        self.write({
            'state': 'done',
            'actual_end_date': fields.Date.today(),
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
