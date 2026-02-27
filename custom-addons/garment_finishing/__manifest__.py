{
    'name': 'Garment Finishing - Tổ Hoàn Thiện',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quản lý tổ hoàn thiện: cắt chỉ, ủi, gấp xếp, đóng tag/nhãn',
    'description': """
        Module quản lý công đoạn hoàn thiện sau may:
        - Lệnh hoàn thiện liên kết lệnh sản xuất
        - Các công việc: cắt chỉ, ủi (pressing), kiểm hàng, đóng tag/nhãn, gấp xếp
        - Theo dõi sản lượng hoàn thiện theo ngày
        - Phát hiện lỗi ở công đoạn hoàn thiện
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_production',
        'garment_quality',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/finishing_data.xml',
        'views/finishing_order_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
