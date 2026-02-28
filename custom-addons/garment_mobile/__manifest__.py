{
    'name': 'Garment Mobile — Responsive & Mobile Optimization',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Mobile-responsive views, touch-friendly UI, quick actions for phone users',
    'description': """
Garment Mobile Optimization
============================
Tối ưu giao diện cho điện thoại và máy tính bảng:

- **Responsive CSS**: Media queries cho tất cả garment views
- **Touch-friendly buttons**: Nút bấm kích thước phù hợp ngón tay (min 44px)
- **Card-based mobile views**: Hiển thị dạng thẻ thay vì bảng trên mobile
- **Quick Actions**: Nút hành động nhanh cho các tác vụ phổ biến
- **Mobile Dashboard**: OWL component KPI tối ưu cho mobile
- **Swipe-friendly**: Hỗ trợ vuốt ngang/dọc trên mobile
- **Approval Workflow**: Luồng duyệt đơn hàng với nút bấm mobile-friendly
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_production',
        'garment_quality',
        'garment_dashboard',
        'garment_hr',
        'garment_delivery',
        'garment_packing',
        'garment_inventory',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mobile_dashboard_views.xml',
        'views/approval_views.xml',
        'views/mobile_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'garment_mobile/static/src/css/mobile_responsive.css',
            'garment_mobile/static/src/css/mobile_dashboard.css',
            'garment_mobile/static/src/xml/mobile_dashboard.xml',
            'garment_mobile/static/src/js/mobile_dashboard.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
