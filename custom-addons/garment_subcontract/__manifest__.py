{
    'name': 'Garment Subcontract - Quản lý Gia Công',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Gia công may - Gửi gia công & nhận gia công',
    'description': """
        Garment Subcontract Module
        ===========================
        Quản lý gia công may mặc bao gồm:
        - Gửi hàng đi gia công (outsource sewing, washing, embroidery)
        - Nhận hàng gia công từ công ty khác
        - Quản lý đối tác gia công (subcontractors)
        - Theo dõi giao nhận nguyên phụ liệu
        - Kiểm soát chất lượng hàng gia công
        - Chi phí & thanh toán gia công
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_production',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/subcontract_data.xml',
        'views/subcontract_order_views.xml',
        'views/subcontract_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
