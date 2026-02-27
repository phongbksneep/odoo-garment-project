from odoo import models, fields, api


class GarmentCartonLine(models.Model):
    _name = 'garment.carton.line'
    _description = 'Carton Line'
    _order = 'carton_from'

    packing_list_id = fields.Many2one(
        'garment.packing.list',
        string='Packing List',
        required=True,
        ondelete='cascade',
    )
    carton_from = fields.Integer(
        string='Carton From',
        required=True,
    )
    carton_to = fields.Integer(
        string='Carton To',
        required=True,
    )
    carton_count = fields.Integer(
        string='No. of Cartons',
        compute='_compute_carton_count',
        store=True,
    )

    size_id = fields.Many2one('garment.size', string='Size')
    color_id = fields.Many2one('garment.color', string='Color')
    pcs_per_carton = fields.Integer(
        string='Pcs/Carton',
        required=True,
    )
    total_pcs = fields.Integer(
        string='Total Pcs',
        compute='_compute_total_pcs',
        store=True,
    )

    # --- Carton Dimensions ---
    length_cm = fields.Float(string='Length (cm)', digits=(10, 1))
    width_cm = fields.Float(string='Width (cm)', digits=(10, 1))
    height_cm = fields.Float(string='Height (cm)', digits=(10, 1))
    gross_weight = fields.Float(
        string='Gross Weight/Ctn (kg)',
        digits=(10, 2),
    )
    net_weight = fields.Float(
        string='Net Weight/Ctn (kg)',
        digits=(10, 2),
    )
    cbm_per_carton = fields.Float(
        string='CBM/Ctn (m³)',
        compute='_compute_cbm',
        store=True,
        digits=(10, 4),
    )

    # --- Totals ---
    total_gross = fields.Float(
        string='Total Gross (kg)',
        compute='_compute_total_weight',
        store=True,
        digits=(10, 2),
    )
    total_net = fields.Float(
        string='Total Net (kg)',
        compute='_compute_total_weight',
        store=True,
        digits=(10, 2),
    )
    total_cbm = fields.Float(
        string='Total CBM (m³)',
        compute='_compute_total_weight',
        store=True,
        digits=(10, 3),
    )

    barcode = fields.Char(string='Carton Barcode')
    notes = fields.Char(string='Notes')

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('carton_from', 'carton_to')
    def _compute_carton_count(self):
        for line in self:
            line.carton_count = max(0, line.carton_to - line.carton_from + 1)

    @api.depends('carton_count', 'pcs_per_carton')
    def _compute_total_pcs(self):
        for line in self:
            line.total_pcs = line.carton_count * line.pcs_per_carton

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for line in self:
            line.cbm_per_carton = (
                line.length_cm * line.width_cm * line.height_cm
            ) / 1_000_000  # cm³ → m³

    @api.depends('gross_weight', 'net_weight', 'cbm_per_carton', 'carton_count')
    def _compute_total_weight(self):
        for line in self:
            line.total_gross = line.gross_weight * line.carton_count
            line.total_net = line.net_weight * line.carton_count
            line.total_cbm = line.cbm_per_carton * line.carton_count
