{
    'name': 'Garment Dashboard - Bảng Điều Khiển',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Dashboard tổng quan: tiến độ SX, đơn hàng, KPI, biểu đồ',
    'description': """
Garment Dashboard
=================
Bảng điều khiển tổng quan cho quản lý nhà máy may:
- Tổng quan đơn hàng: số lượng theo trạng thái
- Tiến độ sản xuất: % hoàn thành, sản lượng ngày
- KPI chuyền may: hiệu suất, tỷ lệ lỗi
- Tình hình giao hàng: đúng hạn / trễ hạn
- Biểu đồ xu hướng sản xuất
- Tình hình nhập nguyên liệu
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_production',
        'garment_quality',
        'garment_delivery',
        'garment_material',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'garment_dashboard/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
