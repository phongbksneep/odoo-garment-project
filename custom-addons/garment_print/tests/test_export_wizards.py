import base64

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestExportPayrollWizard(TransactionCase):
    """Test Excel payroll export wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department = cls.env['hr.department'].search([], limit=1)
        if not cls.department:
            cls.department = cls.env['hr.department'].create({'name': 'Sewing Dept Export'})
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Worker Export',
            'employee_code': 'EMP-EXP-001',
            'department_id': cls.department.id,
        })
        # Create a wage calculation record
        cls.wage = cls.env['garment.wage.calculation'].create({
            'employee_id': cls.employee.id,
            'month': '03',
            'year': 2026,
            'base_salary': 6000000,
            'working_days': 26,
            'actual_days': 24,
        })

    def test_wizard_create(self):
        """Wizard should be creatable with default values."""
        wizard = self.env['garment.export.payroll.wizard'].create({
            'month': '03',
            'year': 2026,
        })
        self.assertEqual(wizard.month, '03')
        self.assertEqual(wizard.year, 2026)

    def test_wizard_export_generates_file(self):
        """Export should generate an Excel file."""
        wizard = self.env['garment.export.payroll.wizard'].create({
            'month': '03',
            'year': 2026,
        })
        result = wizard.action_export()
        # After export, file_data should be set
        self.assertTrue(wizard.file_data, "Excel file should be generated")
        self.assertTrue(wizard.file_name)
        self.assertIn('.xlsx', wizard.file_name)
        # File data should be valid base64
        raw = base64.b64decode(wizard.file_data)
        # XLSX files start with PK (ZIP header)
        self.assertTrue(raw[:2] == b'PK', "File should be a valid XLSX (ZIP format)")

    def test_wizard_export_with_department_filter(self):
        """Export with department filter should work."""
        wizard = self.env['garment.export.payroll.wizard'].create({
            'month': '03',
            'year': 2026,
            'department_ids': [(6, 0, [self.department.id])],
        })
        result = wizard.action_export()
        self.assertTrue(wizard.file_data)

    def test_wizard_export_empty_data(self):
        """Export with no matching data should raise UserError."""
        wizard = self.env['garment.export.payroll.wizard'].create({
            'month': '12',
            'year': 2099,
        })
        with self.assertRaises(UserError):
            wizard.action_export()

    def test_wizard_returns_action(self):
        """Export should return a window action to download the file."""
        wizard = self.env['garment.export.payroll.wizard'].create({
            'month': '03',
            'year': 2026,
        })
        result = wizard.action_export()
        self.assertEqual(result.get('type'), 'ir.actions.act_window')
        self.assertEqual(result.get('res_model'), 'garment.export.payroll.wizard')


@tagged('post_install', '-at_install')
class TestExportProductionWizard(TransactionCase):
    """Test Excel production export wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sewing_line = cls.env['garment.sewing.line'].search([], limit=1)
        if not cls.sewing_line:
            cls.sewing_line = cls.env['garment.sewing.line'].create({
                'name': 'Line Export Test',
                'code': 'LN-EXP-01',
            })
        # Create production order and daily output
        cls.partner = cls.env['res.partner'].create({'name': 'Test Buyer Prod Export'})
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-EXP-001',
            'code': 'ST-EXP-001',
            'category': 'shirt',
        })
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })
        cls.prod_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.garment_order.id,
            'sewing_line_id': cls.sewing_line.id,
            'planned_qty': 500,
        })
        cls.daily_output = cls.env['garment.daily.output'].create({
            'production_order_id': cls.prod_order.id,
            'date': '2026-03-15',
            'target_qty': 200,
            'output_qty': 180,
            'defect_qty': 5,
        })

    def test_wizard_create(self):
        """Production wizard should be creatable."""
        wizard = self.env['garment.export.production.wizard'].create({
            'date_from': '2026-03-01',
            'date_to': '2026-03-31',
        })
        self.assertTrue(wizard)

    def test_wizard_export_generates_file(self):
        """Export should generate an Excel file."""
        wizard = self.env['garment.export.production.wizard'].create({
            'date_from': '2026-03-01',
            'date_to': '2026-03-31',
        })
        result = wizard.action_export()
        self.assertTrue(wizard.file_data)
        self.assertIn('.xlsx', wizard.file_name)
        raw = base64.b64decode(wizard.file_data)
        self.assertTrue(raw[:2] == b'PK')

    def test_wizard_export_with_line_filter(self):
        """Export with sewing line filter should work."""
        wizard = self.env['garment.export.production.wizard'].create({
            'date_from': '2026-03-01',
            'date_to': '2026-03-31',
            'sewing_line_ids': [(6, 0, [self.sewing_line.id])],
        })
        result = wizard.action_export()
        self.assertTrue(wizard.file_data)

    def test_wizard_export_empty_data(self):
        """Export with no matching data should raise UserError."""
        wizard = self.env['garment.export.production.wizard'].create({
            'date_from': '2099-01-01',
            'date_to': '2099-01-31',
        })
        with self.assertRaises(UserError):
            wizard.action_export()
