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

    production_order_count = fields.Integer(
        compute='_compute_production_order_count',
        string='Số Lệnh SX',
    )

    def _compute_production_order_count(self):
        counts = {}
        if self.ids:
            for order, count in self.env[
                    'garment.production.order']._read_group(
                    [('garment_order_id', 'in', self.ids)],
                    ['garment_order_id'], ['__count']):
                counts[order.id] = count
        for record in self:
            record.production_order_count = counts.get(record.id, 0)

    def action_view_production_orders(self):
        self.ensure_one()
        planned = sum(self.production_order_ids.filtered(
            lambda p: p.state != 'cancelled').mapped('planned_qty'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lệnh Sản Xuất — %s' % self.name,
            'res_model': 'garment.production.order',
            'view_mode': 'list,form',
            'domain': [('garment_order_id', '=', self.id)],
            'context': {
                'default_garment_order_id': self.id,
                'default_planned_qty': max(self.total_qty - planned, 0),
            },
        }
