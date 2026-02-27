from odoo import models, fields, api


class GarmentAccessory(models.Model):
    _name = 'garment.accessory'
    _description = 'Quản lý Phụ Liệu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Tên Phụ Liệu',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Phụ Liệu',
        required=True,
        copy=False,
    )
    accessory_type = fields.Selection([
        ('button', 'Nút / Cúc'),
        ('zipper', 'Khóa Kéo'),
        ('thread', 'Chỉ May'),
        ('label', 'Nhãn Mác'),
        ('elastic', 'Thun / Dây Chun'),
        ('lace', 'Ren / Đăng Ten'),
        ('ribbon', 'Ruy Băng'),
        ('hook', 'Móc / Khuy'),
        ('padding', 'Mex / Lót'),
        ('packaging', 'Bao Bì / Đóng Gói'),
        ('hanger', 'Móc Treo'),
        ('tag', 'Thẻ Bài'),
        ('other', 'Khác'),
    ], string='Loại Phụ Liệu', required=True, tracking=True)

    uom_id = fields.Many2one(
        'uom.uom',
        string='Đơn Vị Tính',
        required=True,
    )
    color_ids = fields.Many2many(
        'garment.color',
        string='Màu Có Sẵn',
    )
    size = fields.Char(
        string='Kích Thước',
        help='VD: 15mm, 20cm...',
    )
    material = fields.Char(
        string='Chất Liệu',
        help='VD: Nhựa, Kim Loại, Gỗ...',
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
        string='Đơn Giá',
        digits='Product Price',
    )
    min_order_qty = fields.Float(
        string='Đặt Hàng Tối Thiểu',
        default=1000.0,
    )
    lead_time = fields.Integer(
        string='Thời Gian Giao (ngày)',
        default=7,
    )
    notes = fields.Html(
        string='Ghi Chú',
    )
    active = fields.Boolean(
        string='Đang Sử Dụng',
        default=True,
    )
    image = fields.Binary(
        string='Hình Ảnh',
    )

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã phụ liệu phải là duy nhất!',
    )
