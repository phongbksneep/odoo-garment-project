{
    'name': 'Garment Piece-Rate Payroll',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Piece-rate wage calculation for garment workers',
    'description': """
Garment Piece-Rate Payroll
===========================
- Piece rate configuration per operation/style
- Worker daily output tracking
- Monthly wage calculation (base + piece-rate bonus)
- Attendance integration
- Payroll summary reports
    """,
    'author': 'Garment Dev Team',
    'website': '',
    'depends': [
        'garment_base',
        'garment_production',
        'garment_hr',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payroll_data.xml',
        'views/piece_rate_views.xml',
        'views/worker_output_views.xml',
        'views/wage_calculation_views.xml',
        'views/bonus_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
