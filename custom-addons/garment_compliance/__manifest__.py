{
    'name': 'Garment Compliance',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'BSCI/WRAP audit tracking and corrective action plans',
    'description': """
Garment Compliance
===================
- Social compliance audit tracking (BSCI, WRAP, SEDEX, SA8000)
- Audit finding and severity management
- Corrective Action Plan (CAP) workflow
- Document/certificate management
- Compliance calendar and reminders
    """,
    'author': 'Garment Dev Team',
    'website': '',
    'depends': [
        'garment_base',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/compliance_data.xml',
        'views/audit_views.xml',
        'views/cap_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
