from odoo import models, fields, api


class GarmentOrderProgress(models.Model):
    """Extend garment.order with production progress tracking."""
    _inherit = 'garment.order'

    production_order_ids = fields.One2many(
        'garment.production.order',
        'garment_order_id',
        string='Lệnh Sản Xuất',
    )
    produced_qty = fields.Integer(
        string='Đã Sản Xuất',
        compute='_compute_progress',
    )
    progress = fields.Float(
        string='Tiến Độ (%)',
        compute='_compute_progress',
    )

    @api.depends('production_order_ids.completed_qty', 'total_qty')
    def _compute_progress(self):
        for order in self:
            order.produced_qty = sum(
                order.production_order_ids.mapped('completed_qty')
            )
            if order.total_qty:
                order.progress = (order.produced_qty / order.total_qty) * 100
            else:
                order.progress = 0.0
