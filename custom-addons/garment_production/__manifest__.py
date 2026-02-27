{
    'name': 'Garment Production - Quản lý Sản Xuất May',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quản lý sản xuất may - Chuyền may, Lệnh sản xuất, Năng suất',
    'description': """
        Garment Production Module
        ==========================
        Module quản lý sản xuất may bao gồm:
        - Quản lý chuyền may (Sewing Line)
        - Lệnh sản xuất may (Production Order)
        - Theo dõi công đoạn: Cắt - May - Hoàn thiện - Ủi - Đóng gói
        - Báo cáo năng suất chuyền
        - Quản lý công nhân theo chuyền
        - Theo dõi tiến độ sản xuất
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_base',
        'mrp',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/production_data.xml',
        'views/sewing_line_views.xml',
        'views/production_order_views.xml',
        'views/cutting_order_views.xml',
        'views/daily_output_views.xml',
        'views/garment_order_progress_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
