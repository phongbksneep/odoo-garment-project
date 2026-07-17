from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestWageGuards(TransactionCase):
    """Guard trạng thái phiếu lương: không xác nhận trước khi tính,
    không reset/xóa phiếu đã trả."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Emp Wage Grd'})

    def _create_wage(self):
        return self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '02',
            'year': 2026,
        })

    def _walk_to_paid(self, wage):
        wage.action_calculate()
        wage.action_confirm()
        wage.action_pay()

    def test_cannot_confirm_before_calculate(self):
        wage = self._create_wage()
        with self.assertRaises(UserError):
            wage.action_confirm()

    def test_happy_path(self):
        wage = self._create_wage()
        self._walk_to_paid(wage)
        self.assertEqual(wage.state, 'paid')

    def test_cannot_pay_twice(self):
        wage = self._create_wage()
        self._walk_to_paid(wage)
        with self.assertRaises(UserError):
            wage.action_pay()

    def test_cannot_reset_paid(self):
        wage = self._create_wage()
        self._walk_to_paid(wage)
        with self.assertRaises(UserError):
            wage.action_reset_draft()

    def test_reset_calculated_ok(self):
        wage = self._create_wage()
        wage.action_calculate()
        wage.action_reset_draft()
        self.assertEqual(wage.state, 'draft')

    def test_cannot_delete_paid(self):
        wage = self._create_wage()
        self._walk_to_paid(wage)
        with self.assertRaises(UserError):
            wage.unlink()

    def test_delete_draft_ok(self):
        wage = self._create_wage()
        wage.unlink()
        self.assertFalse(wage.exists())
