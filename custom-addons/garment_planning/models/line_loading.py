from odoo import models, fields, api
import math


class GarmentLineLoading(models.Model):
    _name = 'garment.line.loading'
    _description = 'Line Loading / Assignment'
    _order = 'date_start'

    plan_id = fields.Many2one(
        'garment.production.plan',
        string='Production Plan',
        required=True,
        ondelete='cascade',
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
        required=True,
    )
    worker_count = fields.Integer(
        string='Số Công Nhân',
        related='sewing_line_id.worker_count',
        readonly=True,
    )
    smv = fields.Float(
        string='SMV',
        related='plan_id.smv',
        readonly=True,
    )

    target_efficiency = fields.Float(
        string='Hiệu Suất Mục Tiêu (%)',
        default=65.0,
        digits=(10, 1),
    )
    daily_capacity = fields.Integer(
        string='Năng Suất/Ngày',
        compute='_compute_daily_capacity',
        store=True,
    )
    planned_qty = fields.Integer(
        string='SL Kế Hoạch',
    )
    date_start = fields.Date(string='Bắt Đầu')
    date_end = fields.Date(string='Kết Thúc')
    required_days = fields.Float(
        string='Số Ngày Cần',
        compute='_compute_required_days',
        digits=(10, 1),
    )

    notes = fields.Char(string='Ghi Chú')

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('worker_count', 'smv', 'target_efficiency')
    def _compute_daily_capacity(self):
        """Daily capacity = (workers × 480 min × efficiency%) / SMV."""
        for line in self:
            if line.smv > 0 and line.worker_count > 0:
                line.daily_capacity = int(
                    (line.worker_count * 480 * line.target_efficiency / 100)
                    / line.smv
                )
            else:
                line.daily_capacity = 0

    @api.depends('planned_qty', 'daily_capacity')
    def _compute_required_days(self):
        for line in self:
            if line.daily_capacity > 0:
                line.required_days = math.ceil(
                    line.planned_qty / line.daily_capacity
                )
            else:
                line.required_days = 0
