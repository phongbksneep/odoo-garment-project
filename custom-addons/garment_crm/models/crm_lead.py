from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentCrmLead(models.Model):
    _name = 'garment.crm.lead'
    _description = 'Lead / Cơ Hội Kinh Doanh'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(
        string='Tiêu Đề',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Lead',
        copy=False,
        readonly=True,
        default='New',
    )
    lead_type = fields.Selection([
        ('lead', 'Lead (Đầu Mối)'),
        ('opportunity', 'Cơ Hội'),
    ], string='Loại', default='lead', required=True, tracking=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng',
        tracking=True,
        domain=[('customer_rank', '>', 0)],
    )
    contact_name = fields.Char(string='Người Liên Hệ')
    contact_email = fields.Char(string='Email')
    contact_phone = fields.Char(string='Điện Thoại')
    company_name = fields.Char(string='Tên Công Ty')
    country_id = fields.Many2one('res.country', string='Quốc Gia')

    # --- Business info ---
    product_category = fields.Selection([
        ('shirt', 'Áo Sơ Mi'),
        ('tshirt', 'Áo Thun / T-Shirt'),
        ('polo', 'Áo Polo'),
        ('jacket', 'Áo Khoác / Jacket'),
        ('pants', 'Quần'),
        ('dress', 'Đầm / Váy'),
        ('uniform', 'Đồng Phục'),
        ('sportswear', 'Đồ Thể Thao'),
        ('childwear', 'Đồ Trẻ Em'),
        ('other', 'Khác'),
    ], string='Loại Sản Phẩm Quan Tâm')

    expected_qty = fields.Integer(string='Số Lượng Dự Kiến')
    expected_revenue = fields.Float(
        string='Doanh Thu Dự Kiến',
        digits='Product Price',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        default=lambda self: self.env.company.currency_id,
    )
    expected_close_date = fields.Date(string='Ngày Dự Kiến Chốt')
    probability = fields.Float(
        string='Xác Suất (%)',
        default=10.0,
        tracking=True,
    )

    # --- Source ---
    source = fields.Selection([
        ('website', 'Website'),
        ('email', 'Email'),
        ('phone', 'Điện Thoại'),
        ('exhibition', 'Triển Lãm'),
        ('referral', 'Giới Thiệu'),
        ('social', 'Mạng Xã Hội'),
        ('agent', 'Đại Lý / Agent'),
        ('direct', 'Liên Hệ Trực Tiếp'),
        ('other', 'Khác'),
    ], string='Nguồn')

    salesperson_id = fields.Many2one(
        'res.users',
        string='Nhân Viên Phụ Trách',
        default=lambda self: self.env.user,
        tracking=True,
    )
    team = fields.Selection([
        ('domestic', 'Nội Địa'),
        ('export', 'Xuất Khẩu'),
        ('cmt', 'CMT'),
    ], string='Nhóm Kinh Doanh')

    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình Thường'),
        ('2', 'Cao'),
        ('3', 'Rất Cao'),
    ], string='Ưu Tiên', default='1')

    # --- Pipeline stage ---
    stage = fields.Selection([
        ('new', 'Mới'),
        ('qualified', 'Đã Đánh Giá'),
        ('proposal', 'Đã Gửi Báo Giá'),
        ('negotiation', 'Đang Thương Lượng'),
        ('won', 'Thành Công'),
        ('lost', 'Thất Bại'),
    ], string='Giai Đoạn', default='new', tracking=True)

    lost_reason = fields.Selection([
        ('price', 'Giá Cao'),
        ('quality', 'Chất Lượng Không Phù Hợp'),
        ('capacity', 'Không Đủ Năng Lực SX'),
        ('delivery', 'Thời Gian Giao Hàng'),
        ('competitor', 'Đối Thủ Cạnh Tranh'),
        ('other', 'Khác'),
    ], string='Lý Do Thất Bại')

    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng Tạo Từ CRM',
        readonly=True,
    )

    notes = fields.Html(string='Ghi Chú')

    # --- Computed ---
    weighted_revenue = fields.Float(
        string='Doanh Thu Kỳ Vọng',
        compute='_compute_weighted_revenue',
        store=True,
        digits='Product Price',
        help='Doanh thu dự kiến × Xác suất',
    )
    days_in_pipeline = fields.Integer(
        string='Số Ngày Trong Pipeline',
        compute='_compute_days_in_pipeline',
    )
    is_overdue = fields.Boolean(
        string='Quá Hạn',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )

    @api.depends('expected_revenue', 'probability')
    def _compute_weighted_revenue(self):
        for lead in self:
            lead.weighted_revenue = (lead.expected_revenue or 0.0) * (lead.probability or 0.0) / 100.0

    @api.depends_context('uid')
    def _compute_days_in_pipeline(self):
        today = fields.Date.today()
        for lead in self:
            if lead.create_date:
                lead.days_in_pipeline = (today - lead.create_date.date()).days
            else:
                lead.days_in_pipeline = 0

    @api.depends('expected_close_date', 'stage')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for lead in self:
            lead.is_overdue = (
                lead.expected_close_date
                and lead.expected_close_date < today
                and lead.stage not in ('won', 'lost')
            )

    def _search_is_overdue(self, operator, value):
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                '&',
                ('expected_close_date', '<', today),
                ('stage', 'not in', ['won', 'lost']),
            ]
        return [
            '|',
            ('expected_close_date', '>=', today),
            ('expected_close_date', '=', False),
        ]

    # --- Constraints ---
    @api.constrains('expected_qty')
    def _check_expected_qty(self):
        for lead in self:
            if lead.expected_qty and lead.expected_qty < 0:
                raise ValidationError(_('Số lượng dự kiến không được âm.'))

    @api.constrains('expected_revenue')
    def _check_expected_revenue(self):
        for lead in self:
            if lead.expected_revenue and lead.expected_revenue < 0:
                raise ValidationError(_('Doanh thu dự kiến không được âm.'))

    @api.constrains('probability')
    def _check_probability(self):
        for lead in self:
            if lead.probability < 0 or lead.probability > 100:
                raise ValidationError(_('Xác suất phải từ 0 đến 100.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'garment.crm.lead'
                ) or 'New'
        return super().create(vals_list)

    def action_convert_opportunity(self):
        """Convert lead to opportunity."""
        for lead in self:
            if lead.lead_type == 'opportunity':
                raise UserError(_('Đây đã là Cơ Hội!'))
            lead.write({
                'lead_type': 'opportunity',
                'stage': 'qualified',
            })

    def action_qualify(self):
        self.write({'stage': 'qualified'})

    def action_propose(self):
        self.write({'stage': 'proposal'})

    def action_negotiate(self):
        self.write({'stage': 'negotiation'})

    def action_won(self):
        self.write({'stage': 'won', 'probability': 100.0})

    def action_lost(self):
        self.write({'stage': 'lost', 'probability': 0.0})

    def action_reset(self):
        self.write({'stage': 'new', 'lost_reason': False})

    def action_create_order(self):
        """Create garment order from won opportunity."""
        self.ensure_one()
        if self.stage != 'won':
            raise UserError(_('Chỉ tạo đơn hàng từ cơ hội Thành Công!'))
        if self.garment_order_id:
            raise UserError(_('Đã tạo đơn hàng cho cơ hội này!'))
        if not self.partner_id:
            raise UserError(_('Phải có khách hàng trước khi tạo đơn hàng!'))

        # Find or create a default style
        style = self.env['garment.style'].search([], limit=1)
        if not style:
            raise UserError(_('Chưa có mẫu may nào, vui lòng tạo mẫu may trước!'))

        order = self.env['garment.order'].create({
            'customer_id': self.partner_id.id,
            'style_id': style.id,
            'notes': _('Tạo từ CRM: %s', self.name),
        })
        self.garment_order_id = order
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'garment.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }
