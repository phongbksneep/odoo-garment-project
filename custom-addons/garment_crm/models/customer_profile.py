from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # --- Garment-specific buyer profile fields ---
    is_garment_buyer = fields.Boolean(
        string='Là Buyer Ngành May',
        default=False,
    )
    buyer_code = fields.Char(string='Mã Buyer')
    buyer_type = fields.Selection([
        ('brand', 'Thương Hiệu (Brand)'),
        ('retailer', 'Nhà Bán Lẻ'),
        ('importer', 'Nhà Nhập Khẩu'),
        ('agent', 'Đại Lý / Agent'),
        ('wholesaler', 'Bán Sỉ'),
        ('other', 'Khác'),
    ], string='Loại Buyer')

    product_interest = fields.Selection([
        ('shirt', 'Áo Sơ Mi'),
        ('tshirt', 'Áo Thun'),
        ('jacket', 'Áo Khoác'),
        ('pants', 'Quần'),
        ('dress', 'Đầm / Váy'),
        ('uniform', 'Đồng Phục'),
        ('sportswear', 'Đồ Thể Thao'),
        ('mixed', 'Đa Dạng'),
    ], string='Sản Phẩm Quan Tâm')

    annual_volume = fields.Float(
        string='SL Đặt Hàng/Năm (Cái)',
        help='Ước tính sản lượng đặt hàng hàng năm',
    )
    annual_revenue = fields.Float(
        string='Doanh Thu/Năm ($)',
        digits='Product Price',
    )
    payment_term_note = fields.Char(string='Điều Kiện Thanh Toán')
    preferred_incoterm = fields.Selection([
        ('fob', 'FOB'),
        ('cif', 'CIF'),
        ('exw', 'EXW'),
        ('cfr', 'CFR'),
    ], string='Incoterm Ưa Thích')

    compliance_requirements = fields.Text(
        string='Yêu Cầu Tuân Thủ',
        help='BSCI, WRAP, Oeko-Tex, GOTS, etc.',
    )
    quality_standard = fields.Text(
        string='Tiêu Chuẩn Chất Lượng',
        help='AQL level, testing requirements, etc.',
    )

    first_order_date = fields.Date(string='Ngày Đơn Hàng Đầu Tiên')
    last_order_date = fields.Date(string='Ngày Đơn Hàng Gần Nhất')

    # --- Counts ---
    garment_order_count = fields.Integer(
        string='Số Đơn Hàng',
        compute='_compute_garment_counts',
    )
    crm_lead_count = fields.Integer(
        string='Số Lead/Cơ Hội',
        compute='_compute_garment_counts',
    )
    feedback_count = fields.Integer(
        string='Số Phản Hồi',
        compute='_compute_garment_counts',
    )

    def _compute_garment_counts(self):
        for partner in self:
            partner.garment_order_count = self.env['garment.order'].search_count(
                [('customer_id', '=', partner.id)]
            )
            partner.crm_lead_count = self.env['garment.crm.lead'].search_count(
                [('partner_id', '=', partner.id)]
            )
            partner.feedback_count = self.env['garment.crm.feedback'].search_count(
                [('partner_id', '=', partner.id)]
            )

    def action_view_garment_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn Hàng May',
            'res_model': 'garment.order',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id},
        }

    def action_view_crm_leads(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead / Cơ Hội',
            'res_model': 'garment.crm.lead',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_view_feedbacks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phản Hồi Khách Hàng',
            'res_model': 'garment.crm.feedback',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
