{
    'name': 'Garment Delivery - Giao Hàng & Vận Chuyển',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/Garment',
    'summary': 'Quản lý giao hàng, vận chuyển, phương tiện - Tổ Lái Xe',
    'description': """
Garment Delivery Management - Quản Lý Giao Hàng Vận Chuyển
===========================================================
* Quản lý phương tiện vận chuyển
* Phiếu giao hàng (Delivery Note)
* Liên kết với đơn hàng may, đóng gói
* Theo dõi trạng thái giao hàng
* Lịch sử vận chuyển
    """,
    'author': 'Garment Factory',
    'depends': [
        'garment_base',
        'garment_packing',
        'garment_warehouse',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_data.xml',
        'views/vehicle_views.xml',
        'views/delivery_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
