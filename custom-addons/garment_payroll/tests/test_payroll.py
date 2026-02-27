from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestPayroll(TransactionCase):
    """Unit tests and E2E tests for garment payroll."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Worker Test',
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-PAY-001',
            'code': 'ST-PAY-001',
            'category': 'shirt',
        })
        cls.piece_rate = cls.env['garment.piece.rate'].create({
            'style_id': cls.style.id,
            'operation': 'sewing',
            'operation_detail': 'Full garment',
            'rate_per_piece': 3000,
            'smv': 12.0,
        })
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Line PAY-Test',
            'code': 'LPAY01',
        })

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_piece_rate_creation(self):
        self.assertEqual(self.piece_rate.rate_per_piece, 3000)
        self.assertEqual(self.piece_rate.operation, 'sewing')

    def test_worker_output_amount(self):
        """amount = quantity × rate_per_piece."""
        from datetime import date
        output = self.env['garment.worker.output'].create({
            'date': date.today(),
            'employee_id': self.employee.id,
            'style_id': self.style.id,
            'piece_rate_id': self.piece_rate.id,
            'sewing_line_id': self.sewing_line.id,
            'quantity': 100,
        })
        self.assertEqual(output.amount, 300000)  # 100 × 3000

    def test_wage_base_amount(self):
        """Base amount = base_salary / working_days × actual_days."""
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '01',
            'year': 2024,
            'base_salary': 5200000,
            'working_days': 26,
            'actual_days': 24,
        })
        # 5,200,000 / 26 × 24 = 4,800,000
        self.assertAlmostEqual(wage.base_amount, 4800000, places=0)

    def test_wage_sequence(self):
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '01',
            'year': 2024,
        })
        self.assertTrue(wage.name.startswith('WAGE/'))

    def test_wage_ot_amount(self):
        """OT amount = total_ot_hours × ot_rate."""
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '01',
            'year': 2024,
            'ot_rate': 40000,
        })
        # If no outputs, total_ot_hours = 0
        self.assertEqual(wage.ot_amount, 0)

    def test_cannot_pay_without_confirm(self):
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '01',
            'year': 2024,
        })
        with self.assertRaises(UserError):
            wage.action_pay()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_payroll_workflow(self):
        """E2E: Set rate → record daily output → calculate wage → confirm → pay."""
        from datetime import date

        today = date.today()
        month_str = str(today.month).zfill(2)

        # Step 1: Record daily outputs for the month
        for day_offset in range(5):
            d = today.replace(day=day_offset + 1) if today.day > 5 else today
            try:
                d = today.replace(day=day_offset + 1)
            except ValueError:
                continue
            self.env['garment.worker.output'].create({
                'date': d,
                'employee_id': self.employee.id,
                'style_id': self.style.id,
                'piece_rate_id': self.piece_rate.id,
                'sewing_line_id': self.sewing_line.id,
                'quantity': 80,
                'overtime_hours': 2.0,
            })

        # Step 2: Create wage calculation
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': month_str,
            'year': today.year,
            'base_salary': 5200000,
            'working_days': 26,
            'actual_days': 24,
            'ot_rate': 40000,
            'allowance': 500000,
            'deduction': 100000,
        })

        # Step 3: Calculate
        wage.action_calculate()
        self.assertEqual(wage.state, 'calculated')
        self.assertGreater(wage.total_pieces, 0)
        self.assertGreater(wage.piece_rate_amount, 0)
        self.assertGreater(wage.total_wage, 0)

        # Step 4: Confirm
        wage.action_confirm()
        self.assertEqual(wage.state, 'confirmed')

        # Step 5: Pay
        wage.action_pay()
        self.assertEqual(wage.state, 'paid')
