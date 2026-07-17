from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentWorkerOutput(models.Model):
    _name = 'garment.worker.output'
    _description = 'Worker Daily Output'
    _order = 'date desc, employee_id'

    date = fields.Date(
        string='Ngày',
        required=True,
        index=True,
        default=fields.Date.today,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Công Nhân',
        required=True,
        index=True,
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mã Hàng',
        required=True,
    )
    piece_rate_id = fields.Many2one(
        'garment.piece.rate',
        string='Đơn Giá',
        domain="[('style_id', '=', style_id)]",
    )
    # operation & rate_per_piece là SNAPSHOT tại thời điểm ghi nhận
    # (compute chỉ depends piece_rate_id): sửa đơn giá gốc về sau KHÔNG
    # được viết lại lịch sử sản lượng/lương đã chốt.
    operation = fields.Selection([
        ('sewing', 'May'),
        ('cutting', 'Cắt'),
        ('finishing', 'Hoàn Tất'),
        ('pressing', 'Ủi'),
        ('packing', 'Đóng Gói'),
        ('qc', 'Kiểm Hàng'),
        ('other', 'Khác'),
    ], string='Công Đoạn',
        compute='_compute_from_piece_rate',
        store=True,
        readonly=False,
    )
    quantity = fields.Integer(
        string='Số Lượng',
        required=True,
    )
    rate_per_piece = fields.Float(
        string='Đơn Giá/SP',
        compute='_compute_from_piece_rate',
        store=True,
        readonly=False,
        digits=(10, 0),
    )

    @api.onchange('style_id')
    def _onchange_style_id(self):
        """Tự chọn đơn giá khi mã hàng chỉ có đúng 1 đơn giá khoán."""
        if self.style_id and not self.piece_rate_id:
            rates = self.env['garment.piece.rate'].search([
                ('style_id', '=', self.style_id.id),
            ])
            if len(rates) == 1:
                self.piece_rate_id = rates

    @api.depends('piece_rate_id')
    def _compute_from_piece_rate(self):
        for record in self:
            if record.piece_rate_id:
                record.operation = record.piece_rate_id.operation
                record.rate_per_piece = record.piece_rate_id.rate_per_piece
            else:
                record.operation = record.operation or False
                record.rate_per_piece = record.rate_per_piece or 0

    def _check_wage_not_locked(self):
        """Chặn sửa sản lượng khi phiếu lương tháng đó đã chốt/trả."""
        if self.env.context.get('install_mode'):
            return
        Wage = self.env['garment.wage.calculation']
        for record in self:
            if not record.date or not record.employee_id:
                continue
            locked = Wage.search_count([
                ('employee_id', '=', record.employee_id.id),
                ('month', '=', '%02d' % record.date.month),
                ('year', '=', record.date.year),
                ('state', 'in', ('confirmed', 'paid')),
            ])
            if locked:
                raise UserError(_(
                    'Không thể thêm/sửa/xóa sản lượng tháng %02d/%d của %s: '
                    'phiếu lương tháng này đã được xác nhận/trả.',
                    record.date.month, record.date.year,
                    record.employee_id.name))
    amount = fields.Float(
        string='Thành Tiền (VNĐ)',
        compute='_compute_amount',
        store=True,
        digits=(10, 0),
    )
    overtime_hours = fields.Float(
        string='Giờ Tăng Ca',
        digits=(10, 1),
    )
    notes = fields.Char(string='Ghi Chú')

    @api.depends('quantity', 'rate_per_piece')
    def _compute_amount(self):
        for record in self:
            record.amount = record.quantity * record.rate_per_piece

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_wage_not_locked()
        return records

    def write(self, vals):
        # Trường hệ thống ghi khi recompute không tính là sửa nghiệp vụ
        if not set(vals) <= {'amount', 'operation', 'rate_per_piece'}:
            self._check_wage_not_locked()
        return super().write(vals)

    def unlink(self):
        self._check_wage_not_locked()
        return super().unlink()
