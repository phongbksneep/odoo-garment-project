{
    'name': 'Garment Warehouse - Quản Lý Kho',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Kho nguyên phụ liệu, bán thành phẩm, thành phẩm',
    'description': """
        Quản lý kho chuyên biệt cho công ty may:
        - Phiếu nhập kho (NPL, BTP, TP)
        - Phiếu xuất kho (cho sản xuất, giao hàng)
        - Kiểm kê tồn kho
        - Liên kết đơn hàng / lệnh sản xuất
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_production',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/warehouse_data.xml',
        'views/stock_move_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
