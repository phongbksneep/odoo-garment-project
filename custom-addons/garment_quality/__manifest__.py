{
    'name': 'Garment Quality - Kiểm Tra Chất Lượng',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Kiểm tra chất lượng sản phẩm may - QC Inline, Final, AQL',
    'description': """
        Garment Quality Module
        =======================
        Module kiểm tra chất lượng cho công ty may:
        - QC Inline (Kiểm tra trên chuyền)
        - QC Final (Kiểm tra cuối)
        - AQL Inspection (Kiểm tra theo AQL)
        - Quản lý loại lỗi
        - Báo cáo chất lượng
    """,
    'author': 'Garment Company',
    'website': 'https://www.garment-company.com',
    'license': 'LGPL-3',
    'depends': [
        'garment_base',
        'garment_production',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/quality_data.xml',
        'views/defect_type_views.xml',
        'views/qc_inspection_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
