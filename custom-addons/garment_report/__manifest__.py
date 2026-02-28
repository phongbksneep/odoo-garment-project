{
    'name': 'Garment Report & Analytics',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Production reports, efficiency analysis and dashboards',
    'description': """
Garment Report & Analytics
==========================
- Daily production summary report
- Sewing line efficiency analysis (SQL view)
- Defect rate analysis
- Order delivery tracking
- Dashboard views for management
    """,
    'author': 'Garment Dev Team',
    'website': '',
    'depends': [
        'garment_base',
        'garment_production',
        'garment_quality',
        'garment_costing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/production_report_views.xml',
        'views/efficiency_analysis_views.xml',
        'views/defect_analysis_views.xml',
        'views/cost_analysis_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
