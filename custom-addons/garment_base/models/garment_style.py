from odoo import models, fields, api


class GarmentStyle(models.Model):
    _name = 'garment.style'
    _description = 'Mẫu May / Kiểu Dáng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Tên Mẫu',
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string='Mã Mẫu (Style No.)',
        required=True,
        copy=False,
        tracking=True,
    )
    category = fields.Selection([
        ('shirt', 'Áo Sơ Mi'),
        ('tshirt', 'Áo Thun / T-Shirt'),
        ('polo', 'Áo Polo'),
        ('jacket', 'Áo Khoác / Jacket'),
        ('blazer', 'Áo Vest / Blazer'),
        ('pants', 'Quần Tây'),
        ('jeans', 'Quần Jeans'),
        ('shorts', 'Quần Short'),
        ('skirt', 'Chân Váy'),
        ('dress', 'Đầm / Váy'),
        ('suit', 'Bộ Vest'),
        ('uniform', 'Đồng Phục'),
        ('sportswear', 'Đồ Thể Thao'),
        ('underwear', 'Đồ Lót'),
        ('sleepwear', 'Đồ Ngủ'),
        ('childwear', 'Đồ Trẻ Em'),
        ('other', 'Khác'),
    ], string='Loại Sản Phẩm', required=True, tracking=True)

    season = fields.Selection([
        ('ss', 'Xuân Hè (SS)'),
        ('aw', 'Thu Đông (AW)'),
        ('all', 'Quanh Năm'),
    ], string='Mùa', default='all')

    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('unisex', 'Unisex'),
        ('kids', 'Trẻ Em'),
    ], string='Giới Tính', default='unisex')

    fabric_ids = fields.Many2many(
        'garment.fabric',
        string='Vải Sử Dụng',
    )
    accessory_ids = fields.Many2many(
        'garment.accessory',
        string='Phụ Liệu Sử Dụng',
    )
    size_ids = fields.Many2many(
        'garment.size',
        string='Bảng Size',
    )
    color_ids = fields.Many2many(
        'garment.color',
        string='Bảng Màu',
    )

    fabric_consumption = fields.Float(
        string='Định Mức Vải (m/sp)',
        help='Số mét vải cần cho 1 sản phẩm',
        digits=(12, 3),
    )
    sewing_time = fields.Float(
        string='Thời Gian May (phút/sp)',
        help='Thời gian may trung bình cho 1 sản phẩm',
    )
    sam = fields.Float(
        string='SAM (Standard Allowed Minutes)',
        help='Thời gian chuẩn cho phép (phút)',
    )
    difficulty_level = fields.Selection([
        ('easy', 'Dễ'),
        ('medium', 'Trung Bình'),
        ('hard', 'Khó'),
        ('very_hard', 'Rất Khó'),
    ], string='Độ Khó', default='medium')

    # Wash Care Instructions
    wash_care = fields.Text(
        string='Hướng Dẫn Giặt Ủi',
        help='VD: Giặt máy ở 30°C, không tẩy, ủi nhiệt độ trung bình',
    )
    wash_symbol_ids = fields.Many2many(
        'garment.wash.symbol',
        string='Ký Hiệu Giặt',
    )

    # Thông tin kỹ thuật
    tech_pack = fields.Binary(
        string='Tech Pack / Tài Liệu Kỹ Thuật',
    )
    tech_pack_filename = fields.Char(
        string='Tên File Tech Pack',
    )
    pattern_file = fields.Binary(
        string='File Rập / Pattern',
    )
    pattern_filename = fields.Char(
        string='Tên File Rập',
    )
    
    image_front = fields.Binary(string='Hình Mặt Trước')
    image_back = fields.Binary(string='Hình Mặt Sau')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('design', 'Đang Thiết Kế'),
        ('sample', 'Làm Mẫu'),
        ('approved', 'Đã Duyệt'),
        ('production', 'Đang Sản Xuất'),
        ('discontinued', 'Ngừng Sản Xuất'),
    ], string='Trạng Thái', default='draft', tracking=True)

    customer_id = fields.Many2one(
        'res.partner',
        string='Khách Hàng',
        domain=[('customer_rank', '>', 0)],
    )
    description = fields.Html(
        string='Mô Tả Chi Tiết',
    )
    notes = fields.Html(
        string='Ghi Chú Kỹ Thuật',
    )
    active = fields.Boolean(
        string='Đang Sử Dụng',
        default=True,
    )

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Mã mẫu (Style No.) phải là duy nhất!',
    )

    def action_design(self):
        self.write({'state': 'design'})

    def action_sample(self):
        self.write({'state': 'sample'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_production(self):
        self.write({'state': 'production'})

    def action_discontinue(self):
        self.write({'state': 'discontinued'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
