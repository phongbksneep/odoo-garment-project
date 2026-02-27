from odoo import models, fields, api


class GarmentCuttingLayer(models.Model):
    _name = 'garment.cutting.layer'
    _description = 'Lớp Trải Vải'
    _order = 'sequence'

    cutting_order_id = fields.Many2one(
        'garment.cutting.order.adv',
        string='Cutting Order',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Layer No.', default=10)
    fabric_roll_no = fields.Char(string='Roll No.')
    lot_id = fields.Many2one(
        'stock.lot',
        string='Fabric Lot',
    )
    length = fields.Float(
        string='Length (m)',
        digits=(10, 2),
        required=True,
    )
    shade = fields.Char(
        string='Shade / Lot Color',
        help='Số lô màu của cuộn vải',
    )
    defects_found = fields.Integer(
        string='Defects Found',
        default=0,
    )
    splice_count = fields.Integer(
        string='Splices',
        default=0,
        help='Số điểm nối vải trong lớp trải',
    )
    notes = fields.Char(string='Notes')
