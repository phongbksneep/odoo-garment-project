from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPayrollSecurity(TransactionCase):
    """Công nhân (Level 1) chỉ xem lương của mình, không sửa sản lượng."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.worker_user = cls.env['res.users'].create({
            'name': 'Worker A Security',
            'login': 'worker_a_sec',
            'group_ids': [(6, 0, [
                cls.env.ref('garment_base.group_garment_user').id,
                cls.env.ref('base.group_user').id,
            ])],
        })
        cls.emp_a = cls.env['hr.employee'].create({
            'name': 'Emp A Sec',
            'user_id': cls.worker_user.id,
        })
        cls.emp_b = cls.env['hr.employee'].create({'name': 'Emp B Sec'})
        cls.wage_a = cls.env['garment.wage.calculation'].create({
            'employee_id': cls.emp_a.id, 'month': '01', 'year': 2026,
        })
        cls.wage_b = cls.env['garment.wage.calculation'].create({
            'employee_id': cls.emp_b.id, 'month': '01', 'year': 2026,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-SEC-001',
            'code': 'ST-SEC-001',
            'category': 'shirt',
        })

    def test_worker_sees_only_own_wage(self):
        wages = self.env['garment.wage.calculation'].with_user(
            self.worker_user).search([])
        self.assertEqual(wages, self.wage_a)

    def test_worker_cannot_read_other_wage(self):
        with self.assertRaises(AccessError):
            self.wage_b.with_user(self.worker_user).read(['net_pay'])

    def test_worker_cannot_create_output(self):
        with self.assertRaises(AccessError):
            self.env['garment.worker.output'].with_user(
                self.worker_user).create({
                    'employee_id': self.emp_b.id,
                    'date': '2026-01-05',
                    'style_id': self.style.id,
                    'quantity': 999,
                })

    def test_worker_cannot_write_output(self):
        output = self.env['garment.worker.output'].create({
            'employee_id': self.emp_a.id,
            'date': '2026-01-05',
            'style_id': self.style.id,
            'quantity': 10,
        })
        with self.assertRaises(AccessError):
            output.with_user(self.worker_user).write({'quantity': 9999})
