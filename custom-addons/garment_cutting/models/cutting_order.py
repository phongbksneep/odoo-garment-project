from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentCuttingOrderAdv(models.Model):
    _name = 'garment.cutting.order.adv'
    _description = 'Lệnh Cắt Nâng Cao'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    production_order_id = fields.Many2one(
        'garment.production.order',
        string='Production Order',
        required=True,
        tracking=True,
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Garment Order',
        related='production_order_id.garment_order_id',
        store=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Style',
        related='production_order_id.style_id',
        store=True,
    )
    date = fields.Date(
        string='Cutting Date',
        default=fields.Date.today,
        required=True,
    )

    # --- Marker Info ---
    marker_length = fields.Float(
        string='Marker Length (m)',
        digits=(10, 2),
        help='Chiều dài sơ đồ cắt',
    )
    marker_width = fields.Float(
        string='Marker Width (cm)',
        digits=(10, 2),
    )
    marker_efficiency = fields.Float(
        string='Marker Efficiency (%)',
        digits=(5, 2),
        help='Tỷ lệ sử dụng vải trên sơ đồ cắt',
    )

    # --- Fabric ---
    fabric_id = fields.Many2one(
        'garment.fabric',
        string='Fabric',
    )
    fabric_color = fields.Char(string='Fabric Color')

    # --- Spreading (Trải vải) ---
    layer_ids = fields.One2many(
        'garment.cutting.layer',
        'cutting_order_id',
        string='Spreading Layers',
    )
    total_layers = fields.Integer(
        string='Total Layers',
        compute='_compute_layer_totals',
        store=True,
    )
    total_fabric_used = fields.Float(
        string='Total Fabric Used (m)',
        compute='_compute_layer_totals',
        store=True,
        digits=(10, 2),
    )

    # --- Bundles ---
    bundle_ids = fields.One2many(
        'garment.cutting.bundle',
        'cutting_order_id',
        string='Bundles',
    )
    total_pieces_cut = fields.Integer(
        string='Total Pieces Cut',
        compute='_compute_bundle_totals',
        store=True,
    )
    total_bundles = fields.Integer(
        string='Total Bundles',
        compute='_compute_bundle_totals',
        store=True,
    )

    # --- Quality ---
    defective_pieces = fields.Integer(
        string='Defective Pieces',
        default=0,
    )
    wastage_kg = fields.Float(
        string='Wastage (kg)',
        digits=(10, 2),
    )

    cutter_id = fields.Many2one(
        'hr.employee',
        string='Cutter',
    )
    table_no = fields.Char(string='Cutting Table No.')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('spreading', 'Đang Trải Vải'),
        ('cutting', 'Đang Cắt'),
        ('numbering', 'Đánh Số / Bó Hàng'),
        ('done', 'Hoàn Thành'),
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
                    'garment.cutting.order.adv'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains('marker_efficiency')
    def _check_marker_efficiency(self):
        for record in self:
            if record.marker_efficiency and (
                record.marker_efficiency < 0 or record.marker_efficiency > 100
            ):
                raise ValidationError(
                    _('Marker efficiency must be between 0 and 100%%.')
                )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('layer_ids.length', 'layer_ids')
    def _compute_layer_totals(self):
        for record in self:
            record.total_layers = len(record.layer_ids)
            record.total_fabric_used = sum(record.layer_ids.mapped('length'))

    @api.depends('bundle_ids.quantity', 'bundle_ids')
    def _compute_bundle_totals(self):
        for record in self:
            record.total_bundles = len(record.bundle_ids)
            record.total_pieces_cut = sum(record.bundle_ids.mapped('quantity'))

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_start_spreading(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Can only start spreading from draft state.'))
        self.write({'state': 'spreading'})

    def action_start_cutting(self):
        self.ensure_one()
        if self.state != 'spreading':
            raise UserError(_('Must complete spreading before cutting.'))
        if not self.layer_ids:
            raise UserError(_('Please add spreading layers before cutting.'))
        self.write({'state': 'cutting'})

    def action_start_numbering(self):
        self.ensure_one()
        if self.state != 'cutting':
            raise UserError(_('Must complete cutting before numbering.'))
        self.write({'state': 'numbering'})

    def action_done(self):
        self.ensure_one()
        if self.state != 'numbering':
            raise UserError(_('Must complete numbering before finalizing.'))
        if not self.bundle_ids:
            raise UserError(_('Please create bundles before completing.'))
        self.write({'state': 'done'})

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'done':
            raise UserError(_('Cannot cancel a completed cutting order.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})
