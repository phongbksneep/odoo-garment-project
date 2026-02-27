from odoo import models, fields, api


class GarmentFabric(models.Model):
    _name = 'garment.fabric'
    _description = 'Quản lý Vải'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Tên Vải',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Vải',
        required=True,
        copy=False,
    )
    fabric_type = fields.Selection([
        ('cotton', 'Cotton'),
        ('polyester', 'Polyester'),
        ('silk', 'Lụa'),
        ('linen', 'Vải Lanh'),
        ('denim', 'Denim'),
        ('wool', 'Len'),
        ('chiffon', 'Vải Voan'),
        ('knit', 'Vải Dệt Kim'),
        ('woven', 'Vải Dệt Thoi'),
        ('blend', 'Vải Pha'),
        ('other', 'Khác'),
    ], string='Loại Vải', required=True, tracking=True)

    composition = fields.Char(
        string='Thành Phần',
        help='VD: 80% Cotton, 20% Polyester',
    )
    width = fields.Float(
        string='Khổ Vải (cm)',
        help='Chiều rộng khổ vải tính bằng cm',
    )
    weight = fields.Float(
        string='Định Lượng (g/m²)',
        help='Trọng lượng vải trên mét vuông',
    )
    color_ids = fields.Many2many(
        'garment.color',
        string='Màu Có Sẵn',
    )
    supplier_ids = fields.Many2many(
        'res.partner',
        string='Nhà Cung Cấp',
        domain=[('supplier_rank', '>', 0)],
    )
    product_id = fields.Many2one(
        'product.product',
        string='Sản Phẩm Liên Kết',
    )
    unit_price = fields.Float(
        string='Giá / Mét',
        digits='Product Price',
    )
    min_order_qty = fields.Float(
        string='Đặt Hàng Tối Thiểu (m)',
        default=100.0,
    )
    lead_time = fields.Integer(
        string='Thời Gian Giao (ngày)',
        default=14,
    )
    shrinkage = fields.Float(
        string='Độ Co Rút (%)',
        help='Tỷ lệ co rút sau giặt',
    )
    notes = fields.Html(
        string='Ghi Chú',
    )
    active = fields.Boolean(
        string='Đang Sử Dụng',
        default=True,
    )
    image = fields.Binary(
        string='Hình Ảnh Vải',
    )

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã vải phải là duy nhất!',
    )

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'[{record.code}] {record.name}' if record.code else record.name
