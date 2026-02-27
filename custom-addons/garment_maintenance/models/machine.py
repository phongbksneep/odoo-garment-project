from odoo import models, fields, api, _


class GarmentMachine(models.Model):
    _name = 'garment.machine'
    _description = 'Sewing Machine'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(
        string='Mã Máy',
        required=True,
    )
    machine_type = fields.Selection([
        ('lockstitch', 'Máy 1 Kim (Lockstitch)'),
        ('overlock', 'Máy Vắt Sổ (Overlock)'),
        ('flatlock', 'Máy Bằng (Flatlock/Coverstitch)'),
        ('bartack', 'Máy Bọ (Bartack)'),
        ('buttonhole', 'Máy Khuy (Buttonhole)'),
        ('button_attach', 'Máy Đính Cúc (Button Attach)'),
        ('zigzag', 'Máy Zigzag'),
        ('cutting', 'Máy Cắt'),
        ('pressing', 'Máy Ủi / Ép'),
        ('other', 'Khác'),
    ], string='Loại Máy', required=True, default='lockstitch')

    brand = fields.Char(string='Hãng')
    model = fields.Char(string='Model')
    serial_number = fields.Char(string='Số Serial')
    purchase_date = fields.Date(string='Ngày Mua')
    warranty_expiry = fields.Date(string='Hết Bảo Hành')

    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
    )
    responsible_id = fields.Many2one(
        'hr.employee',
        string='Thợ Phụ Trách',
    )

    status = fields.Selection([
        ('active', 'Đang Hoạt Động'),
        ('maintenance', 'Đang Bảo Trì'),
        ('broken', 'Hư Hỏng'),
        ('retired', 'Ngưng Sử Dụng'),
    ], string='Trạng Thái', default='active', tracking=True)

    # Maintenance schedule
    maintenance_interval = fields.Integer(
        string='Chu Kỳ Bảo Trì (ngày)',
        default=30,
    )
    last_maintenance_date = fields.Date(string='Bảo Trì Gần Nhất')
    next_maintenance_date = fields.Date(
        string='Bảo Trì Tiếp',
        compute='_compute_next_maintenance',
        store=True,
    )

    maintenance_request_ids = fields.One2many(
        'garment.maintenance.request',
        'machine_id',
        string='Lịch Sử Bảo Trì',
    )
    total_requests = fields.Integer(
        string='Tổng Yêu Cầu',
        compute='_compute_total_requests',
    )

    notes = fields.Text(string='Ghi Chú')

    _serial_unique = models.Constraint(
        'UNIQUE(serial_number)',
        'Số serial phải là duy nhất!',
    )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('last_maintenance_date', 'maintenance_interval')
    def _compute_next_maintenance(self):
        for machine in self:
            if machine.last_maintenance_date and machine.maintenance_interval:
                machine.next_maintenance_date = fields.Date.add(
                    machine.last_maintenance_date,
                    days=machine.maintenance_interval,
                )
            else:
                machine.next_maintenance_date = False

    def _compute_total_requests(self):
        for machine in self:
            machine.total_requests = len(machine.maintenance_request_ids)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_view_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Yêu Cầu Bảo Trì - %s') % self.name,
            'res_model': 'garment.maintenance.request',
            'view_mode': 'list,form',
            'domain': [('machine_id', '=', self.id)],
        }
