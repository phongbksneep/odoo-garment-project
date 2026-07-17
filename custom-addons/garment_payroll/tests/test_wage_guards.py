from odoo.exceptions import UserError, ValidationError
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


@tagged('post_install', '-at_install')
class TestFlexOptions(TransactionCase):
    """Tùy chọn giảm/tắt phúc lợi: hệ số OT, thuế, BHXH per-employee."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.emp_bhxh = cls.env['hr.employee'].create({
            'name': 'Emp Flex BHXH'})
        cls.emp_no_bhxh = cls.env['hr.employee'].create({
            'name': 'Emp Flex NoBHXH', 'has_social_insurance': False})
        cls.icp = cls.env['ir.config_parameter'].sudo()

    def _create_wage(self, employee, **kwargs):
        vals = {
            'employee_id': employee.id,
            'month': '06',
            'year': 2026,
            'base_salary': 6240000,
            'working_days': 26,
            'actual_days': 26,
        }
        vals.update(kwargs)
        return self.env['garment.wage.calculation'].create(vals)

    def test_employee_without_insurance(self):
        wage = self._create_wage(self.emp_no_bhxh, sick_leave_days=3)
        self.assertFalse(wage.apply_insurance)
        self.assertEqual(wage.total_insurance, 0)
        self.assertEqual(wage.bhxh_employer, 0)
        self.assertEqual(wage.bhxh_benefit_amount, 0)

    def test_custom_ot_multipliers(self):
        """Công ty giảm hệ số OT xuống 1.2/1.5/2.0."""
        self.icp.set_param('garment_payroll.ot_mult_weekday', '1.2')
        self.icp.set_param('garment_payroll.ot_mult_weekend', '1.5')
        self.icp.set_param('garment_payroll.ot_mult_holiday', '2.0')
        wage = self._create_wage(
            self.emp_bhxh, ot_hours_weekend=4, ot_hours_holiday=2)
        # hourly = 30.000; OT = 30.000 × (1.5×4 + 2.0×2) = 300.000
        self.assertAlmostEqual(wage.ot_amount, 300000, places=0)
        # Miễn thuế = 30.000 × (0.5×4 + 1.0×2) = 120.000
        self.assertAlmostEqual(wage.ot_exempt_amount, 120000, places=0)

    def test_pit_disabled(self):
        self.icp.set_param('garment_payroll.pit_enabled', 'False')
        wage = self._create_wage(
            self.emp_bhxh, base_salary=40000000, insurance_base=40000000)
        self.assertGreater(wage.taxable_income, 0)
        self.assertEqual(wage.pit_amount, 0)

    def test_pit_enabled_default(self):
        wage = self._create_wage(
            self.emp_bhxh, base_salary=40000000, insurance_base=40000000)
        self.assertGreater(wage.pit_amount, 0)


@tagged('post_install', '-at_install')
class TestPayrollReportWizards(TransactionCase):
    """Wizard xuất bảng kê BHXH và tổng hợp TNCN."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Emp Report Wiz'})
        cls.wage = cls.env['garment.wage.calculation'].create({
            'employee_id': cls.employee.id,
            'month': '05',
            'year': 2026,
            'base_salary': 8000000,
            'working_days': 26,
            'actual_days': 26,
        })
        cls.wage.action_calculate()

    def test_bhxh_export(self):
        wizard = self.env['garment.bhxh.report.wizard'].create({
            'month': '05', 'year': 2026})
        wizard.action_export()
        self.assertTrue(wizard.file_data)
        self.assertEqual(wizard.file_name, 'BHXH_05_2026.xlsx')

    def test_bhxh_export_no_data_raises(self):
        from odoo.exceptions import UserError
        wizard = self.env['garment.bhxh.report.wizard'].create({
            'month': '01', 'year': 2020})
        with self.assertRaises(UserError):
            wizard.action_export()

    def test_pit_annual_export(self):
        wizard = self.env['garment.pit.annual.wizard'].create({
            'year': 2026})
        wizard.action_export()
        self.assertTrue(wizard.file_data)
        self.assertEqual(wizard.file_name, 'TNCN_2026.xlsx')


@tagged('post_install', '-at_install')
class TestPayrollDataLocks(TransactionCase):
    """Snapshot đơn giá + khóa dữ liệu khi lương đã chốt."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Emp Lock'})
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-LOCK-001', 'code': 'ST-LOCK-001',
            'category': 'shirt'})
        cls.rate = cls.env['garment.piece.rate'].create({
            'style_id': cls.style.id,
            'operation': 'sewing',
            'operation_detail': 'Lock test',
            'rate_per_piece': 5000,
            'smv': 10.0,
        })

    def _create_output(self, date='2026-04-05', qty=100):
        return self.env['garment.worker.output'].create({
            'employee_id': self.employee.id,
            'date': date,
            'style_id': self.style.id,
            'piece_rate_id': self.rate.id,
            'quantity': qty,
        })

    def test_rate_edit_does_not_rewrite_history(self):
        """Sửa đơn giá gốc KHÔNG được viết lại sản lượng đã ghi nhận."""
        output = self._create_output()
        self.assertAlmostEqual(output.amount, 500000, places=0)
        self.rate.write({'rate_per_piece': 9000})
        self.assertAlmostEqual(output.rate_per_piece, 5000, places=0)
        self.assertAlmostEqual(output.amount, 500000, places=0)
        # Sản lượng MỚI lấy đơn giá mới
        new_output = self._create_output(date='2026-04-06')
        self.assertAlmostEqual(new_output.rate_per_piece, 9000, places=0)

    def test_output_locked_after_wage_confirmed(self):
        output = self._create_output()
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '04', 'year': 2026,
            'base_salary': 5200000,
        })
        wage.action_calculate()
        wage.action_confirm()
        with self.assertRaises(UserError):
            output.write({'quantity': 999})
        with self.assertRaises(UserError):
            output.unlink()
        with self.assertRaises(UserError):
            self._create_output(date='2026-04-20')

    def test_wage_unique_per_period(self):
        from odoo.tools import mute_logger
        self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id, 'month': '03', 'year': 2026})
        with self.assertRaises(Exception), \
                self.env.cr.savepoint(), mute_logger('odoo.sql_db'):
            self.env['garment.wage.calculation'].create({
                'employee_id': self.employee.id,
                'month': '03', 'year': 2026})
            self.env.flush_all()

    def test_bonus_flows_into_wage(self):
        bonus = self.env['garment.bonus'].create({
            'bonus_type': 'productivity',
            'date': '2026-04-15',
            'year': 2026,
            'line_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'amount': 1500000,
            })],
        })
        bonus.action_confirm()
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '04', 'year': 2026,
            'base_salary': 5200000,
        })
        wage.action_calculate()
        self.assertAlmostEqual(wage.bonus_amount, 1500000, places=0)

    def test_department_snapshot(self):
        """Chuyển phòng ban không viết lại phiếu lương cũ."""
        dept_a = self.env['hr.department'].create({'name': 'Chuyền A Lock'})
        dept_b = self.env['hr.department'].create({'name': 'Chuyền B Lock'})
        self.employee.department_id = dept_a
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id, 'month': '02', 'year': 2026})
        self.assertEqual(wage.department_id, dept_a)
        self.employee.department_id = dept_b
        self.assertEqual(wage.department_id, dept_a)


@tagged('post_install', '-at_install')
class TestLeaveWageLock(TransactionCase):
    """Không duyệt/từ chối phép khi lương tháng đó đã chốt."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Emp LeaveLock', 'join_date': '2024-01-01'})

    def test_cannot_approve_leave_after_wage_confirmed(self):
        wage = self.env['garment.wage.calculation'].create({
            'employee_id': self.employee.id,
            'month': '05', 'year': 2026,
            'base_salary': 5200000,
        })
        wage.action_calculate()
        wage.action_confirm()
        leave = self.env['garment.leave'].create({
            'employee_id': self.employee.id,
            'leave_type': 'annual',
            'date_from': '2026-05-11',
            'date_to': '2026-05-12',
        })
        leave.action_submit()
        with self.assertRaises(ValidationError):
            leave.action_approve()


@tagged('post_install', '-at_install')
class TestWageBatchWizard(TransactionCase):
    """Tạo bảng lương hàng loạt + tính lương theo batch."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dept = cls.env['hr.department'].create({'name': 'Chuyền Batch W'})
        cls.employees = cls.env['hr.employee'].create([
            {'name': f'Emp BatchW {i}', 'department_id': cls.dept.id}
            for i in range(5)
        ])
        # Nhân viên 0 có phiếu tháng trước để test chép số liệu
        cls.env['garment.wage.calculation'].create({
            'employee_id': cls.employees[0].id,
            'month': '06', 'year': 2026,
            'base_salary': 6500000,
            'dependent_count': 2,
            'allowance_lunch': 700000,
        })

    def test_batch_generate_and_calculate(self):
        wizard = self.env['garment.wage.batch.wizard'].create({
            'month': '07', 'year': 2026,
            'department_ids': [(6, 0, [self.dept.id])],
            'auto_calculate': True,
        })
        result = wizard.action_generate()
        wages = self.env['garment.wage.calculation'].search(
            result['domain'])
        self.assertEqual(len(wages), 5)
        self.assertTrue(all(w.state == 'calculated' for w in wages))
        # Số liệu chép từ tháng trước
        w0 = wages.filtered(lambda w: w.employee_id == self.employees[0])
        self.assertAlmostEqual(w0.base_salary, 6500000, places=0)
        self.assertEqual(w0.dependent_count, 2)
        self.assertAlmostEqual(w0.allowance_lunch, 700000, places=0)

    def test_batch_skips_existing(self):
        self.env['garment.wage.calculation'].create({
            'employee_id': self.employees[1].id,
            'month': '08', 'year': 2026,
        })
        wizard = self.env['garment.wage.batch.wizard'].create({
            'month': '08', 'year': 2026,
            'department_ids': [(6, 0, [self.dept.id])],
            'auto_calculate': False,
        })
        result = wizard.action_generate()
        wages = self.env['garment.wage.calculation'].search(result['domain'])
        self.assertEqual(len(wages), 4)  # bỏ qua người đã có

    def test_multi_record_action_calculate(self):
        wages = self.env['garment.wage.calculation'].create([
            {'employee_id': emp.id, 'month': '09', 'year': 2026,
             'base_salary': 5200000, 'actual_days': 26}
            for emp in self.employees
        ])
        wages.action_calculate()  # batch, không còn ensure_one
        self.assertTrue(all(w.state == 'calculated' for w in wages))
        self.assertTrue(all(w.base_amount > 0 for w in wages))


@tagged('post_install', '-at_install')
class TestWorkerOutputCopy(TransactionCase):
    """Chép sản lượng hôm trước với SL=0."""

    def test_copy_previous_day(self):
        style = self.env['garment.style'].create({
            'name': 'STYLE-CPY-001', 'code': 'ST-CPY-001',
            'category': 'shirt'})
        rate = self.env['garment.piece.rate'].create({
            'style_id': style.id, 'operation': 'sewing',
            'operation_detail': 'Copy test', 'rate_per_piece': 4000,
            'smv': 10.0})
        line = self.env['garment.sewing.line'].create({
            'name': 'Line Copy', 'code': 'LCPY'})
        employees = self.env['hr.employee'].create([
            {'name': f'Emp Copy {i}'} for i in range(3)])
        self.env['garment.worker.output'].create([{
            'employee_id': emp.id, 'date': '2026-07-01',
            'sewing_line_id': line.id, 'style_id': style.id,
            'piece_rate_id': rate.id, 'quantity': 50,
        } for emp in employees])
        wizard = self.env['garment.worker.output.copy.wizard'].create({
            'date': '2026-07-02', 'sewing_line_id': line.id})
        result = wizard.action_copy()
        rows = self.env['garment.worker.output'].search(result['domain'])
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r.quantity == 0 for r in rows))
        self.assertTrue(all(r.piece_rate_id == rate for r in rows))
        self.assertTrue(all(r.rate_per_piece == 4000 for r in rows))


@tagged('post_install', '-at_install')
class TestDailyOutputFill(TransactionCase):
    """Lấy tổng sản lượng chuyền từ sản lượng công nhân."""

    def test_fill_from_worker_output(self):
        partner = self.env['res.partner'].create({
            'name': 'Buyer Fill', 'customer_rank': 1})
        style = self.env['garment.style'].create({
            'name': 'STYLE-FILL-001', 'code': 'ST-FILL-001',
            'category': 'shirt'})
        color = self.env['garment.color'].create({
            'name': 'Đen Fill', 'code': 'BLK-FILL'})
        size = self.env['garment.size'].create({
            'name': 'M-FILL', 'code': 'M-FILL', 'size_type': 'letter'})
        order = self.env['garment.order'].create({
            'customer_id': partner.id, 'style_id': style.id,
            'unit_price': 5.0})
        self.env['garment.order.line'].create({
            'order_id': order.id, 'color_id': color.id,
            'size_id': size.id, 'quantity': 1000})
        order.action_confirm()
        line = self.env['garment.sewing.line'].create({
            'name': 'Line Fill', 'code': 'LFIL'})
        po = self.env['garment.production.order'].create({
            'garment_order_id': order.id,
            'sewing_line_id': line.id,
            'planned_qty': 500})
        rate = self.env['garment.piece.rate'].create({
            'style_id': style.id, 'operation': 'sewing',
            'operation_detail': 'Fill', 'rate_per_piece': 3000,
            'smv': 10.0})
        for i in range(3):
            emp = self.env['hr.employee'].create({
                'name': f'Emp Fill {i}', 'sewing_line_id': line.id})
            self.env['garment.worker.output'].create({
                'employee_id': emp.id, 'date': '2026-07-03',
                'sewing_line_id': line.id, 'style_id': style.id,
                'piece_rate_id': rate.id, 'quantity': 40})
            self.env['garment.attendance'].create({
                'employee_id': emp.id, 'date': '2026-07-03',
                'status': 'present', 'work_hours': 8})
        daily = self.env['garment.daily.output'].create({
            'production_order_id': po.id,
            'date': '2026-07-03',
            'output_qty': 0, 'shift': 'morning'})
        daily.action_fill_from_worker_output()
        self.assertEqual(daily.output_qty, 120)
        self.assertEqual(daily.worker_count, 3)


@tagged('post_install', '-at_install')
class TestWorkerOutputPaste(TransactionCase):
    """Dán sản lượng cuối ca từ Excel."""

    def test_paste_outputs(self):
        style = self.env['garment.style'].create({
            'name': 'STYLE-PST-001', 'code': 'ST-PST-001',
            'category': 'shirt'})
        rate = self.env['garment.piece.rate'].create({
            'style_id': style.id, 'operation': 'sewing',
            'operation_detail': 'Paste', 'rate_per_piece': 3500,
            'smv': 10.0})
        e1 = self.env['hr.employee'].create({
            'name': 'Emp Paste 1', 'employee_code': 'PST01'})
        e2 = self.env['hr.employee'].create({'name': 'Emp Paste 2'})
        wizard = self.env['garment.worker.output.paste.wizard'].create({
            'date': '2026-07-05',
            'style_id': style.id,
            'piece_rate_id': rate.id,
            'paste_text': "PST01\t120\nEmp Paste 2\t95\n",
        })
        result = wizard.action_import()
        rows = self.env['garment.worker.output'].search(result['domain'])
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            rows.filtered(lambda r: r.employee_id == e1).quantity, 120)
        self.assertEqual(
            rows.filtered(lambda r: r.employee_id == e2).quantity, 95)

    def test_paste_unknown_employee_rejected(self):
        style = self.env['garment.style'].create({
            'name': 'STYLE-PST-002', 'code': 'ST-PST-002',
            'category': 'shirt'})
        rate = self.env['garment.piece.rate'].create({
            'style_id': style.id, 'operation': 'sewing',
            'operation_detail': 'Paste2', 'rate_per_piece': 3500,
            'smv': 10.0})
        wizard = self.env['garment.worker.output.paste.wizard'].create({
            'date': '2026-07-05',
            'style_id': style.id,
            'piece_rate_id': rate.id,
            'paste_text': "KHONGCO99\t50\n",
        })
        with self.assertRaises(UserError):
            wizard.action_import()
