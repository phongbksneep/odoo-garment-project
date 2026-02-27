from odoo import models, fields, api


class WashRecipe(models.Model):
    _name = 'garment.wash.recipe'
    _description = 'Công Thức Giặt (Wash Recipe)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Tên Công Thức',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Công Thức',
        required=True,
        copy=False,
    )
    wash_type = fields.Selection([
        ('normal', 'Giặt Thường (Normal Wash)'),
        ('enzyme', 'Giặt Enzyme (Enzyme Wash)'),
        ('stone', 'Giặt Đá (Stone Wash)'),
        ('acid', 'Giặt Axit (Acid Wash)'),
        ('bleach', 'Giặt Tẩy (Bleach Wash)'),
        ('garment_dye', 'Nhuộm Hàng May (Garment Dye)'),
        ('softener', 'Xả Mềm (Softener)'),
        ('silicon', 'Silicon Wash'),
        ('sand_blast', 'Phun Cát (Sand Blast)'),
        ('ozone', 'Ozone Wash'),
        ('other', 'Khác'),
    ], string='Loại Giặt', required=True, tracking=True)

    fabric_type = fields.Selection([
        ('cotton', 'Cotton'),
        ('polyester', 'Polyester'),
        ('blend', 'Pha (Blend)'),
        ('denim', 'Denim / Jeans'),
        ('silk', 'Lụa (Silk)'),
        ('wool', 'Len (Wool)'),
        ('nylon', 'Nylon'),
        ('other', 'Khác'),
    ], string='Loại Vải Áp Dụng')

    temperature = fields.Float(
        string='Nhiệt Độ (°C)',
        digits=(5, 1),
    )
    duration_minutes = fields.Integer(
        string='Thời Gian (phút)',
    )
    water_ratio = fields.Float(
        string='Tỷ Lệ Nước (lít/kg)',
        digits=(8, 2),
        help='Số lít nước trên mỗi kg hàng',
    )
    ph_level = fields.Float(
        string='Độ pH Yêu Cầu',
        digits=(4, 1),
    )

    step_ids = fields.One2many(
        'garment.wash.recipe.step',
        'recipe_id',
        string='Các Bước Thực Hiện',
    )
    total_time = fields.Integer(
        string='Tổng Thời Gian (phút)',
        compute='_compute_total_time',
        store=True,
    )
    total_chemical_cost = fields.Float(
        string='Chi Phí Hóa Chất/kg Hàng',
        compute='_compute_total_chemical_cost',
        store=True,
        digits=(12, 2),
    )

    instruction = fields.Html(
        string='Hướng Dẫn Chi Tiết',
    )
    notes = fields.Text(
        string='Ghi Chú',
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã công thức phải là duy nhất!',
    )

    @api.depends('step_ids.duration_minutes')
    def _compute_total_time(self):
        for recipe in self:
            recipe.total_time = sum(recipe.step_ids.mapped('duration_minutes'))

    @api.depends('step_ids.chemical_cost_per_kg')
    def _compute_total_chemical_cost(self):
        for recipe in self:
            recipe.total_chemical_cost = sum(recipe.step_ids.mapped('chemical_cost_per_kg'))


class WashRecipeStep(models.Model):
    _name = 'garment.wash.recipe.step'
    _description = 'Bước Trong Công Thức Giặt'
    _order = 'sequence, id'

    recipe_id = fields.Many2one(
        'garment.wash.recipe',
        string='Công Thức Giặt',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Thứ Tự',
        default=10,
    )
    name = fields.Char(
        string='Tên Bước',
        required=True,
    )
    step_type = fields.Selection([
        ('pre_wash', 'Giặt Sơ (Pre-Wash)'),
        ('main_wash', 'Giặt Chính (Main Wash)'),
        ('rinse', 'Xả Nước (Rinse)'),
        ('softener', 'Xả Mềm (Softener)'),
        ('dry', 'Sấy (Dry)'),
        ('other', 'Khác'),
    ], string='Loại Bước', required=True)

    chemical_id = fields.Many2one(
        'garment.wash.chemical',
        string='Hóa Chất Sử Dụng',
    )
    chemical_dosage = fields.Float(
        string='Liều Lượng (g/kg hàng)',
        digits=(10, 2),
        help='Gram hóa chất trên mỗi kg hàng giặt',
    )
    chemical_cost_per_kg = fields.Float(
        string='Chi Phí HC/kg Hàng',
        compute='_compute_chemical_cost',
        store=True,
        digits=(12, 2),
    )
    temperature = fields.Float(
        string='Nhiệt Độ (°C)',
        digits=(5, 1),
    )
    duration_minutes = fields.Integer(
        string='Thời Gian (phút)',
    )
    water_liters = fields.Float(
        string='Nước Sử Dụng (lít/kg)',
        digits=(8, 2),
    )
    instruction = fields.Text(
        string='Hướng Dẫn',
    )

    @api.depends('chemical_id.unit_price', 'chemical_dosage')
    def _compute_chemical_cost(self):
        for step in self:
            if step.chemical_id and step.chemical_dosage:
                # unit_price is per kg, dosage is g/kg → convert
                step.chemical_cost_per_kg = (step.chemical_dosage / 1000.0) * step.chemical_id.unit_price
            else:
                step.chemical_cost_per_kg = 0.0
