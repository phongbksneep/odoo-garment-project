from odoo import models, fields, api, _


class GarmentBonus(models.Model):
    _name = 'garment.bonus'
    _description = 'Thưởng (Quý / Năm / Đột Xuất)'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(
        string='Mã Phiếu Thưởng',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    bonus_type = fields.Selection([
        ('quarterly', 'Thưởng Quý'),
        ('yearly', 'Thưởng Năm (Tết)'),
        ('productivity', 'Thưởng Năng Suất'),
        ('attendance', 'Thưởng Chuyên Cần'),
        ('quality', 'Thưởng Chất Lượng'),
        ('seniority', 'Thưởng Thâm Niên'),
        ('other', 'Thưởng Khác'),
    ], string='Loại Thưởng', required=True, default='quarterly')

    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    quarter = fields.Selection([
        ('q1', 'Quý 1'),
        ('q2', 'Quý 2'),
        ('q3', 'Quý 3'),
        ('q4', 'Quý 4'),
    ], string='Quý')
    year = fields.Integer(
        string='Năm',
        default=lambda self: fields.Date.today().year,
    )

    line_ids = fields.One2many(
        'garment.bonus.line',
        'bonus_id',
        string='Chi Tiết Thưởng',
    )
    total_amount = fields.Float(
        string='Tổng Tiền Thưởng',
        compute='_compute_total',
        store=True,
        digits=(12, 0),
    )
    reason = fields.Text(string='Lý Do / Ghi Chú')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('paid', 'Đã Chi'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.bonus') or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('amount'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_pay(self):
        self.write({'state': 'paid'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GarmentBonusLine(models.Model):
    _name = 'garment.bonus.line'
    _description = 'Chi Tiết Thưởng'
    _order = 'employee_id'

    bonus_id = fields.Many2one(
        'garment.bonus',
        string='Phiếu Thưởng',
        required=True,
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        required=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    amount = fields.Float(
        string='Số Tiền Thưởng (VNĐ)',
        required=True,
        digits=(12, 0),
    )
    rating = fields.Selection([
        ('a', 'A - Xuất Sắc'),
        ('b', 'B - Tốt'),
        ('c', 'C - Trung Bình'),
        ('d', 'D - Yếu'),
    ], string='Xếp Loại')
    notes = fields.Char(string='Ghi Chú')
