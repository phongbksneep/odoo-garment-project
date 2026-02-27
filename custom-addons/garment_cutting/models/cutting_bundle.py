from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentCuttingBundle(models.Model):
    _name = 'garment.cutting.bundle'
    _description = 'Bó Hàng Cắt'
    _order = 'sequence'

    cutting_order_id = fields.Many2one(
        'garment.cutting.order.adv',
        string='Cutting Order',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    bundle_no = fields.Char(
        string='Bundle No.',
        required=True,
    )
    size_id = fields.Many2one(
        'garment.size',
        string='Size',
        required=True,
    )
    color_id = fields.Many2one(
        'garment.color',
        string='Color',
    )
    quantity = fields.Integer(
        string='Quantity (pcs)',
        required=True,
    )
    layer_from = fields.Integer(string='From Layer')
    layer_to = fields.Integer(string='To Layer')

    is_issued = fields.Boolean(
        string='Issued to Sewing',
        default=False,
        help='Đã phát xuống chuyền may chưa',
    )
    issued_date = fields.Date(string='Issued Date')
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Sewing Line',
    )
    notes = fields.Char(string='Notes')

    _bundle_no_per_order_unique = models.Constraint(
        'UNIQUE(cutting_order_id, bundle_no)',
        'Số bó hàng phải duy nhất trong cùng lệnh cắt!',
    )

    def action_issue_to_sewing(self):
        """Mark bundle as issued to sewing line."""
        for bundle in self:
            if bundle.is_issued:
                raise UserError(
                    _('Bundle %s is already issued.') % bundle.bundle_no
                )
            if not bundle.sewing_line_id:
                raise UserError(
                    _('Please select a sewing line for bundle %s.') % bundle.bundle_no
                )
            bundle.write({
                'is_issued': True,
                'issued_date': fields.Date.today(),
            })
