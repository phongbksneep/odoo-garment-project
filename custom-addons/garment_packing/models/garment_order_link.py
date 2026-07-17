from odoo import fields, models


class GarmentOrderLink(models.Model):
    _inherit = 'garment.order'

    packing_list_count = fields.Integer(
        compute='_compute_packing_list_count',
        string='Số Packing List',
    )

    def _compute_packing_list_count(self):
        counts = {}
        if self.ids:
            for order, count in self.env['garment.packing.list']._read_group(
                    [('garment_order_id', 'in', self.ids)],
                    ['garment_order_id'], ['__count']):
                counts[order.id] = count
        for record in self:
            record.packing_list_count = counts.get(record.id, 0)

    def action_view_packing_lists(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Packing List — %s' % self.name,
            'res_model': 'garment.packing.list',
            'view_mode': 'list,form',
            'domain': [('garment_order_id', '=', self.id)],
            'context': {'default_garment_order_id': self.id, 'default_buyer_id': self.customer_id.id, 'default_style_id': self.style_id.id},
        }
