from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GarmentDailyOutput(models.Model):
    _name = 'garment.daily.output'
    _description = 'Sản Lượng Hàng Ngày'
    _order = 'date desc, sewing_line_id'

    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Lệnh Sản Xuất',
        required=True,
        index=True,
        ondelete='cascade',
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
        related='production_order_id.sewing_line_id',
        store=True,
    )
    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
    )
    shift = fields.Selection([
        ('morning', 'Ca Sáng'),
        ('afternoon', 'Ca Chiều'),
        ('night', 'Ca Tối'),
        ('overtime', 'Tăng Ca'),
    ], string='Ca Làm Việc', required=True, default='morning')

    target_qty = fields.Integer(
        string='Mục Tiêu (sp)',
        help='Số lượng mục tiêu trong ca',
    )
    output_qty = fields.Integer(
        string='Sản Lượng Đạt (sp)',
        required=True,
    )
    defect_qty = fields.Integer(
        string='Số Lượng Lỗi (sp)',
        default=0,
    )
    rework_qty = fields.Integer(
        string='Sửa Lại (sp)',
        default=0,
    )
    worker_count = fields.Integer(
        string='Số CN Làm Việc',
    )
    working_hours = fields.Float(
        string='Giờ Làm Việc',
        default=8.0,
    )
    efficiency = fields.Float(
        string='Hiệu Suất (%)',
        compute='_compute_efficiency',
        store=True,
    )
    defect_rate = fields.Float(
        string='Tỷ Lệ Lỗi (%)',
        compute='_compute_defect_rate',
        store=True,
    )
    pieces_per_hour = fields.Float(
        string='SP/Giờ/CN',
        compute='_compute_pieces_per_hour',
        store=True,
        digits=(12, 2),
    )
    notes = fields.Text(
        string='Ghi Chú / Nguyên Nhân',
    )

    @api.constrains('output_qty', 'defect_qty', 'rework_qty')
    def _check_quantities(self):
        for record in self:
            if record.output_qty < 0:
                raise ValidationError('Sản lượng đạt không được âm.')
            if record.defect_qty < 0:
                raise ValidationError('Số lượng lỗi không được âm.')
            if record.rework_qty < 0:
                raise ValidationError('Số lượng sửa lại không được âm.')

    @api.constrains('output_qty', 'production_order_id')
    def _check_total_vs_planned(self):
        """Tổng sản lượng không vượt SL kế hoạch của lệnh SX
        (+ dung sai cấu hình, mặc định 5%)."""
        icp = self.env['ir.config_parameter'].sudo()
        try:
            tolerance = float(
                icp.get_param('garment_base.qty_tolerance_pct') or 5.0)
        except (TypeError, ValueError):
            tolerance = 5.0
        for prod_order in self.production_order_id:
            if not prod_order.planned_qty:
                continue
            total = sum(prod_order.daily_output_ids.mapped('output_qty'))
            cap = prod_order.planned_qty * (1 + tolerance / 100)
            if total > cap:
                raise ValidationError(
                    'Tổng sản lượng (%d) vượt SL kế hoạch của lệnh %s '
                    '(%d, dung sai %.0f%%).'
                    % (total, prod_order.name, prod_order.planned_qty,
                       tolerance))

    @api.depends('target_qty', 'output_qty')
    def _compute_efficiency(self):
        for record in self:
            if record.target_qty:
                record.efficiency = (record.output_qty / record.target_qty) * 100
            else:
                record.efficiency = 0.0

    @api.depends('output_qty', 'defect_qty')
    def _compute_defect_rate(self):
        for record in self:
            total = record.output_qty + record.defect_qty
            if total:
                record.defect_rate = (record.defect_qty / total) * 100
            else:
                record.defect_rate = 0.0

    @api.depends('output_qty', 'worker_count', 'working_hours')
    def _compute_pieces_per_hour(self):
        for record in self:
            total_hours = record.worker_count * record.working_hours
            if total_hours > 0:
                record.pieces_per_hour = record.output_qty / total_hours
            else:
                record.pieces_per_hour = 0.0
