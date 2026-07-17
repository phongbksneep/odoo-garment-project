from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


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
        ondelete='restrict',
        string='Đơn Hàng May',
        required=True,
        index=True,
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
        index=True,
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
    is_overdue = fields.Boolean(
        string='Quá Hạn',
        compute='_compute_is_overdue',
        store=True,
    )
    delay_days = fields.Integer(
        string='Số Ngày Trễ',
        compute='_compute_is_overdue',
        store=True,
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

    @api.constrains('planned_qty', 'garment_order_id')
    def _check_planned_vs_order(self):
        """Tổng SL kế hoạch các lệnh SX không vượt SL đơn hàng
        (+ dung sai cấu hình, mặc định 5%)."""
        icp = self.env['ir.config_parameter'].sudo()
        try:
            tolerance = float(
                icp.get_param('garment_base.qty_tolerance_pct') or 5.0)
        except (TypeError, ValueError):
            tolerance = 5.0
        for order in self:
            g_order = order.garment_order_id
            if not g_order or not g_order.total_qty:
                continue
            siblings = self.search([
                ('garment_order_id', '=', g_order.id),
                ('state', '!=', 'cancelled'),
            ])
            total_planned = sum(siblings.mapped('planned_qty'))
            cap = g_order.total_qty * (1 + tolerance / 100)
            if total_planned > cap:
                raise ValidationError(
                    'Tổng SL kế hoạch (%d) vượt SL đơn hàng %s (%d, dung '
                    'sai %.0f%%). Kiểm tra lại các lệnh sản xuất.'
                    % (total_planned, g_order.name, g_order.total_qty,
                       tolerance))

    @api.constrains('planned_qty')
    def _check_planned_qty(self):
        for order in self:
            if order.planned_qty <= 0:
                raise ValidationError('Số lượng kế hoạch phải lớn hơn 0.')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for order in self:
            if order.start_date and order.end_date and order.end_date < order.start_date:
                raise ValidationError('Ngày kết thúc dự kiến phải sau ngày bắt đầu.')

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

    @api.depends('end_date', 'state', 'actual_end_date')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for order in self:
            if order.end_date and order.state in ('confirmed', 'in_progress'):
                delta = (today - order.end_date).days
                order.is_overdue = delta > 0
                order.delay_days = max(delta, 0)
            elif order.end_date and order.state == 'done' and order.actual_end_date:
                delta = (order.actual_end_date - order.end_date).days
                order.is_overdue = delta > 0
                order.delay_days = max(delta, 0)
            else:
                order.is_overdue = False
                order.delay_days = 0

    def action_confirm(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('Chỉ lệnh sản xuất Nháp mới được xác nhận.')
            if order.garment_order_id.state in ('draft', 'cancelled'):
                raise UserError(
                    'Không thể xác nhận lệnh sản xuất cho đơn hàng %s '
                    'chưa xác nhận hoặc đã hủy.'
                    % order.garment_order_id.name)
        self.write({'state': 'confirmed'})

    def action_start(self):
        for order in self:
            vals = {'state': 'in_progress'}
            if not order.start_date:
                vals['start_date'] = fields.Date.today()
            order.write(vals)

    def action_done(self):
        for order in self:
            if order.completed_qty <= 0:
                raise UserError(
                    'Lệnh sản xuất %s chưa có sản lượng — không thể '
                    'hoàn thành.' % order.name)
        self.write({
            'state': 'done',
            'actual_end_date': fields.Date.today(),
        })

    def action_cancel(self):
        for order in self:
            if order.state == 'done':
                raise UserError('Không thể hủy lệnh sản xuất đã hoàn thành.')
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
