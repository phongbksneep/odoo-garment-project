{
    'name': 'Garment HR - Nhân Sự & Chấm Công',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Quản lý nhân sự may mặc: chấm công, phòng ban, tay nghề, nghỉ phép',
    'description': """
        Module nhân sự chuyên biệt cho công ty may:
        - Phòng ban: Tổ Cắt, Chuyền May, Tổ Hoàn Thiện, Tổ QC, Xưởng Giặt, Kho, Vận Chuyển, Kế Toán, HC-NS
        - Chấm công hàng ngày (đi muộn, về sớm, vắng)
        - Tổng hợp ngày công tháng → liên kết tính lương
        - Quản lý nghỉ phép, tay nghề công nhân
    """,
    'author': 'Garment ERP Team',
    'depends': [
        'garment_base',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_data.xml',
        'views/attendance_views.xml',
        'views/employee_skill_views.xml',
        'views/leave_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
