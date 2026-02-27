{
    'name': 'Garment Cutting Advanced - Cắt Nâng Cao',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quản lý cắt nâng cao - Marker, Spreading, Bundle tracking',
    'description': """
        Garment Cutting Advanced Module
        =================================
        Mở rộng chức năng cắt:
        - Sơ đồ cắt (Marker planning)
        - Quản lý trải vải (Fabric spreading)
        - Theo dõi bó hàng (Bundle tracking)
        - Tỷ lệ sử dụng vải (Fabric utilization)
        - Phát hàng xuống chuyền may
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_production',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cutting_data.xml',
        'views/cutting_order_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
