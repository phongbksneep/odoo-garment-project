from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentFinishingOrder(models.Model):
    _name = 'garment.finishing.order'
    _description = 'Lệnh Hoàn Thiện'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Số Lệnh',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
        required=True,
        tracking=True,
    )
    garment_order_id = fields.Many2one(
        related='production_order_id.garment_order_id',
        store=True,
        readonly=True,
    )
    style_id = fields.Many2one(
        related='production_order_id.style_id',
        store=True,
        readonly=True,
    )
    customer_id = fields.Many2one(
        related='production_order_id.customer_id',
        store=True,
        readonly=True,
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền Hoàn Thiện',
        domain="[('line_type', '=', 'finishing')]",
    )
    date_start = fields.Date(string='Ngày Bắt Đầu')
    date_end = fields.Date(string='Ngày Kết Thúc Dự Kiến')
    date_done = fields.Date(string='Ngày Hoàn Thành Thực Tế')

    qty_received = fields.Integer(
        string='SL Nhận Từ May',
        help='Số lượng bán thành phẩm nhận từ chuyền may',
    )
    task_ids = fields.One2many(
        'garment.finishing.task',
        'finishing_order_id',
        string='Công Việc Hoàn Thiện',
    )

    # --- Aggregated counts ---
    qty_thread_cut = fields.Integer(
        string='Đã Cắt Chỉ',
        compute='_compute_task_summary',
        store=True,
    )
    qty_pressed = fields.Integer(
        string='Đã Ủi',
        compute='_compute_task_summary',
        store=True,
    )
    qty_tagged = fields.Integer(
        string='Đã Đóng Tag',
        compute='_compute_task_summary',
        store=True,
    )
    qty_folded = fields.Integer(
        string='Đã Gấp Xếp',
        compute='_compute_task_summary',
        store=True,
    )
    qty_passed_qc = fields.Integer(
        string='QC Đạt',
        compute='_compute_task_summary',
        store=True,
    )
    qty_defect = fields.Integer(
        string='Lỗi Phát Hiện',
        compute='_compute_task_summary',
        store=True,
    )
    completion_rate = fields.Float(
        string='Tỷ Lệ Hoàn Thành (%)',
        compute='_compute_completion',
        store=True,
    )
    quality_pass_rate = fields.Float(
        string='Tỷ Lệ QC Đạt (%)',
        compute='_compute_quality_pass_rate',
        store=True,
    )
    is_overdue = fields.Boolean(
        string='Quá Hạn',
        compute='_compute_is_overdue',
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('in_progress', 'Đang Hoàn Thiện'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Html(string='Ghi Chú')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.finishing.order') or _('New')
        return super().create(vals_list)

    @api.depends('task_ids.task_type', 'task_ids.qty_done', 'task_ids.qty_defect')
    def _compute_task_summary(self):
        for order in self:
            tasks = order.task_ids
            order.qty_thread_cut = sum(
                t.qty_done for t in tasks if t.task_type == 'thread_cut')
            order.qty_pressed = sum(
                t.qty_done for t in tasks if t.task_type == 'pressing')
            order.qty_tagged = sum(
                t.qty_done for t in tasks if t.task_type == 'tagging')
            order.qty_folded = sum(
                t.qty_done for t in tasks if t.task_type == 'folding')
            order.qty_passed_qc = sum(
                t.qty_done for t in tasks if t.task_type == 'qc_check')
            order.qty_defect = sum(t.qty_defect for t in tasks)

    @api.depends('qty_received', 'qty_folded')
    def _compute_completion(self):
        for order in self:
            if order.qty_received > 0:
                order.completion_rate = (
                    order.qty_folded / order.qty_received) * 100
            else:
                order.completion_rate = 0.0

    @api.depends('qty_received', 'qty_passed_qc')
    def _compute_quality_pass_rate(self):
        for order in self:
            if order.qty_received > 0:
                order.quality_pass_rate = (
                    order.qty_passed_qc / order.qty_received) * 100
            else:
                order.quality_pass_rate = 0.0

    @api.depends('date_end', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for order in self:
            if order.date_end and order.state in ('confirmed', 'in_progress'):
                order.is_overdue = today > order.date_end
            else:
                order.is_overdue = False

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({
            'state': 'in_progress',
            'date_start': fields.Date.today(),
        })

    def action_done(self):
        self.write({
            'state': 'done',
            'date_done': fields.Date.today(),
        })

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Không thể hủy lệnh đã hoàn thành.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentFinishingTask(models.Model):
    _name = 'garment.finishing.task'
    _description = 'Công Việc Hoàn Thiện'
    _order = 'date desc, task_type'

    finishing_order_id = fields.Many2one(
        'garment.finishing.order',
        string='Lệnh Hoàn Thiện',
        required=True,
        ondelete='cascade',
    )
    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    task_type = fields.Selection([
        ('thread_cut', 'Cắt Chỉ'),
        ('pressing', 'Ủi'),
        ('tagging', 'Đóng Tag / Nhãn'),
        ('folding', 'Gấp Xếp'),
        ('qc_check', 'Kiểm Hàng'),
    ], string='Công Việc', required=True)

    employee_id = fields.Many2one(
        'hr.employee',
        string='Công Nhân',
    )
    qty_done = fields.Integer(
        string='Số Lượng Hoàn Thành',
        required=True,
    )
    qty_defect = fields.Integer(
        string='Số Lượng Lỗi',
        default=0,
    )
    notes = fields.Char(string='Ghi Chú')

    _qty_positive = models.Constraint(
        'CHECK(qty_done >= 0)',
        'Số lượng hoàn thành phải >= 0!',
    )
