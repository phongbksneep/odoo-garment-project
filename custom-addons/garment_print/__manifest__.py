{
    'name': 'Garment Print & Export - In Ấn & Xuất Dữ Liệu',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/Garment',
    'summary': 'In PDF (Packing List, Phiếu Giao, Hóa Đơn, Bảng Lương, Phiếu QC) & Xuất Excel',
    'description': """
Garment Print & Export
======================
* In PDF (QWeb Report): Packing List, Delivery Order, Invoice, Payslip, QC Inspection
* Xuất Excel: Bảng lương tổng hợp, Báo cáo sản xuất, Chấm công
* Cảnh báo tự động (Scheduled Actions): Đơn trễ hạn, QC fail rate cao
    """,
    'author': 'Garment ERP Team',
    'license': 'LGPL-3',
    'depends': [
        'garment_base',
        'garment_packing',
        'garment_delivery',
        'garment_accounting',
        'garment_payroll',
        'garment_quality',
        'garment_production',
        'garment_hr',
        'garment_material',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/report_packing_list.xml',
        'report/report_delivery_order.xml',
        'report/report_invoice.xml',
        'report/report_payslip.xml',
        'report/report_qc_inspection.xml',
        'wizard/export_payroll_views.xml',
        'wizard/export_production_views.xml',
        'data/scheduled_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
