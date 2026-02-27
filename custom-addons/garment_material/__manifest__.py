{
    'name': 'Garment Material Receipt - Nhập Nguyên Liệu',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quản lý nhập nguyên phụ liệu: mua hàng & khách gửi (CMT)',
    'description': """
Garment Material Receipt
========================
Quản lý quy trình nhận nguyên phụ liệu cho sản xuất may:
- Phiếu nhập NL mua hàng (Purchase)
- Phiếu nhập NL khách gửi (Buyer-Supplied / CMT)
- Kiểm tra chất lượng NL đầu vào
- Phân bổ NL cho đơn hàng / lệnh sản xuất
- Theo dõi tồn kho NL theo đơn hàng
- Báo cáo tình hình nhập NL
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_production',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/material_data.xml',
        'views/material_receipt_views.xml',
        'views/material_allocation_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
