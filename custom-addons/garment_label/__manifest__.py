{
    'name': 'Garment Label & Pallet - In Tem & Quản Lý Pallet',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'In tem QR code, quản lý pallet, đóng/tách thùng hàng',
    'description': """
Garment Label & Pallet Management
===================================
Quản lý in tem và pallet cho công ty may:
- In tem sản phẩm / thùng hàng / pallet (QR Code)
- Quản lý pallet: tạo, gộp, tách pallet
- Quản lý thùng hàng: đóng, gộp, tách thùng (carton)
- Theo dõi sản phẩm / vị trí bằng quét QR code
- Liên kết với packing list, đơn hàng, giao hàng
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_packing',
        'garment_delivery',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/label_data.xml',
        'views/label_views.xml',
        'views/pallet_views.xml',
        'views/carton_management_views.xml',
        'views/delivery_integration_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
