{
    'name': 'Garment Base - Quản lý Công ty May',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Module cơ sở cho ngành may - Quản lý vải, phụ liệu, mẫu may',
    'description': """
        Garment Base Module
        ====================
        Module cơ sở cho công ty may bao gồm:
        - Quản lý danh mục vải (Fabric)
        - Quản lý phụ liệu (Accessories/Trims)
        - Quản lý mẫu may / kiểu dáng (Style/Pattern)
        - Quản lý bảng màu (Color)
        - Quản lý bảng size (Size)
        - Quản lý đơn hàng may (Garment Order)
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'stock',
        'purchase',
        'sale_management',
        'mrp',
        'hr',
    ],
    'data': [
        'security/garment_security.xml',
        'security/ir.model.access.csv',
        'data/garment_data.xml',
        'views/fabric_views.xml',
        'views/accessory_views.xml',
        'views/garment_style_views.xml',
        'views/garment_color_views.xml',
        'views/garment_size_views.xml',
        'views/garment_order_views.xml',
        'views/wash_symbol_views.xml',
        'views/audit_log_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
