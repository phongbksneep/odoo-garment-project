from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentSample(models.Model):
    _name = 'garment.sample'
    _description = 'Quản Lý Mẫu May'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Style',
        required=True,
        tracking=True,
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        required=True,
        domain=[('customer_rank', '>', 0)],
    )
    sample_type = fields.Selection([
        ('proto', 'Proto Sample'),
        ('fit', 'Fit Sample'),
        ('size_set', 'Size Set Sample'),
        ('salesman', 'Salesman Sample'),
        ('pp', 'PP Sample'),
        ('top', 'TOP Sample'),
        ('shipment', 'Shipment Sample'),
        ('ad_hoc', 'Ad-hoc Sample'),
    ], string='Sample Type', required=True, tracking=True)

    quantity = fields.Integer(
        string='Quantity',
        default=1,
        required=True,
    )
    size_ids = fields.Many2many(
        'garment.size',
        string='Sizes',
    )
    color_ids = fields.Many2many(
        'garment.color',
        string='Colors',
    )

    # Dates
    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.today,
    )
    required_date = fields.Date(
        string='Required Date',
        required=True,
        tracking=True,
    )
    submission_date = fields.Date(
        string='Submission Date',
        tracking=True,
    )
    approval_date = fields.Date(
        string='Approval Date',
    )

    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )

    # Materials
    fabric_info = fields.Text(string='Fabric Information')
    material_notes = fields.Text(string='Material Notes')

    # Images
    image_front = fields.Binary(string='Front Image')
    image_back = fields.Binary(string='Back Image')
    image_detail = fields.Binary(string='Detail Image')

    # Comments
    comment_ids = fields.One2many(
        'garment.sample.comment',
        'sample_id',
        string='Comments',
    )
    comment_count = fields.Integer(
        string='Comments',
        compute='_compute_comment_count',
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang Làm'),
        ('submitted', 'Đã Gửi Buyer'),
        ('approved', 'Đã Duyệt'),
        ('approved_with_comments', 'Duyệt Có Chỉnh Sửa'),
        ('rejected', 'Bị Từ Chối'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    revision = fields.Integer(string='Revision', default=0, copy=False)
    courier_info = fields.Char(string='Courier / Tracking')
    notes = fields.Html(string='Notes')

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.sample'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('comment_ids')
    def _compute_comment_count(self):
        for record in self:
            record.comment_count = len(record.comment_ids)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_start(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft samples can be started.'))
        self.write({'state': 'in_progress'})

    def action_submit(self):
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_('Only in-progress samples can be submitted.'))
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.today(),
        })

    def action_approve(self):
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted samples can be approved.'))
        self.write({
            'state': 'approved',
            'approval_date': fields.Date.today(),
        })

    def action_approve_with_comments(self):
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted samples can be approved.'))
        self.write({
            'state': 'approved_with_comments',
            'approval_date': fields.Date.today(),
        })

    def action_reject(self):
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted samples can be rejected.'))
        self.write({'state': 'rejected'})

    def action_revise(self):
        """Create a new revision and restart workflow."""
        self.ensure_one()
        if self.state not in ('rejected', 'approved_with_comments'):
            raise UserError(_('Only rejected or conditionally approved samples can be revised.'))
        self.write({
            'state': 'in_progress',
            'revision': self.revision + 1,
            'submission_date': False,
            'approval_date': False,
        })

    def action_cancel(self):
        self.ensure_one()
        if self.state in ('approved', 'cancelled'):
            raise UserError(_('Cannot cancel an approved or already cancelled sample.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})


class GarmentSampleComment(models.Model):
    _name = 'garment.sample.comment'
    _description = 'Sample Comment / Buyer Feedback'
    _order = 'date desc'

    sample_id = fields.Many2one(
        'garment.sample',
        string='Sample',
        required=True,
        ondelete='cascade',
    )
    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
    )
    comment_type = fields.Selection([
        ('buyer', 'Buyer Comment'),
        ('internal', 'Internal Comment'),
        ('correction', 'Correction Required'),
    ], string='Type', default='buyer', required=True)
    comment = fields.Text(
        string='Comment',
        required=True,
    )
    image = fields.Binary(string='Attachment Image')
    revision = fields.Integer(
        related='sample_id.revision',
        store=True,
        string='Revision',
    )
