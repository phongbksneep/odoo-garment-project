from odoo import models, fields, api


class SewingLine(models.Model):
    _name = 'garment.sewing.line'
    _description = 'Chuyền May'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(
        string='Tên Chuyền',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Chuyền',
        required=True,
    )
    line_type = fields.Selection([
        ('sewing', 'Chuyền May'),
        ('cutting', 'Bàn Cắt'),
        ('finishing', 'Chuyền Hoàn Thiện'),
        ('ironing', 'Chuyền Ủi'),
        ('packing', 'Chuyền Đóng Gói'),
    ], string='Loại Chuyền', required=True, default='sewing')

    manager_id = fields.Many2one(
        'hr.employee',
        string='Chuyền Trưởng',
    )
    worker_ids = fields.Many2many(
        'hr.employee',
        string='Công Nhân',
    )
    worker_count = fields.Integer(
        string='Số Công Nhân',
        compute='_compute_worker_count',
        store=True,
    )
    machine_count = fields.Integer(
        string='Số Máy',
        default=0,
    )
    capacity_per_day = fields.Integer(
        string='Năng Suất / Ngày (sp)',
        help='Số sản phẩm dự kiến hoàn thành trong 1 ngày',
    )
    efficiency = fields.Float(
        string='Hiệu Suất (%)',
        default=80.0,
    )
    location = fields.Char(
        string='Vị Trí / Nhà Xưởng',
    )
    state = fields.Selection([
        ('active', 'Đang Hoạt Động'),
        ('maintenance', 'Đang Bảo Trì'),
        ('inactive', 'Ngừng Hoạt Động'),
    ], string='Trạng Thái', default='active', tracking=True)

    notes = fields.Text(
        string='Ghi Chú',
    )
    active = fields.Boolean(default=True)

    @api.depends('worker_ids')
    def _compute_worker_count(self):
        for line in self:
            line.worker_count = len(line.worker_ids)

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã chuyền phải là duy nhất!',
    )
