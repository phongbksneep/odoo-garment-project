{
    'name': 'Garment Demo Data - Dữ Liệu Mẫu',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/Garment',
    'summary': 'Dữ liệu mẫu cho toàn bộ hệ thống quản lý may',
    'description': """
Garment Demo Data
=================
Tạo dữ liệu mẫu cho tất cả module:
* Khách hàng, nhà cung cấp
* Nhân viên theo 17 tổ/phòng
* Vải, màu, size, mẫu may
* Đơn hàng, lệnh sản xuất, chuyền may
* Máy may, bảo trì
* Cắt, may, hoàn thiện, giặt, đóng gói
* QC, kiểm tra chất lượng
* Kho, nhập xuất, giao hàng
* Chấm công, lương, thưởng
* Hóa đơn, thanh toán
    """,
    'author': 'Garment Factory',
    'depends': [
        'garment_base',
        'garment_production',
        'garment_quality',
        'garment_cutting',
        'garment_packing',
        'garment_costing',
        'garment_sample',
        'garment_planning',
        'garment_maintenance',
        'garment_compliance',
        'garment_payroll',
        'garment_washing',
        'garment_subcontract',
        'garment_finishing',
        'garment_hr',
        'garment_accounting',
        'garment_warehouse',
        'garment_delivery',
        'garment_report',
    ],
    'data': [
        'demo/demo_base.xml',
        'demo/demo_employees.xml',
        'demo/demo_production.xml',
        'demo/demo_operations.xml',
        'demo/demo_hr_payroll.xml',
        'demo/demo_accounting_delivery.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
