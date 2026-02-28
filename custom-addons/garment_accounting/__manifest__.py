{
    'name': 'Garment Accounting VN - Kế Toán May Việt Nam',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Kế toán may mặc Việt Nam: thuế GTGT, hóa đơn, công nợ, tích hợp sale/purchase',
    'description': """
        Module kế toán cho công ty may theo chuẩn Việt Nam:
        - Hóa đơn bán hàng (xuất khẩu / nội địa)
        - Hóa đơn mua hàng (NPL, gia công)
        - Thuế GTGT: 0% (xuất khẩu), 5%, 8%, 10%
        - Quản lý công nợ phải thu / phải trả
        - Liên kết đơn hàng may → hóa đơn
        - Tích hợp Odoo Sale Order / Purchase Order / Account Move
        - Báo cáo tài chính cơ bản
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_material',
        'account',
        'sale_management',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/accounting_data.xml',
        'views/invoice_views.xml',
        'views/payment_views.xml',
        'views/integration_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
