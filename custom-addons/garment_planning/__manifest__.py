{
    'name': 'Garment Production Planning',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Production planning, line loading and capacity management',
    'description': """
Garment Production Planning
============================
- Production plan with start/end dates
- Line loading (assign orders to sewing lines)
- Capacity calculation per line
- Auto-schedule based on order priority and line capacity
- Gantt-style overview
    """,
    'author': 'Garment Dev Team',
    'website': '',
    'depends': [
        'garment_base',
        'garment_production',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/planning_data.xml',
        'views/production_plan_views.xml',
        'views/line_loading_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
