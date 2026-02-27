from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_subcontractor = fields.Boolean(
        string='Là Đối Tác Gia Công',
        help='Đánh dấu đối tác này là nhà gia công (subcontractor)',
    )
    subcontract_type = fields.Selection([
        ('sewing', 'May (Sewing)'),
        ('cutting', 'Cắt (Cutting)'),
        ('washing', 'Giặt (Washing)'),
        ('embroidery', 'Thêu (Embroidery)'),
        ('printing', 'In (Printing)'),
        ('cmt', 'CMT'),
        ('multi', 'Đa Năng'),
    ], string='Loại Gia Công')

    subcontract_capacity = fields.Integer(
        string='Công Suất (pcs/ngày)',
        help='Năng lực sản xuất ước tính mỗi ngày',
    )
    subcontract_rating = fields.Selection([
        ('a', 'A - Xuất Sắc'),
        ('b', 'B - Tốt'),
        ('c', 'C - Trung Bình'),
        ('d', 'D - Kém'),
    ], string='Xếp Hạng GC')

    subcontract_note = fields.Text(
        string='Ghi Chú Gia Công',
        help='Năng lực, máy móc, chuyên môn, lịch sử hợp tác',
    )

    subcontract_order_ids = fields.One2many(
        'garment.subcontract.order',
        'partner_id',
        string='Đơn Gia Công',
    )
    subcontract_order_count = fields.Integer(
        string='Số Đơn GC',
        compute='_compute_subcontract_count',
    )

    def _compute_subcontract_count(self):
        for partner in self:
            partner.subcontract_order_count = len(partner.subcontract_order_ids)
