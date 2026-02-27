from odoo import models, fields, api


class GarmentCostLine(models.Model):
    _name = 'garment.cost.line'
    _description = 'Chi Tiết Chi Phí'
    _order = 'cost_type, sequence, id'

    cost_sheet_id = fields.Many2one(
        'garment.cost.sheet',
        string='Cost Sheet',
        required=True,
        ondelete='cascade',
    )
    cost_type = fields.Selection([
        ('fabric', 'Vải'),
        ('accessory', 'Phụ Liệu'),
        ('packing', 'Đóng Gói'),
        ('other', 'Khác'),
    ], string='Loại Chi Phí', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
    )
    consumption = fields.Float(
        string='Consumption/Pc',
        digits=(10, 4),
        required=True,
        help='Định mức tiêu hao trên 1 sản phẩm',
    )
    unit_price = fields.Float(
        string='Unit Price',
        digits=(10, 4),
        required=True,
    )
    wastage_pct = fields.Float(
        string='Wastage (%)',
        default=0.0,
        digits=(5, 2),
    )
    currency_id = fields.Many2one(
        related='cost_sheet_id.currency_id',
        store=True,
    )
    amount_per_pc = fields.Monetary(
        string='Amount/Pc',
        compute='_compute_amount',
        store=True,
        currency_field='currency_id',
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier_rank', '>', 0)],
    )
    notes = fields.Char(string='Notes')

    @api.depends('consumption', 'unit_price', 'wastage_pct')
    def _compute_amount(self):
        for line in self:
            consumption_with_wastage = line.consumption * (
                1.0 + line.wastage_pct / 100.0
            )
            line.amount_per_pc = consumption_with_wastage * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.standard_price
            self.uom_id = self.product_id.uom_id
