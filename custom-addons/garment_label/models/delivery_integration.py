from odoo import models, fields, api


class GarmentDeliveryOrderLabel(models.Model):
    """Extend delivery order with pallet/label tracking."""
    _inherit = 'garment.delivery.order'

    pallet_ids = fields.Many2many(
        'garment.pallet',
        'garment_delivery_pallet_rel',
        'delivery_id',
        'pallet_id',
        string='Pallets',
    )
    pallet_count = fields.Integer(
        string='Số Pallet',
        compute='_compute_pallet_count',
    )
    label_count = fields.Integer(
        string='Số Tem',
        compute='_compute_label_count',
    )

    @api.depends('pallet_ids')
    def _compute_pallet_count(self):
        for rec in self:
            rec.pallet_count = len(rec.pallet_ids)

    @api.depends('garment_order_id')
    def _compute_label_count(self):
        for rec in self:
            if rec.garment_order_id:
                rec.label_count = self.env['garment.label'].search_count([
                    ('garment_order_id', '=', rec.garment_order_id.id),
                ])
            else:
                rec.label_count = 0

    def action_view_labels(self):
        """View labels for this delivery's order."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tem QR',
            'res_model': 'garment.label',
            'view_mode': 'list,form',
            'domain': [('garment_order_id', '=', self.garment_order_id.id)] if self.garment_order_id else [('id', '=', 0)],
        }

    def action_view_pallets(self):
        """View pallets for this delivery."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pallets',
            'res_model': 'garment.pallet',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.pallet_ids.ids)],
        }
