from odoo import models, fields, api


class WashChemical(models.Model):
    _name = 'garment.wash.chemical'
    _description = 'Hóa Chất Giặt'
    _order = 'name'

    name = fields.Char(
        string='Tên Hóa Chất',
        required=True,
    )
    code = fields.Char(
        string='Mã',
        required=True,
    )
    chemical_type = fields.Selection([
        ('detergent', 'Chất Giặt (Detergent)'),
        ('softener', 'Chất Làm Mềm (Softener)'),
        ('bleach', 'Chất Tẩy (Bleach)'),
        ('enzyme', 'Enzyme'),
        ('acid', 'Axit'),
        ('alkali', 'Kiềm (Alkali)'),
        ('resin', 'Nhựa (Resin)'),
        ('silicon', 'Silicon'),
        ('dye', 'Thuốc Nhuộm'),
        ('other', 'Khác'),
    ], string='Loại Hóa Chất', required=True)

    supplier_id = fields.Many2one(
        'res.partner',
        string='Nhà Cung Cấp',
        domain=[('supplier_rank', '>', 0)],
    )
    unit_price = fields.Float(
        string='Đơn Giá (VNĐ/kg)',
        digits=(12, 2),
    )
    uom = fields.Selection([
        ('kg', 'Kilogram'),
        ('liter', 'Lít'),
        ('gram', 'Gram'),
        ('ml', 'Mililit'),
    ], string='Đơn Vị Tính', default='kg')

    safety_note = fields.Text(
        string='Lưu Ý An Toàn',
        help='Hướng dẫn bảo quản, sử dụng an toàn hóa chất',
    )
    msds_file = fields.Binary(string='MSDS File')
    msds_filename = fields.Char(string='Tên File MSDS')

    stock_qty = fields.Float(
        string='Tồn Kho (kg)',
        digits=(12, 2),
    )
    min_stock = fields.Float(
        string='Tồn Kho Tối Thiểu',
        digits=(12, 2),
    )
    is_low_stock = fields.Boolean(
        string='Sắp Hết',
        compute='_compute_is_low_stock',
        store=True,
    )
    active = fields.Boolean(default=True)

    @api.depends('stock_qty', 'min_stock')
    def _compute_is_low_stock(self):
        for rec in self:
            rec.is_low_stock = rec.stock_qty <= rec.min_stock
