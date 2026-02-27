{
    'name': 'Garment Machine Maintenance',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Machine registry, preventive maintenance and spare parts',
    'description': """
Garment Machine Maintenance
=============================
- Machine registry with serial numbers and types
- Preventive maintenance schedules
- Breakdown tracking
- Spare parts inventory
- Maintenance request workflow
    """,
    'author': 'Garment Dev Team',
    'website': '',
    'depends': [
        'garment_base',
        'garment_production',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_data.xml',
        'views/machine_views.xml',
        'views/maintenance_request_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
