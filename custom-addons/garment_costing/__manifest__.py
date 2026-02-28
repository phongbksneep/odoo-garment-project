{
    'name': 'Garment Costing - Tính Giá Thành',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Tính giá thành FOB/CM/CMT cho sản phẩm may',
    'description': """
        Garment Costing Module
        =======================
        Module tính giá thành cho công ty may:
        - Tính giá FOB (Free On Board)
        - Tính giá CM (Cut & Make)
        - Tính giá CMT (Cut, Make & Trim)
        - Phân tích chi phí nguyên phụ liệu
        - Chi phí gia công theo SMV
        - Chi phí thương mại (commission, freight, overhead)
        - So sánh giá thành giữa các phiên bản
        - Load tự động từ BOM
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_production',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/costing_data.xml',
        'views/bom_views.xml',
        'views/cost_sheet_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
