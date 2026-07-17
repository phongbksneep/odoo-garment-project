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


@tagged('post_install', '-at_install')
class TestWageBatchCompute(TransactionCase):
    """Tính sản lượng gộp theo batch phải khớp với tính theo từng nhân viên."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.emp_1 = cls.env['hr.employee'].create({'name': 'Emp Batch 1'})
        cls.emp_2 = cls.env['hr.employee'].create({'name': 'Emp Batch 2'})
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-BATCH-001',
            'code': 'ST-BATCH-001',
            'category': 'shirt',
        })
        cls.rate_2000 = cls.env['garment.piece.rate'].create({
            'style_id': cls.style.id,
            'operation': 'sewing',
            'operation_detail': 'Batch rate 2000',
            'rate_per_piece': 2000,
            'smv': 10.0,
        })
        cls.rate_3000 = cls.env['garment.piece.rate'].create({
            'style_id': cls.style.id,
            'operation': 'finishing',
            'operation_detail': 'Batch rate 3000',
            'rate_per_piece': 3000,
            'smv': 12.0,
        })
        Output = cls.env['garment.worker.output']
        Output.create([
            {'employee_id': cls.emp_1.id, 'date': '2026-03-05',
             'style_id': cls.style.id, 'quantity': 100,
             'piece_rate_id': cls.rate_2000.id, 'overtime_hours': 1.5},
            {'employee_id': cls.emp_1.id, 'date': '2026-03-20',
             'style_id': cls.style.id, 'quantity': 50,
             'piece_rate_id': cls.rate_2000.id, 'overtime_hours': 0.5},
            # Khác tháng — không được tính vào 03/2026
            {'employee_id': cls.emp_1.id, 'date': '2026-04-01',
             'style_id': cls.style.id, 'quantity': 999,
             'piece_rate_id': cls.rate_2000.id},
            {'employee_id': cls.emp_2.id, 'date': '2026-03-10',
             'style_id': cls.style.id, 'quantity': 70,
             'piece_rate_id': cls.rate_3000.id, 'overtime_hours': 2.0},
        ])

    def test_batch_totals_match(self):
        wages = self.env['garment.wage.calculation'].create([
            {'employee_id': self.emp_1.id, 'month': '03', 'year': 2026},
            {'employee_id': self.emp_2.id, 'month': '03', 'year': 2026},
        ])
        w1 = wages.filtered(lambda w: w.employee_id == self.emp_1)
        w2 = wages.filtered(lambda w: w.employee_id == self.emp_2)
        self.assertEqual(w1.total_pieces, 150)
        self.assertAlmostEqual(w1.piece_rate_amount, 300000)
        self.assertAlmostEqual(w1.total_ot_hours, 2.0)
        self.assertEqual(w2.total_pieces, 70)
        self.assertAlmostEqual(w2.piece_rate_amount, 210000)
        self.assertAlmostEqual(w2.total_ot_hours, 2.0)
