from odoo import fields, models


class GarmentOrderLink(models.Model):
    _inherit = 'garment.order'

    allocation_count = fields.Integer(
        compute='_compute_allocation_count',
        string='Số Phiếu Phân Bổ',
    )

    def _compute_allocation_count(self):
        counts = {}
        if self.ids:
            for order, count in self.env['garment.material.allocation']._read_group(
                    [('garment_order_id', 'in', self.ids)],
                    ['garment_order_id'], ['__count']):
                counts[order.id] = count
        for record in self:
            record.allocation_count = counts.get(record.id, 0)

    def action_view_allocations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phân Bổ Nguyên Liệu — %s' % self.name,
            'res_model': 'garment.material.allocation',
            'view_mode': 'list,form',
            'domain': [('garment_order_id', '=', self.id)],
            'context': {'default_garment_order_id': self.id},
        }
