{
    'name': 'Garment Packing - Đóng Gói Xuất Hàng',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Đóng gói và xuất hàng - Packing list, Carton management',
    'description': """
        Garment Packing Module
        =======================
        Quản lý đóng gói xuất hàng:
        - Packing list theo tỷ lệ size/màu
        - Quản lý thùng carton
        - Solid pack / Ratio pack / Assorted pack
        - Theo dõi xuất hàng (shipment)
        - Tính toán CBM, trọng lượng
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
        'data/packing_data.xml',
        'views/packing_list_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
