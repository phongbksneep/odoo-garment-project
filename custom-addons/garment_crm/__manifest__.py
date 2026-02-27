{
    'name': 'Garment CRM - Quản Lý Quan Hệ Khách Hàng',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'CRM ngành may: lead, cơ hội, feedback, phản hồi khách hàng',
    'description': """
Garment CRM - Quan Hệ Khách Hàng
==================================
Quản lý quan hệ khách hàng chuyên biệt cho công ty may:
- Quản lý Lead / đầu mối khách hàng
- Pipeline cơ hội kinh doanh (Opportunity)
- Hồ sơ khách hàng: buyer profile, lịch sử đặt hàng
- Phản hồi / khiếu nại từ khách hàng (Feedback/Complaint)
- Theo dõi hoạt động chăm sóc khách hàng
- Báo cáo phân tích khách hàng
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_data.xml',
        'views/crm_lead_views.xml',
        'views/crm_feedback_views.xml',
        'views/customer_profile_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
