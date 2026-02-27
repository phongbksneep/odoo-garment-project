{
    'name': 'Garment Sample - Quản Lý Mẫu',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quản lý mẫu may - Proto, Fit, PP, TOP, Shipment Sample',
    'description': """
        Garment Sample Module
        ======================
        Quản lý quy trình phát triển mẫu:
        - Proto sample (mẫu thiết kế)
        - Fit sample (mẫu thử form)
        - Size set sample (mẫu bộ size)
        - PP sample (mẫu tiền sản xuất)
        - TOP sample (mẫu đầu chuyền)
        - Shipment sample (mẫu giao hàng)
        - Theo dõi comments & approval từ buyer
        - Quản lý revision
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sample_data.xml',
        'views/sample_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
