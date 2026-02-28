from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentCrmFeedback(models.Model):
    _name = 'garment.crm.feedback'
    _description = 'Phản Hồi / Khiếu Nại Khách Hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Tiêu Đề',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Phản Hồi',
        copy=False,
        readonly=True,
        default='New',
    )
    feedback_type = fields.Selection([
        ('feedback', 'Phản Hồi'),
        ('complaint', 'Khiếu Nại'),
        ('suggestion', 'Đề Xuất'),
        ('praise', 'Khen Ngợi'),
    ], string='Loại', required=True, default='feedback', tracking=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng',
        required=True,
        tracking=True,
        domain=[('customer_rank', '>', 0)],
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng Liên Quan',
    )
    date = fields.Date(
        string='Ngày Nhận',
        default=fields.Date.today,
        required=True,
    )

    # --- Category ---
    category = fields.Selection([
        ('quality', 'Chất Lượng'),
        ('delivery', 'Giao Hàng'),
        ('packaging', 'Đóng Gói'),
        ('communication', 'Giao Tiếp'),
        ('price', 'Giá Cả'),
        ('service', 'Dịch Vụ'),
        ('other', 'Khác'),
    ], string='Danh Mục', required=True, tracking=True)

    severity = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung Bình'),
        ('high', 'Cao'),
        ('critical', 'Nghiêm Trọng'),
    ], string='Mức Độ', default='medium', tracking=True)

    description = fields.Html(
        string='Nội Dung Chi Tiết',
        required=True,
    )

    # --- Resolution ---
    assigned_to = fields.Many2one(
        'res.users',
        string='Người Xử Lý',
        tracking=True,
    )
    resolution = fields.Html(string='Biện Pháp Xử Lý')
    resolution_date = fields.Date(string='Ngày Giải Quyết')

    # --- Follow-up ---
    follow_up_date = fields.Date(string='Ngày Theo Dõi Tiếp')
    follow_up_notes = fields.Text(string='Ghi Chú Theo Dõi')

    satisfaction_rating = fields.Selection([
        ('1', '★ Rất Không Hài Lòng'),
        ('2', '★★ Không Hài Lòng'),
        ('3', '★★★ Bình Thường'),
        ('4', '★★★★ Hài Lòng'),
        ('5', '★★★★★ Rất Hài Lòng'),
    ], string='Đánh Giá Hài Lòng')

    state = fields.Selection([
        ('draft', 'Mới'),
        ('processing', 'Đang Xử Lý'),
        ('resolved', 'Đã Giải Quyết'),
        ('closed', 'Đã Đóng'),
    ], string='Trạng Thái', default='draft', tracking=True)

    # --- Computed ---
    days_open = fields.Integer(
        string='Số Ngày Mở',
        compute='_compute_days_open',
    )
    resolution_days = fields.Integer(
        string='Thời Gian Xử Lý (Ngày)',
        compute='_compute_resolution_days',
    )
    is_overdue = fields.Boolean(
        string='Quá Hạn Theo Dõi',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )

    @api.depends('date', 'state')
    def _compute_days_open(self):
        today = fields.Date.today()
        for fb in self:
            if fb.date and fb.state in ('draft', 'processing'):
                fb.days_open = (today - fb.date).days
            else:
                fb.days_open = 0

    @api.depends('date', 'resolution_date')
    def _compute_resolution_days(self):
        for fb in self:
            if fb.date and fb.resolution_date:
                fb.resolution_days = (fb.resolution_date - fb.date).days
            else:
                fb.resolution_days = 0

    @api.depends('follow_up_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for fb in self:
            fb.is_overdue = (
                fb.follow_up_date
                and fb.follow_up_date < today
                and fb.state in ('draft', 'processing')
            )

    def _search_is_overdue(self, operator, value):
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                '&',
                ('follow_up_date', '<', today),
                ('state', 'in', ['draft', 'processing']),
            ]
        return [
            '|',
            ('follow_up_date', '>=', today),
            ('follow_up_date', '=', False),
        ]

    # --- Constraints ---
    @api.constrains('satisfaction_rating')
    def _check_satisfaction_rating(self):
        for fb in self:
            if fb.satisfaction_rating and fb.satisfaction_rating not in ('1', '2', '3', '4', '5'):
                raise ValidationError(_('Đánh giá hài lòng phải từ 1 đến 5.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'garment.crm.feedback'
                ) or 'New'
        return super().create(vals_list)

    def action_process(self):
        for rec in self:
            if not rec.assigned_to:
                raise UserError(_('Vui lòng chọn người xử lý trước!'))
        self.write({'state': 'processing'})

    def action_resolve(self):
        for rec in self:
            if not rec.resolution:
                raise UserError(_('Vui lòng nhập biện pháp xử lý!'))
        self.write({
            'state': 'resolved',
            'resolution_date': fields.Date.today(),
        })

    def action_close(self):
        self.write({'state': 'closed'})

    def action_reopen(self):
        self.write({'state': 'processing', 'resolution_date': False})
