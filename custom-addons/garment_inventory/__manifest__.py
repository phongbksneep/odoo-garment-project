{
    'name': 'Garment Inventory - Kiểm Kê Kho',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Kiểm kê kho hàng, quét QR nhập nhanh, đối chiếu tồn kho',
    'description': """
Garment Inventory - Kiểm Kê Kho Hàng
======================================
- Tạo phiên kiểm kê theo kho (NPL, BTP, TP)
- Quét QR Code để nhập sản phẩm nhanh vào phiếu kiểm kê
- So sánh tồn kho lý thuyết vs thực tế
- Tự động tạo phiếu điều chỉnh kho (stock adjustment)
- Lịch sử kiểm kê theo thời gian
- Báo cáo chênh lệch kiểm kê
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'garment_warehouse',
        'garment_label',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/inventory_data.xml',
        'views/inventory_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'garment_inventory/static/src/css/barcode_scanner.css',
            'garment_inventory/static/src/xml/barcode_scanner.xml',
            'garment_inventory/static/src/js/barcode_scanner.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
