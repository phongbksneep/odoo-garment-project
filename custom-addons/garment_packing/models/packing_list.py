from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentPackingList(models.Model):
    _name = 'garment.packing.list'
    _description = 'Packing List'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Garment Order',
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        required=True,
        domain=[('customer_rank', '>', 0)],
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Style',
    )
    date = fields.Date(
        string='Packing Date',
        default=fields.Date.today,
    )

    # --- Shipment Info ---
    po_number = fields.Char(string='PO Number')
    destination_port = fields.Char(string='Destination Port')
    ship_mode = fields.Selection([
        ('sea', 'Sea Freight'),
        ('air', 'Air Freight'),
        ('courier', 'Courier'),
    ], string='Ship Mode', default='sea')
    etd = fields.Date(string='ETD')
    eta = fields.Date(string='ETA')
    vessel_name = fields.Char(string='Vessel / Flight')
    bl_number = fields.Char(string='B/L Number')
    container_no = fields.Char(string='Container No.')

    # --- Packing Type ---
    packing_type = fields.Selection([
        ('solid', 'Solid Pack'),
        ('ratio', 'Ratio Pack'),
        ('assorted', 'Assorted Pack'),
    ], string='Packing Type', default='ratio')

    # --- Carton Lines ---
    carton_ids = fields.One2many(
        'garment.carton.line',
        'packing_list_id',
        string='Cartons',
    )

    # --- Related Shipping Documents ---
    shipping_instruction_ids = fields.One2many(
        'garment.shipping.instruction',
        'packing_list_id',
        string='Shipping Instructions',
    )
    certificate_origin_ids = fields.One2many(
        'garment.certificate.origin',
        'packing_list_id',
        string='Certificates of Origin',
    )
    si_count = fields.Integer(
        string='SI Count',
        compute='_compute_doc_counts',
    )
    co_count = fields.Integer(
        string='C/O Count',
        compute='_compute_doc_counts',
    )

    # --- Computed Totals ---
    total_cartons = fields.Integer(
        string='Total Cartons',
        compute='_compute_totals',
        store=True,
    )
    total_pieces = fields.Integer(
        string='Total Pieces',
        compute='_compute_totals',
        store=True,
    )
    total_gross_weight = fields.Float(
        string='Total Gross Weight (kg)',
        compute='_compute_totals',
        store=True,
        digits=(10, 2),
    )
    total_net_weight = fields.Float(
        string='Total Net Weight (kg)',
        compute='_compute_totals',
        store=True,
        digits=(10, 2),
    )
    total_cbm = fields.Float(
        string='Total CBM (m³)',
        compute='_compute_totals',
        store=True,
        digits=(10, 3),
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('packing', 'Đang Đóng Gói'),
        ('packed', 'Đã Đóng'),
        ('shipped', 'Đã Xuất'),
        ('delivered', 'Đã Giao'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Notes')

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.packing.list'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    def _compute_doc_counts(self):
        for rec in self:
            rec.si_count = len(rec.shipping_instruction_ids)
            rec.co_count = len(rec.certificate_origin_ids)

    @api.depends(
        'carton_ids.carton_count', 'carton_ids.total_pcs',
        'carton_ids.total_gross', 'carton_ids.total_net', 'carton_ids.total_cbm',
    )
    def _compute_totals(self):
        for record in self:
            record.total_cartons = sum(record.carton_ids.mapped('carton_count'))
            record.total_pieces = sum(record.carton_ids.mapped('total_pcs'))
            record.total_gross_weight = sum(record.carton_ids.mapped('total_gross'))
            record.total_net_weight = sum(record.carton_ids.mapped('total_net'))
            record.total_cbm = sum(record.carton_ids.mapped('total_cbm'))

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_start_packing(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Can only start packing from draft.'))
        self.write({'state': 'packing'})

    def action_packed(self):
        self.ensure_one()
        if self.state != 'packing':
            raise UserError(_('Must be packing to mark as packed.'))
        if not self.carton_ids:
            raise UserError(_('Please add carton lines before completing.'))
        self.write({'state': 'packed'})

    def action_shipped(self):
        self.ensure_one()
        if self.state != 'packed':
            raise UserError(_('Must be packed before shipping.'))
        self.write({'state': 'shipped'})

    def action_delivered(self):
        self.ensure_one()
        if self.state != 'shipped':
            raise UserError(_('Must be shipped before delivery confirmation.'))
        self.write({'state': 'delivered'})

    def action_cancel(self):
        self.ensure_one()
        if self.state in ('shipped', 'delivered'):
            raise UserError(_('Cannot cancel shipped or delivered packing lists.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_view_shipping_instructions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Shipping Instructions'),
            'res_model': 'garment.shipping.instruction',
            'view_mode': 'list,form',
            'domain': [('packing_list_id', '=', self.id)],
            'context': {'default_packing_list_id': self.id},
        }

    def action_view_certificates_origin(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificates of Origin'),
            'res_model': 'garment.certificate.origin',
            'view_mode': 'list,form',
            'domain': [('packing_list_id', '=', self.id)],
            'context': {'default_packing_list_id': self.id},
        }
