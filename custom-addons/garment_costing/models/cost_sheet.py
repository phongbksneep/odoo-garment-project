from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentCostSheet(models.Model):
    _name = 'garment.cost.sheet'
    _description = 'Bảng Tính Giá Thành'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Style',
        required=True,
        tracking=True,
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        required=True,
        tracking=True,
        domain=[('customer_rank', '>', 0)],
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Garment Order',
    )
    bom_id = fields.Many2one(
        'garment.bom',
        string='BOM / Định Mức',
        help='BOM được sử dụng để tính chi phí nguyên phụ liệu',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # --- Costing Type ---
    costing_type = fields.Selection([
        ('fob', 'FOB (Free On Board)'),
        ('cm', 'CM (Cut & Make)'),
        ('cmt', 'CMT (Cut, Make & Trim)'),
    ], string='Costing Type', required=True, default='fob', tracking=True)

    order_qty = fields.Integer(
        string='Order Quantity',
        required=True,
        default=1,
    )

    # --- Material Cost Lines ---
    fabric_line_ids = fields.One2many(
        'garment.cost.line', 'cost_sheet_id',
        string='Fabric Cost',
        domain=[('cost_type', '=', 'fabric')],
    )
    accessory_line_ids = fields.One2many(
        'garment.cost.line', 'cost_sheet_id',
        string='Accessories Cost',
        domain=[('cost_type', '=', 'accessory')],
    )
    packing_line_ids = fields.One2many(
        'garment.cost.line', 'cost_sheet_id',
        string='Packing Cost',
        domain=[('cost_type', '=', 'packing')],
    )
    other_line_ids = fields.One2many(
        'garment.cost.line', 'cost_sheet_id',
        string='Other Cost',
        domain=[('cost_type', '=', 'other')],
    )

    # --- Computed Material Costs (per piece) ---
    fabric_cost_per_pc = fields.Monetary(
        string='Fabric Cost/Pc',
        compute='_compute_material_costs',
        store=True,
        currency_field='currency_id',
    )
    accessory_cost_per_pc = fields.Monetary(
        string='Accessory Cost/Pc',
        compute='_compute_material_costs',
        store=True,
        currency_field='currency_id',
    )
    packing_cost_per_pc = fields.Monetary(
        string='Packing Cost/Pc',
        compute='_compute_material_costs',
        store=True,
        currency_field='currency_id',
    )
    other_cost_per_pc = fields.Monetary(
        string='Other Cost/Pc',
        compute='_compute_material_costs',
        store=True,
        currency_field='currency_id',
    )
    total_material_cost = fields.Monetary(
        string='Total Material/Pc',
        compute='_compute_material_costs',
        store=True,
        currency_field='currency_id',
    )

    # --- CM Cost ---
    smv = fields.Float(
        string='SMV (Standard Minute Value)',
        digits=(10, 2),
        help='Thời gian tiêu chuẩn để may 1 sản phẩm (phút)',
    )
    target_efficiency = fields.Float(
        string='Target Efficiency (%)',
        default=60.0,
        digits=(5, 2),
    )
    cm_rate_per_minute = fields.Monetary(
        string='CM Rate / Minute',
        currency_field='currency_id',
    )
    cm_cost = fields.Monetary(
        string='CM Cost/Pc',
        compute='_compute_cm_cost',
        store=True,
        currency_field='currency_id',
    )

    # --- Process Costs ---
    washing_cost = fields.Monetary(
        string='Washing/Pc',
        currency_field='currency_id',
    )
    embroidery_cost = fields.Monetary(
        string='Embroidery/Pc',
        currency_field='currency_id',
    )
    printing_cost = fields.Monetary(
        string='Printing/Pc',
        currency_field='currency_id',
    )
    testing_cost = fields.Monetary(
        string='Testing/Pc',
        currency_field='currency_id',
    )
    total_process_cost = fields.Monetary(
        string='Total Process/Pc',
        compute='_compute_process_cost',
        store=True,
        currency_field='currency_id',
    )

    # --- Commercial Costs (FOB only) ---
    commission_pct = fields.Float(
        string='Commission (%)',
        default=0.0,
        digits=(5, 2),
    )
    commission_cost = fields.Monetary(
        string='Commission/Pc',
        compute='_compute_commercial_costs',
        store=True,
        currency_field='currency_id',
    )
    freight_cost = fields.Monetary(
        string='Inland Freight/Pc',
        currency_field='currency_id',
    )
    overhead_pct = fields.Float(
        string='Overhead (%)',
        default=5.0,
        digits=(5, 2),
    )
    overhead_cost = fields.Monetary(
        string='Overhead/Pc',
        compute='_compute_commercial_costs',
        store=True,
        currency_field='currency_id',
    )
    profit_pct = fields.Float(
        string='Profit (%)',
        default=5.0,
        digits=(5, 2),
    )
    profit_cost = fields.Monetary(
        string='Profit/Pc',
        compute='_compute_commercial_costs',
        store=True,
        currency_field='currency_id',
    )

    # --- Final ---
    cost_price = fields.Monetary(
        string='Cost Price/Pc',
        compute='_compute_final_price',
        store=True,
        currency_field='currency_id',
    )
    selling_price = fields.Monetary(
        string='Selling Price/Pc',
        compute='_compute_final_price',
        store=True,
        currency_field='currency_id',
    )
    total_order_value = fields.Monetary(
        string='Total Order Value',
        compute='_compute_final_price',
        store=True,
        currency_field='currency_id',
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('approved', 'Đã Duyệt'),
        ('revised', 'Đã Sửa'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    revision = fields.Integer(string='Revision', default=0, copy=False)
    notes = fields.Html(string='Notes')

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.cost.sheet'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains('order_qty')
    def _check_order_qty(self):
        for record in self:
            if record.order_qty <= 0:
                raise ValidationError(
                    _('Order quantity must be greater than zero.')
                )

    @api.constrains('target_efficiency')
    def _check_efficiency(self):
        for record in self:
            if record.target_efficiency <= 0 or record.target_efficiency > 100:
                raise ValidationError(
                    _('Target efficiency must be between 0 and 100%%.')
                )

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------
    @api.depends(
        'fabric_line_ids.amount_per_pc',
        'accessory_line_ids.amount_per_pc',
        'packing_line_ids.amount_per_pc',
        'other_line_ids.amount_per_pc',
    )
    def _compute_material_costs(self):
        for sheet in self:
            sheet.fabric_cost_per_pc = sum(
                sheet.fabric_line_ids.mapped('amount_per_pc')
            )
            sheet.accessory_cost_per_pc = sum(
                sheet.accessory_line_ids.mapped('amount_per_pc')
            )
            sheet.packing_cost_per_pc = sum(
                sheet.packing_line_ids.mapped('amount_per_pc')
            )
            sheet.other_cost_per_pc = sum(
                sheet.other_line_ids.mapped('amount_per_pc')
            )
            sheet.total_material_cost = (
                sheet.fabric_cost_per_pc
                + sheet.accessory_cost_per_pc
                + sheet.packing_cost_per_pc
                + sheet.other_cost_per_pc
            )

    @api.depends('smv', 'target_efficiency', 'cm_rate_per_minute')
    def _compute_cm_cost(self):
        for sheet in self:
            if sheet.target_efficiency > 0 and sheet.smv > 0:
                actual_minutes = sheet.smv / (sheet.target_efficiency / 100.0)
                sheet.cm_cost = actual_minutes * sheet.cm_rate_per_minute
            else:
                sheet.cm_cost = 0.0

    @api.depends('washing_cost', 'embroidery_cost', 'printing_cost', 'testing_cost')
    def _compute_process_cost(self):
        for sheet in self:
            sheet.total_process_cost = (
                sheet.washing_cost
                + sheet.embroidery_cost
                + sheet.printing_cost
                + sheet.testing_cost
            )

    @api.depends(
        'total_material_cost', 'cm_cost', 'total_process_cost',
        'commission_pct', 'freight_cost', 'overhead_pct', 'profit_pct',
    )
    def _compute_commercial_costs(self):
        for sheet in self:
            subtotal = (
                sheet.total_material_cost
                + sheet.cm_cost
                + sheet.total_process_cost
            )
            sheet.overhead_cost = subtotal * (sheet.overhead_pct / 100.0)
            base = subtotal + sheet.overhead_cost + sheet.freight_cost
            sheet.commission_cost = base * (sheet.commission_pct / 100.0)
            sheet.profit_cost = base * (sheet.profit_pct / 100.0)

    @api.depends(
        'costing_type', 'total_material_cost', 'cm_cost',
        'total_process_cost', 'overhead_cost', 'freight_cost',
        'commission_cost', 'profit_cost', 'order_qty',
    )
    def _compute_final_price(self):
        for sheet in self:
            if sheet.costing_type == 'cm':
                sheet.cost_price = sheet.cm_cost
                sheet.selling_price = (
                    sheet.cm_cost + sheet.overhead_cost + sheet.profit_cost
                )
            elif sheet.costing_type == 'cmt':
                sheet.cost_price = (
                    sheet.accessory_cost_per_pc
                    + sheet.cm_cost
                    + sheet.total_process_cost
                )
                sheet.selling_price = (
                    sheet.cost_price + sheet.overhead_cost + sheet.profit_cost
                )
            else:  # fob
                sheet.cost_price = (
                    sheet.total_material_cost
                    + sheet.cm_cost
                    + sheet.total_process_cost
                    + sheet.overhead_cost
                    + sheet.freight_cost
                )
                sheet.selling_price = (
                    sheet.cost_price
                    + sheet.commission_cost
                    + sheet.profit_cost
                )
            sheet.total_order_value = sheet.selling_price * sheet.order_qty

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft cost sheets can be confirmed.'))
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Only confirmed cost sheets can be approved.'))
        self.write({'state': 'approved'})

    def action_revise(self):
        self.ensure_one()
        if self.state not in ('confirmed', 'approved'):
            raise UserError(_('Only confirmed or approved cost sheets can be revised.'))
        self.write({
            'state': 'revised',
            'revision': self.revision + 1,
        })

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError(_('Cost sheet is already cancelled.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_load_from_bom(self):
        """Load material lines from garment BOM linked to style."""
        self.ensure_one()
        bom = self.env['garment.bom'].search([
            ('style_id', '=', self.style_id.id),
            ('state', '=', 'approved'),
        ], order='version desc', limit=1)
        if not bom:
            # Fall back to confirmed BOM
            bom = self.env['garment.bom'].search([
                ('style_id', '=', self.style_id.id),
                ('state', '=', 'confirmed'),
            ], order='version desc', limit=1)
        if not bom:
            raise UserError(
                _('Không tìm thấy BOM cho mã hàng "%s". Hãy tạo BOM trước!')
                % self.style_id.name
            )
        # Clear existing lines
        self.env['garment.cost.line'].search([
            ('cost_sheet_id', '=', self.id),
        ]).unlink()

        type_mapping = {
            'fabric': 'fabric',
            'lining': 'fabric',
            'interlining': 'accessory',
            'thread': 'accessory',
            'zipper': 'accessory',
            'button': 'accessory',
            'label': 'accessory',
            'elastic': 'accessory',
            'packing': 'packing',
            'other': 'other',
        }

        for bom_line in bom.line_ids:
            cost_type = type_mapping.get(bom_line.material_type, 'other')
            vals = {
                'cost_sheet_id': self.id,
                'cost_type': cost_type,
                'description': bom_line.description,
                'consumption': bom_line.consumption,
                'unit_price': bom_line.unit_price,
                'wastage_pct': bom_line.wastage_pct,
                'supplier_id': bom_line.supplier_id.id,
            }
            if bom_line.product_id:
                vals['product_id'] = bom_line.product_id.id
                vals['uom_id'] = bom_line.product_id.uom_id.id
            self.env['garment.cost.line'].create(vals)
