from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestReportActions(TransactionCase):
    """Test that all PDF report actions are properly registered."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner Report',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-RPT-001',
            'code': 'ST-RPT-001',
            'category': 'shirt',
        })
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })

    # ------------------------------------------------------------------
    # Packing List Report
    # ------------------------------------------------------------------
    def test_packing_list_report_exists(self):
        """Report action for packing list should exist."""
        report = self.env.ref('garment_print.action_report_packing_list')
        self.assertTrue(report)
        self.assertEqual(report.model, 'garment.packing.list')
        self.assertEqual(report.report_type, 'qweb-pdf')

    def test_packing_list_report_template(self):
        """QWeb template for packing list should be loadable."""
        template = self.env.ref('garment_print.report_packing_list_document')
        self.assertTrue(template)

    def test_packing_list_report_render(self):
        """Packing list PDF should render without error."""
        packing_list = self.env['garment.packing.list'].create({
            'buyer_id': self.partner.id,
            'style_id': self.style.id,
            'ship_mode': 'sea',
            'packing_type': 'ratio',
        })
        size = self.env['garment.size'].search([], limit=1)
        color = self.env['garment.color'].search([], limit=1)
        self.env['garment.carton.line'].create({
            'packing_list_id': packing_list.id,
            'carton_from': 1,
            'carton_to': 10,
            'size_id': size.id if size else False,
            'color_id': color.id if color else False,
            'pcs_per_carton': 20,
            'length_cm': 60,
            'width_cm': 40,
            'height_cm': 30,
            'gross_weight': 12.5,
            'net_weight': 11.0,
        })
        report = self.env.ref('garment_print.action_report_packing_list')
        pdf_content, content_type = report._render_qweb_pdf(report.id, packing_list.ids)
        self.assertTrue(pdf_content)
        self.assertIn(content_type, ('html', 'pdf'))

    # ------------------------------------------------------------------
    # Delivery Order Report
    # ------------------------------------------------------------------
    def test_delivery_order_report_exists(self):
        """Report action for delivery order should exist."""
        report = self.env.ref('garment_print.action_report_delivery_order')
        self.assertTrue(report)
        self.assertEqual(report.model, 'garment.delivery.order')

    def test_delivery_order_report_render(self):
        """Delivery order PDF should render without error."""
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'garment_order_id': self.garment_order.id,
            'shipping_method': 'sea',
            'ship_to': 'Test Destination',
        })
        self.env['garment.delivery.line'].create({
            'delivery_id': delivery.id,
            'style_code': 'ST-001',
            'color': 'Red',
            'size': 'M',
            'quantity': 500,
            'carton_qty': 25,
            'pcs_per_carton': 20,
            'gross_weight': 300.0,
        })
        report = self.env.ref('garment_print.action_report_delivery_order')
        pdf_content, content_type = report._render_qweb_pdf(report.id, delivery.ids)
        self.assertTrue(pdf_content)
        self.assertIn(content_type, ('html', 'pdf'))

    # ------------------------------------------------------------------
    # Invoice Report
    # ------------------------------------------------------------------
    def test_invoice_report_exists(self):
        """Report action for invoice should exist."""
        report = self.env.ref('garment_print.action_report_invoice')
        self.assertTrue(report)
        self.assertEqual(report.model, 'garment.invoice')

    def test_invoice_report_render(self):
        """Invoice PDF should render without error."""
        invoice = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'garment_order_id': self.garment_order.id,
            'date': '2026-03-01',
            'due_date': '2026-04-01',
            'tax_type': '10',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': invoice.id,
            'description': 'T-Shirt FOB',
            'quantity': 1000,
            'unit': 'pcs',
            'unit_price': 5.50,
        })
        report = self.env.ref('garment_print.action_report_invoice')
        pdf_content, content_type = report._render_qweb_pdf(report.id, invoice.ids)
        self.assertTrue(pdf_content)
        self.assertIn(content_type, ('html', 'pdf'))

    # ------------------------------------------------------------------
    # Payslip Report
    # ------------------------------------------------------------------
    def test_payslip_report_exists(self):
        """Report action for payslip should exist."""
        report = self.env.ref('garment_print.action_report_payslip')
        self.assertTrue(report)
        self.assertEqual(report.model, 'garment.wage.calculation')

    def test_payslip_report_render(self):
        """Payslip PDF should render without error."""
        dept = self.env['hr.department'].search([], limit=1)
        if not dept:
            dept = self.env['hr.department'].create({'name': 'Test Dept RPT'})
        employee = self.env['hr.employee'].create({
            'name': 'Test Worker Report',
            'employee_code': 'EMP-RPT-001',
            'department_id': dept.id,
        })
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': employee.id,
            'month': '03',
            'year': 2026,
            'base_salary': 6000000,
            'working_days': 26,
            'actual_days': 24,
        })
        report = self.env.ref('garment_print.action_report_payslip')
        pdf_content, content_type = report._render_qweb_pdf(report.id, wage.ids)
        self.assertTrue(pdf_content)
        self.assertIn(content_type, ('html', 'pdf'))

    # ------------------------------------------------------------------
    # QC Inspection Report
    # ------------------------------------------------------------------
    def test_qc_inspection_report_exists(self):
        """Report action for QC inspection should exist."""
        report = self.env.ref('garment_print.action_report_qc_inspection')
        self.assertTrue(report)
        self.assertEqual(report.model, 'garment.qc.inspection')

    def test_qc_inspection_report_render(self):
        """QC Inspection PDF should render without error."""
        dept = self.env['hr.department'].search([], limit=1)
        if not dept:
            dept = self.env['hr.department'].create({'name': 'Test Dept QC'})
        inspector = self.env['hr.employee'].create({
            'name': 'Test Inspector Report',
            'department_id': dept.id,
        })
        inspection = self.env['garment.qc.inspection'].create({
            'inspection_type': 'inline',
            'garment_order_id': self.garment_order.id,
            'inspector_id': inspector.id,
            'inspected_qty': 100,
            'passed_qty': 95,
        })
        report = self.env.ref('garment_print.action_report_qc_inspection')
        pdf_content, content_type = report._render_qweb_pdf(report.id, inspection.ids)
        self.assertTrue(pdf_content)
        self.assertIn(content_type, ('html', 'pdf'))

    # ------------------------------------------------------------------
    # All reports binding
    # ------------------------------------------------------------------
    def test_all_reports_have_binding(self):
        """All 5 reports should be bound to their models via binding_model_id."""
        report_refs = [
            'garment_print.action_report_packing_list',
            'garment_print.action_report_delivery_order',
            'garment_print.action_report_invoice',
            'garment_print.action_report_payslip',
            'garment_print.action_report_qc_inspection',
        ]
        for ref in report_refs:
            report = self.env.ref(ref)
            self.assertTrue(report.binding_model_id, f"Report {ref} should have binding_model_id")
            self.assertEqual(report.binding_type, 'report', f"Report {ref} should have binding_type='report'")


@tagged('post_install', '-at_install')
class TestFloorReports(TransactionCase):
    """4 mẫu in đi xưởng: lệnh SX, lệnh cắt, bảng lương ký nhận, phiếu NPL."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Buyer FloorRpt', 'customer_rank': 1})
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-FRP-001', 'code': 'ST-FRP-001',
            'category': 'shirt'})
        cls.color = cls.env['garment.color'].create({
            'name': 'Đen FRP', 'code': 'BLK-FRP'})
        cls.size = cls.env['garment.size'].create({
            'name': 'M-FRP', 'code': 'M-FRP', 'size_type': 'letter'})
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id, 'style_id': cls.style.id,
            'unit_price': 5.0})
        cls.env['garment.order.line'].create({
            'order_id': cls.order.id, 'color_id': cls.color.id,
            'size_id': cls.size.id, 'quantity': 500})
        cls.order.action_confirm()

    def _render(self, xmlid, records):
        report = self.env.ref(xmlid)
        pdf, ctype = self.env['ir.actions.report']._render_qweb_pdf(
            report.id, records.ids)
        self.assertTrue(pdf)

    def test_production_order_report(self):
        po = self.env['garment.production.order'].create({
            'garment_order_id': self.order.id, 'planned_qty': 500})
        self._render('garment_print.action_report_production_order', po)

    def test_cutting_order_report(self):
        fabric = self.env['garment.fabric'].create({
            'name': 'Vải FRP', 'code': 'FAB-FRP-01',
            'fabric_type': 'cotton'})
        cut = self.env['garment.cutting.order'].create({
            'production_order_id': self.env[
                'garment.production.order'].create({
                    'garment_order_id': self.order.id,
                    'planned_qty': 500}).id,
            'fabric_id': fabric.id,
            'fabric_length': 100, 'fabric_width': 1.5,
            'planned_qty': 500, 'layers': 50,
        })
        self._render('garment_print.action_report_cutting_order', cut)

    def test_wage_summary_report(self):
        employees = self.env['hr.employee'].create([
            {'name': f'Emp FRP {i}'} for i in range(3)])
        wages = self.env['garment.wage.calculation'].create([{
            'employee_id': emp.id, 'month': '06', 'year': 2026,
            'base_salary': 5200000, 'actual_days': 26,
        } for emp in employees])
        wages.action_calculate()
        self._render('garment_print.action_report_wage_summary', wages)

    def test_material_allocation_report(self):
        alloc = self.env['garment.material.allocation'].create({
            'garment_order_id': self.order.id, 'date': '2026-07-01'})
        self.env['garment.material.allocation.line'].create({
            'allocation_id': alloc.id, 'material_type': 'fabric',
            'description': 'Vải FRP', 'unit': 'm',
            'quantity_required': 100, 'quantity_issued': 100})
        self._render('garment_print.action_report_material_allocation', alloc)
