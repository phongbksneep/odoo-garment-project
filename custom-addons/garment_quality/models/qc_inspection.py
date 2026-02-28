from odoo import models, fields, api


class GarmentQCInspection(models.Model):
    _name = 'garment.qc.inspection'
    _description = 'Kiểm Tra Chất Lượng'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'garment.audit.mixin']
    _order = 'create_date desc'

    def _audit_tracked_fields(self):
        return ['inspection_type', 'result', 'state', 'inspected_qty',
                'passed_qty', 'failed_qty']

    name = fields.Char(
        string='Số Phiếu QC',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    inspection_type = fields.Selection([
        ('inline', 'QC Inline (Trên Chuyền)'),
        ('endline', 'QC Endline (Cuối Chuyền)'),
        ('final', 'QC Final (Kiểm Cuối)'),
        ('aql', 'AQL Inspection'),
        ('fabric', 'Kiểm Vải'),
        ('accessory', 'Kiểm Phụ Liệu'),
    ], string='Loại Kiểm Tra', required=True, tracking=True)

    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mẫu May',
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
    )
    inspector_id = fields.Many2one(
        'hr.employee',
        string='Người Kiểm Tra (QC)',
        required=True,
    )
    inspection_date = fields.Datetime(
        string='Ngày Giờ Kiểm Tra',
        default=fields.Datetime.now,
    )

    # AQL Fields
    aql_level = fields.Selection([
        ('1.0', 'AQL 1.0'),
        ('1.5', 'AQL 1.5'),
        ('2.5', 'AQL 2.5'),
        ('4.0', 'AQL 4.0'),
        ('6.5', 'AQL 6.5'),
    ], string='Mức AQL', default='2.5')

    lot_size = fields.Integer(
        string='Kích Thước Lô',
    )
    sample_size = fields.Integer(
        string='Kích Thước Mẫu',
    )
    inspected_qty = fields.Integer(
        string='Số Lượng Kiểm',
        required=True,
    )
    passed_qty = fields.Integer(
        string='Đạt',
    )
    failed_qty = fields.Integer(
        string='Không Đạt',
        compute='_compute_failed_qty',
        store=True,
    )
    pass_rate = fields.Float(
        string='Tỷ Lệ Đạt (%)',
        compute='_compute_pass_rate',
        store=True,
    )

    defect_line_ids = fields.One2many(
        'garment.qc.defect.line',
        'inspection_id',
        string='Chi Tiết Lỗi',
    )
    total_defects = fields.Integer(
        string='Tổng Số Lỗi',
        compute='_compute_total_defects',
        store=True,
    )
    minor_defects = fields.Integer(
        string='Lỗi Nhẹ',
        compute='_compute_defect_summary',
        store=True,
    )
    major_defects = fields.Integer(
        string='Lỗi Nặng',
        compute='_compute_defect_summary',
        store=True,
    )
    critical_defects = fields.Integer(
        string='Lỗi Nghiêm Trọng',
        compute='_compute_defect_summary',
        store=True,
    )

    result = fields.Selection([
        ('pass', 'ĐẠT (Pass)'),
        ('fail', 'KHÔNG ĐẠT (Fail)'),
        ('pending', 'Chờ Xử Lý'),
    ], string='Kết Quả', tracking=True)

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang Kiểm'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Html(string='Ghi Chú / Nhận Xét')
    corrective_actions = fields.Html(string='Biện Pháp Khắc Phục')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('garment.qc.inspection') or 'New'
        return super().create(vals_list)

    @api.depends('inspected_qty', 'passed_qty')
    def _compute_failed_qty(self):
        for rec in self:
            rec.failed_qty = rec.inspected_qty - rec.passed_qty

    @api.depends('inspected_qty', 'passed_qty')
    def _compute_pass_rate(self):
        for rec in self:
            if rec.inspected_qty:
                rec.pass_rate = (rec.passed_qty / rec.inspected_qty) * 100
            else:
                rec.pass_rate = 0.0

    @api.depends('defect_line_ids.quantity')
    def _compute_total_defects(self):
        for rec in self:
            rec.total_defects = sum(rec.defect_line_ids.mapped('quantity'))

    @api.depends('defect_line_ids.quantity', 'defect_line_ids.severity')
    def _compute_defect_summary(self):
        for rec in self:
            rec.minor_defects = sum(
                rec.defect_line_ids.filtered(lambda l: l.severity == 'minor').mapped('quantity')
            )
            rec.major_defects = sum(
                rec.defect_line_ids.filtered(lambda l: l.severity == 'major').mapped('quantity')
            )
            rec.critical_defects = sum(
                rec.defect_line_ids.filtered(lambda l: l.severity == 'critical').mapped('quantity')
            )

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class GarmentQCDefectLine(models.Model):
    _name = 'garment.qc.defect.line'
    _description = 'Chi Tiết Lỗi QC'
    _order = 'inspection_id, defect_type_id'

    inspection_id = fields.Many2one(
        'garment.qc.inspection',
        string='Phiếu QC',
        required=True,
        ondelete='cascade',
    )
    defect_type_id = fields.Many2one(
        'garment.defect.type',
        string='Loại Lỗi',
        required=True,
    )
    severity = fields.Selection(
        related='defect_type_id.severity',
        store=True,
        string='Mức Độ',
    )
    quantity = fields.Integer(
        string='Số Lượng',
        required=True,
        default=1,
    )
    location = fields.Char(
        string='Vị Trí Lỗi',
        help='VD: Cổ áo, Tay trái, Lai quần...',
    )
    notes = fields.Char(
        string='Ghi Chú',
    )
