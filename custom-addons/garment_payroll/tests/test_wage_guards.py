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


@tagged('post_install', '-at_install')
class TestWageBounds(TransactionCase):
    """Các trường nhập của phiếu lương không được âm."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Emp Bounds'})

    def test_negative_base_salary_rejected(self):
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.env['garment.wage.calculation'].create({
                'employee_id': self.employee.id,
                'month': '05',
                'year': 2026,
                'base_salary': -1000,
            })

    def test_negative_ot_rate_rejected(self):
        from odoo.exceptions import ValidationError
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '05',
            'year': 2026,
        })
        with self.assertRaises(ValidationError):
            wage.write({'ot_rate': -5})


@tagged('post_install', '-at_install')
class TestPayrollVietnamRules(TransactionCase):
    """Tính lương theo quy định Việt Nam: OT 150/200/300, trần BHXH,
    miễn thuế phụ cấp/phụ trội OT, giảm trừ gia cảnh 2026."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Emp VN Rules'})

    def _create_wage(self, **kwargs):
        vals = {
            'employee_id': self.employee.id,
            'month': '06',
            'year': 2026,
            'base_salary': 6240000,  # → 240.000đ/ngày, 30.000đ/giờ
            'working_days': 26,
            'actual_days': 26,
        }
        vals.update(kwargs)
        return self.env['garment.wage.calculation'].create(vals)

    def test_hourly_rate_default(self):
        wage = self._create_wage()
        # 6.240.000 / 26 / 8 = 30.000
        self.assertAlmostEqual(wage.hourly_rate, 30000, places=0)

    def test_statutory_ot_multipliers(self):
        """ot_rate=0 → tính 150/200/300% trên đơn giá giờ chuẩn."""
        wage = self._create_wage(
            ot_hours_weekend=4, ot_hours_holiday=2)
        # total_ot_hours = 0 (không có output) → weekday = 0
        # OT = 30.000 × (2.0×4 + 3.0×2) = 30.000 × 14 = 420.000
        self.assertAlmostEqual(wage.ot_amount, 420000, places=0)
        # Miễn thuế = 30.000 × (1.0×4 + 2.0×2) = 240.000
        self.assertAlmostEqual(wage.ot_exempt_amount, 240000, places=0)

    def test_legacy_flat_ot_rate(self):
        """ot_rate>0 → giữ cách tính khoán cũ."""
        wage = self._create_wage(ot_rate=50000)
        self.assertEqual(wage.ot_amount, 0)  # chưa có giờ OT

    def test_insurance_default_base_and_rates(self):
        wage = self._create_wage()
        self.assertAlmostEqual(wage.insurance_base, 6240000, places=0)
        self.assertAlmostEqual(wage.bhxh_employee, 6240000 * 0.08, places=0)
        self.assertAlmostEqual(wage.bhyt_employee, 6240000 * 0.015, places=0)
        self.assertAlmostEqual(wage.bhtn_employee, 6240000 * 0.01, places=0)

    def test_insurance_cap(self):
        """BHXH/BHYT trần 20 lần lương cơ sở (46,8tr với LCS 2,34tr)."""
        wage = self._create_wage(
            base_salary=60000000, insurance_base=60000000)
        cap = 20 * 2340000
        self.assertAlmostEqual(wage.bhxh_employee, cap * 0.08, places=0)
        self.assertAlmostEqual(wage.bhyt_employee, cap * 0.015, places=0)
        # BHTN trần 20 lần lương tối thiểu vùng (99,2tr) — 60tr chưa chạm
        self.assertAlmostEqual(
            wage.bhtn_employee, 60000000 * 0.01, places=0)

    def test_employer_contributions(self):
        wage = self._create_wage()
        base = 6240000
        self.assertAlmostEqual(wage.bhxh_employer, base * 0.175, places=0)
        self.assertAlmostEqual(wage.bhyt_employer, base * 0.03, places=0)
        self.assertAlmostEqual(wage.bhtn_employer, base * 0.01, places=0)
        self.assertAlmostEqual(
            wage.union_fee_employer, base * 0.02, places=0)
        self.assertAlmostEqual(
            wage.total_employer_cost,
            wage.total_wage + base * (0.175 + 0.03 + 0.01 + 0.02),
            places=0)

    def test_personal_deduction_2026(self):
        wage = self._create_wage(dependent_count=2)
        self.assertAlmostEqual(wage.personal_deduction, 15500000, places=0)
        self.assertAlmostEqual(
            wage.dependent_deduction, 2 * 6200000, places=0)

    def test_lunch_allowance_exempt_capped(self):
        wage = self._create_wage(
            allowance_lunch=1000000, allowance_phone=200000)
        # Ăn trưa miễn tới 730k, điện thoại miễn toàn bộ
        self.assertAlmostEqual(
            wage.tax_exempt_allowance, 730000 + 200000, places=0)

    def test_low_wage_no_pit(self):
        """Công nhân lương 6,24tr — dưới giảm trừ 15,5tr → không chịu thuế."""
        wage = self._create_wage()
        self.assertEqual(wage.taxable_income, 0)
        self.assertEqual(wage.pit_amount, 0)

    def test_paid_leave_pulled_into_wage(self):
        """Phép năm đã duyệt trong tháng được cộng vào ngày hưởng lương."""
        leave = self.env['garment.leave'].create({
            'employee_id': self.employee.id,
            'leave_type': 'annual',
            'date_from': '2026-06-10',
            'date_to': '2026-06-12',
        })
        leave.action_submit()
        leave.action_approve()
        wage = self._create_wage(actual_days=23)
        wage.action_calculate()
        self.assertAlmostEqual(wage.paid_leave_days, 3, places=1)
        # base = 6.240.000/26 × (23 + 3) = 6.240.000
        self.assertAlmostEqual(wage.base_amount, 6240000, places=0)

    def test_unpaid_leave_not_counted(self):
        leave = self.env['garment.leave'].create({
            'employee_id': self.employee.id,
            'leave_type': 'unpaid',
            'date_from': '2026-06-15',
            'date_to': '2026-06-16',
        })
        leave.action_submit()
        leave.action_approve()
        wage = self._create_wage()
        wage.action_calculate()
        self.assertEqual(wage.paid_leave_days, 0)


@tagged('post_install', '-at_install')
class TestBhxhBenefit(TransactionCase):
    """Trợ cấp BHXH: ốm 75%, thai sản 100% mức đóng/24 ngày."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Emp BHXH Ben'})

    def _create_wage(self, **kwargs):
        vals = {
            'employee_id': self.employee.id,
            'month': '06',
            'year': 2026,
            'base_salary': 7200000,  # mức đóng/ngày = 300.000
            'working_days': 26,
        }
        vals.update(kwargs)
        return self.env['garment.wage.calculation'].create(vals)

    def test_sick_benefit_75_percent(self):
        wage = self._create_wage(sick_leave_days=4)
        # 7.200.000/24 × 75% × 4 = 900.000
        self.assertAlmostEqual(wage.bhxh_benefit_amount, 900000, places=0)

    def test_maternity_benefit_100_percent(self):
        wage = self._create_wage(maternity_leave_days=24)
        # 7.200.000/24 × 100% × 24 = 7.200.000
        self.assertAlmostEqual(wage.bhxh_benefit_amount, 7200000, places=0)

    def test_benefit_added_to_net_not_taxed(self):
        wage = self._create_wage(sick_leave_days=4, actual_days=22)
        base_net_wo_benefit = (wage.total_wage - wage.total_insurance
                               - wage.pit_amount - wage.deduction)
        self.assertAlmostEqual(
            wage.net_pay, base_net_wo_benefit + 900000, places=0)
        # Không nằm trong thu nhập chịu thuế
        self.assertNotIn(wage.bhxh_benefit_amount, [wage.taxable_income])

    def test_sick_leave_pulled_on_calculate(self):
        leave = self.env['garment.leave'].create({
            'employee_id': self.employee.id,
            'leave_type': 'sick',
            'date_from': '2026-06-08',
            'date_to': '2026-06-09',
        })
        leave.action_submit()
        leave.action_approve()
        wage = self._create_wage(actual_days=24)
        wage.action_calculate()
        self.assertAlmostEqual(wage.sick_leave_days, 2, places=1)
        # Nghỉ ốm KHÔNG cộng vào ngày hưởng lương công ty
        self.assertEqual(wage.paid_leave_days, 0)
