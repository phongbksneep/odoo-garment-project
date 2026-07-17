from odoo import fields, models


class GarmentOrderLink(models.Model):
    _inherit = 'garment.order'

    delivery_count = fields.Integer(
        compute='_compute_delivery_count',
        string='Số Phiếu Giao',
    )

    def _compute_delivery_count(self):
        counts = {}
        if self.ids:
            for order, count in self.env['garment.delivery.order']._read_group(
                    [('garment_order_id', 'in', self.ids)],
                    ['garment_order_id'], ['__count']):
                counts[order.id] = count
        for record in self:
            record.delivery_count = counts.get(record.id, 0)

    def action_view_deliveries(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Giao Hàng — %s' % self.name,
            'res_model': 'garment.delivery.order',
            'view_mode': 'list,form',
            'domain': [('garment_order_id', '=', self.id)],
            'context': {'default_garment_order_id': self.id},
        }
