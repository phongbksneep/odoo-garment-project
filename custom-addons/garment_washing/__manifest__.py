{
    'name': 'Garment Washing - Quản lý Xưởng Giặt',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quản lý xưởng giặt - Wash recipe, Wash order, Chemical tracking',
    'description': """
        Garment Washing Module
        =======================
        Quản lý xưởng giặt công nghiệp bao gồm:
        - Quản lý công thức giặt (Wash Recipe)
        - Lệnh giặt nội bộ & nhận giặt bên ngoài
        - Theo dõi quy trình giặt (Wash Process)
        - Quản lý hóa chất giặt (Chemical)
        - Theo dõi nước, năng lượng tiêu thụ
        - Nhận giặt gia công cho công ty khác
        - KPI: tỷ lệ re-wash, thời gian xử lý
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_production',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/washing_data.xml',
        'views/wash_recipe_views.xml',
        'views/wash_order_views.xml',
        'views/wash_chemical_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
