from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentComplianceAudit(models.Model):
    _name = 'garment.compliance.audit'
    _description = 'Compliance Audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'audit_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    audit_type = fields.Selection([
        ('bsci', 'BSCI'),
        ('wrap', 'WRAP'),
        ('sedex', 'SEDEX/SMETA'),
        ('sa8000', 'SA8000'),
        ('oeko_tex', 'OEKO-TEX'),
        ('gots', 'GOTS'),
        ('iso9001', 'ISO 9001'),
        ('iso14001', 'ISO 14001'),
        ('buyer', 'Buyer Audit'),
        ('internal', 'Nội Bộ'),
        ('other', 'Khác'),
    ], string='Loại Audit', required=True, default='bsci')

    audit_date = fields.Date(
        string='Ngày Audit',
        required=True,
    )
    expiry_date = fields.Date(string='Ngày Hết Hạn')
    auditor = fields.Char(string='Auditor / Tổ Chức')
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer (nếu có)',
        domain=[('customer_rank', '>', 0)],
    )

    # --- Results ---
    overall_rating = fields.Selection([
        ('a', 'A - Xuất Sắc'),
        ('b', 'B - Tốt'),
        ('c', 'C - Đạt'),
        ('d', 'D - Cần Cải Thiện'),
        ('e', 'E - Không Đạt'),
    ], string='Xếp Hạng', tracking=True)

    total_findings = fields.Integer(
        string='Tổng Phát Hiện',
        compute='_compute_findings',
    )
    critical_findings = fields.Integer(
        string='Lỗi Nghiêm Trọng',
        compute='_compute_findings',
    )

    finding_ids = fields.One2many(
        'garment.audit.finding',
        'audit_id',
        string='Chi Tiết Phát Hiện',
    )
    cap_ids = fields.One2many(
        'garment.corrective.action',
        'audit_id',
        string='Kế Hoạch Khắc Phục',
    )

    # --- Documents ---
    certificate_file = fields.Binary(string='Chứng Chỉ / Báo Cáo')
    certificate_filename = fields.Char(string='Tên File')

    state = fields.Selection([
        ('scheduled', 'Đã Lên Lịch'),
        ('in_progress', 'Đang Audit'),
        ('completed', 'Hoàn Thành'),
        ('cap_required', 'Cần CAP'),
        ('closed', 'Đã Đóng'),
    ], string='Trạng Thái', default='scheduled', tracking=True)

    notes = fields.Text(string='Ghi Chú')

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.compliance.audit'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    def _compute_findings(self):
        for record in self:
            record.total_findings = len(record.finding_ids)
            record.critical_findings = len(
                record.finding_ids.filtered(
                    lambda f: f.severity == 'critical'
                )
            )

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_start(self):
        self.ensure_one()
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.ensure_one()
        if self.critical_findings > 0:
            self.write({'state': 'cap_required'})
        else:
            self.write({'state': 'completed'})

    def action_close(self):
        self.ensure_one()
        # Check all CAPs are closed
        open_caps = self.cap_ids.filtered(
            lambda c: c.state not in ('done', 'cancelled')
        )
        if open_caps:
            raise UserError(
                _('Vui lòng đóng tất cả CAP trước khi đóng audit. '
                  'Còn %d CAP chưa hoàn thành.') % len(open_caps)
            )
        self.write({'state': 'closed'})

    def action_create_cap(self):
        """Create CAP entries from critical/major findings."""
        self.ensure_one()
        for finding in self.finding_ids.filtered(
            lambda f: f.severity in ('critical', 'major') and not f.cap_id
        ):
            cap = self.env['garment.corrective.action'].create({
                'audit_id': self.id,
                'finding_id': finding.id,
                'description': finding.description,
                'severity': finding.severity,
            })
            finding.write({'cap_id': cap.id})
        return {
            'type': 'ir.actions.act_window',
            'name': _('CAP - %s') % self.name,
            'res_model': 'garment.corrective.action',
            'view_mode': 'list,form',
            'domain': [('audit_id', '=', self.id)],
        }


class GarmentAuditFinding(models.Model):
    _name = 'garment.audit.finding'
    _description = 'Audit Finding'
    _order = 'severity'

    audit_id = fields.Many2one(
        'garment.compliance.audit',
        string='Audit',
        required=True,
        ondelete='cascade',
    )
    category = fields.Selection([
        ('health_safety', 'An Toàn & Sức Khỏe'),
        ('labor', 'Lao Động'),
        ('wages', 'Tiền Lương & Giờ Làm'),
        ('environment', 'Môi Trường'),
        ('management', 'Hệ Thống Quản Lý'),
        ('chemical', 'Hóa Chất'),
        ('fire_safety', 'PCCC'),
        ('building', 'Cơ Sở Vật Chất'),
        ('discrimination', 'Phân Biệt Đối Xử'),
        ('child_labor', 'Lao Động Trẻ Em'),
        ('other', 'Khác'),
    ], string='Hạng Mục', required=True)

    severity = fields.Selection([
        ('critical', 'Nghiêm Trọng (Critical)'),
        ('major', 'Lớn (Major)'),
        ('minor', 'Nhỏ (Minor)'),
        ('observation', 'Quan Sát (Observation)'),
    ], string='Mức Độ', required=True, default='minor')

    description = fields.Text(
        string='Mô Tả',
        required=True,
    )
    evidence = fields.Text(string='Bằng Chứng')
    cap_id = fields.Many2one(
        'garment.corrective.action',
        string='CAP Liên Quan',
        readonly=True,
    )
