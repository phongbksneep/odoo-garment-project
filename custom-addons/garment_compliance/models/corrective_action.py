from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentCorrectiveAction(models.Model):
    _name = 'garment.corrective.action'
    _description = 'Corrective Action Plan (CAP)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'deadline'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    audit_id = fields.Many2one(
        'garment.compliance.audit',
        string='Audit',
        required=True,
    )
    finding_id = fields.Many2one(
        'garment.audit.finding',
        string='Phát Hiện Liên Quan',
    )
    severity = fields.Selection([
        ('critical', 'Nghiêm Trọng'),
        ('major', 'Lớn'),
        ('minor', 'Nhỏ'),
    ], string='Mức Độ')

    description = fields.Text(
        string='Mô Tả Vấn Đề',
        required=True,
    )
    root_cause = fields.Text(string='Nguyên Nhân Gốc')
    corrective_action = fields.Text(string='Hành Động Khắc Phục')
    preventive_action = fields.Text(string='Hành Động Phòng Ngừa')

    responsible_id = fields.Many2one(
        'hr.employee',
        string='Người Phụ Trách',
    )
    deadline = fields.Date(string='Hạn Hoàn Thành')
    completion_date = fields.Date(string='Ngày Hoàn Thành')

    # Evidence
    evidence_file = fields.Binary(string='Bằng Chứng Khắc Phục')
    evidence_filename = fields.Char(string='Tên File')

    state = fields.Selection([
        ('open', 'Mở'),
        ('in_progress', 'Đang Xử Lý'),
        ('submitted', 'Đã Nộp'),
        ('done', 'Đã Xác Minh'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='open', tracking=True)

    is_overdue = fields.Boolean(
        string='Quá Hạn',
        compute='_compute_is_overdue',
    )

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.corrective.action'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.deadline
                and record.deadline < today
                and record.state not in ('done', 'cancelled')
            )

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_start(self):
        self.ensure_one()
        self.write({'state': 'in_progress'})

    def action_submit(self):
        self.ensure_one()
        if not self.corrective_action:
            raise UserError(
                _('Vui lòng mô tả hành động khắc phục trước khi nộp.')
            )
        self.write({'state': 'submitted'})

    def action_verify(self):
        self.ensure_one()
        self.write({
            'state': 'done',
            'completion_date': fields.Date.today(),
        })

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})
