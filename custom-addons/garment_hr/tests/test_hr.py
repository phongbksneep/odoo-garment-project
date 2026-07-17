from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestGarmentAttendance(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'NV Test HR'})

    def test_attendance_create(self):
        att = self.env['garment.attendance'].create({
            'employee_id': self.employee.id,
            'status': 'present',
            'check_in': 7.5,
            'check_out': 17.0,
        })
        self.assertEqual(att.status, 'present')
        # 17-7.5=9.5 - 1h lunch = 8.5
        self.assertAlmostEqual(att.work_hours, 8.5)

    def test_absent_zero_hours(self):
        att = self.env['garment.attendance'].create({
            'employee_id': self.employee.id,
            'status': 'absent',
        })
        self.assertEqual(att.work_hours, 0)

    def test_half_day(self):
        att = self.env['garment.attendance'].create({
            'employee_id': self.employee.id,
            'status': 'half_day',
        })
        self.assertEqual(att.work_hours, 4)

    def test_unique_constraint(self):
        from odoo.tools import mute_logger
        self.env['garment.attendance'].create({
            'employee_id': self.employee.id,
            'status': 'present',
        })
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(Exception):
                self.env['garment.attendance'].create({
                    'employee_id': self.employee.id,
                    'status': 'late',
                })


@tagged('post_install', '-at_install')
class TestAttendanceSummary(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'NV Summary'})

    def test_calculate_summary(self):
        from odoo import fields as f
        today = f.Date.today()
        month = str(today.month).zfill(2)
        year = today.year
        # Create several attendances
        for day_offset in range(5):
            d = today.replace(day=min(today.day, 28))
            try:
                d = today.replace(day=1 + day_offset)
            except ValueError:
                continue
            self.env['garment.attendance'].create({
                'employee_id': self.employee.id,
                'date': d,
                'status': 'present' if day_offset < 4 else 'absent',
                'overtime_hours': 1.5 if day_offset < 2 else 0,
            })
        summary = self.env['garment.attendance.summary'].create({
            'employee_id': self.employee.id,
            'month': month,
            'year': year,
        })
        summary.action_calculate()
        self.assertEqual(summary.state, 'confirmed')
        self.assertGreater(summary.present_days, 0)


@tagged('post_install', '-at_install')
class TestGarmentLeave(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'NV Leave'})

    def test_leave_workflow(self):
        from odoo import fields as f
        today = f.Date.today()
        leave = self.env['garment.leave'].create({
            'employee_id': self.employee.id,
            'leave_type': 'annual',
            'date_from': today,
            'date_to': today,
        })
        self.assertEqual(leave.days, 1)
        leave.action_submit()
        self.assertEqual(leave.state, 'submitted')
        leave.action_approve()
        self.assertEqual(leave.state, 'approved')

    def test_leave_date_validation(self):
        from odoo import fields as f
        today = f.Date.today()
        from datetime import timedelta
        with self.assertRaises(ValidationError):
            self.env['garment.leave'].create({
                'employee_id': self.employee.id,
                'leave_type': 'sick',
                'date_from': today,
                'date_to': today - timedelta(days=3),
            })


@tagged('post_install', '-at_install')
class TestEmployeeSkill(TransactionCase):

    def test_create_skill(self):
        emp = self.env['hr.employee'].create({'name': 'NV Skill'})
        skill = self.env['garment.employee.skill'].create({
            'employee_id': emp.id,
            'skill_type': 'sewing',
            'level': 'advanced',
            'detail': 'May cổ áo sơ mi',
        })
        self.assertEqual(skill.level, 'advanced')


@tagged('post_install', '-at_install')
class TestGarmentEmployee(TransactionCase):
    """Tests for garment-specific employee fields."""

    def test_create_employee_with_garment_fields(self):
        emp = self.env['hr.employee'].create({
            'name': 'Nguyễn Văn A',
            'employee_code': 'NV001',
            'garment_role': 'worker',
            'contract_type': 'definite',
        })
        self.assertEqual(emp.employee_code, 'NV001')
        self.assertEqual(emp.garment_role, 'worker')
        self.assertEqual(emp.contract_type, 'definite')

    def test_team_leader_role(self):
        emp = self.env['hr.employee'].create({
            'name': 'Trần Thị B',
            'employee_code': 'NV002',
            'garment_role': 'team_leader',
        })
        self.assertEqual(emp.garment_role, 'team_leader')

    def test_dept_manager_role(self):
        emp = self.env['hr.employee'].create({
            'name': 'Lê Văn C',
            'employee_code': 'NV003',
            'garment_role': 'dept_manager',
        })
        self.assertEqual(emp.garment_role, 'dept_manager')

    def test_employee_skill_count(self):
        emp = self.env['hr.employee'].create({
            'name': 'NV Skills',
            'employee_code': 'NV004',
        })
        self.env['garment.employee.skill'].create({
            'employee_id': emp.id,
            'skill_type': 'sewing',
            'level': 'advanced',
        })
        self.env['garment.employee.skill'].create({
            'employee_id': emp.id,
            'skill_type': 'cutting',
            'level': 'basic',
        })
        self.assertEqual(emp.skill_count, 2)

    def test_employee_id_fields(self):
        emp = self.env['hr.employee'].create({
            'name': 'NV ID',
            'employee_code': 'NV005',
            'id_number': '012345678901',
            'insurance_number': 'BH123456',
            'tax_code': 'MST123456',
            'bank_name': 'Vietcombank',
            'bank_account': '0123456789',
        })
        self.assertEqual(emp.id_number, '012345678901')
        self.assertEqual(emp.bank_name, 'Vietcombank')

    def test_employee_emergency_contact(self):
        emp = self.env['hr.employee'].create({
            'name': 'NV Emergency',
            'emergency_contact': 'Nguyễn Mẹ',
            'emergency_phone': '0987654321',
        })
        self.assertEqual(emp.emergency_contact, 'Nguyễn Mẹ')


@tagged('post_install', '-at_install')
class TestSecurityGroups(TransactionCase):
    """Tests for role-based permission groups."""

    def test_groups_exist(self):
        user_group = self.env.ref('garment_base.group_garment_user')
        self.assertTrue(user_group)
        tl_group = self.env.ref('garment_base.group_garment_team_leader')
        self.assertTrue(tl_group)
        dm_group = self.env.ref('garment_base.group_garment_dept_manager')
        self.assertTrue(dm_group)
        admin_group = self.env.ref('garment_base.group_garment_manager')
        self.assertTrue(admin_group)

    def test_group_hierarchy(self):
        tl_group = self.env.ref('garment_base.group_garment_team_leader')
        user_group = self.env.ref('garment_base.group_garment_user')
        self.assertIn(user_group, tl_group.implied_ids)

        dm_group = self.env.ref('garment_base.group_garment_dept_manager')
        self.assertIn(tl_group, dm_group.implied_ids)

        admin_group = self.env.ref('garment_base.group_garment_manager')
        self.assertIn(dm_group, admin_group.implied_ids)

    def test_admin_has_all_roles(self):
        admin_group = self.env.ref('garment_base.group_garment_manager')
        user_group = self.env.ref('garment_base.group_garment_user')
        # Admin implies dept_manager which implies team_leader which implies user
        all_implied = admin_group.all_implied_ids
        self.assertIn(user_group, all_implied)


@tagged('post_install', '-at_install')
class TestLeaveGuards(TransactionCase):
    """Guard trạng thái đơn nghỉ phép."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Emp LeaveGrd'})

    def _create_leave(self):
        return self.env['garment.leave'].create({
            'employee_id': self.employee.id,
            'leave_type': 'annual',
            'date_from': '2026-08-03',
            'date_to': '2026-08-04',
        })

    def test_cannot_approve_draft(self):
        leave = self._create_leave()
        with self.assertRaises(ValidationError):
            leave.action_approve()

    def test_cannot_submit_twice(self):
        leave = self._create_leave()
        leave.action_submit()
        with self.assertRaises(ValidationError):
            leave.action_submit()

    def test_happy_path(self):
        leave = self._create_leave()
        leave.action_submit()
        leave.action_approve()
        self.assertEqual(leave.state, 'approved')


@tagged('post_install', '-at_install')
class TestAnnualLeaveBalance(TransactionCase):
    """Số dư phép năm: 12 ngày + thâm niên, chặn duyệt vượt số dư."""

    def _create_employee(self, join_date):
        return self.env['hr.employee'].create({
            'name': f'Emp Balance {join_date}',
            'join_date': join_date,
        })

    def _approved_leave(self, employee, date_from, date_to):
        leave = self.env['garment.leave'].create({
            'employee_id': employee.id,
            'leave_type': 'annual',
            'date_from': date_from,
            'date_to': date_to,
        })
        leave.action_submit()
        leave.action_approve()
        return leave

    def test_base_entitlement(self):
        emp = self._create_employee('2024-01-15')
        self.assertAlmostEqual(emp.annual_leave_entitlement, 12.0, places=1)

    def test_seniority_bonus(self):
        """+1 ngày cho mỗi 5 năm thâm niên (Điều 114 BLLĐ)."""
        emp = self._create_employee('2015-06-01')  # ~11 năm → +2
        self.assertAlmostEqual(emp.annual_leave_entitlement, 14.0, places=1)

    def test_mid_year_prorata(self):
        """Vào làm 01/07 năm nay → 6/12 tháng → 6 ngày."""
        emp = self._create_employee('2026-07-01')
        self.assertAlmostEqual(emp.annual_leave_entitlement, 6.0, places=1)

    def test_used_and_remaining(self):
        emp = self._create_employee('2024-01-15')
        self._approved_leave(emp, '2026-03-02', '2026-03-04')  # 3 ngày
        self.assertAlmostEqual(emp.annual_leave_used, 3.0, places=1)
        self.assertAlmostEqual(emp.annual_leave_remaining, 9.0, places=1)

    def test_cannot_approve_over_balance(self):
        emp = self._create_employee('2024-01-15')
        # Dùng 10 ngày
        self._approved_leave(emp, '2026-02-02', '2026-02-11')
        # Xin thêm 5 ngày — vượt số dư 2 ngày
        leave = self.env['garment.leave'].create({
            'employee_id': emp.id,
            'leave_type': 'annual',
            'date_from': '2026-09-07',
            'date_to': '2026-09-11',
        })
        leave.action_submit()
        with self.assertRaises(ValidationError):
            leave.action_approve()


@tagged('post_install', '-at_install')
class TestLeavePolicyOptions(TransactionCase):
    """Chính sách phép năm cấu hình được: số ngày cơ bản, thâm niên."""

    def test_reduced_base_days(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'garment_hr.annual_leave_base_days', '10')
        emp = self.env['hr.employee'].create({
            'name': 'Emp Policy 10d', 'join_date': '2024-01-15'})
        self.assertAlmostEqual(emp.annual_leave_entitlement, 10.0, places=1)

    def test_seniority_bonus_disabled(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('garment_hr.annual_leave_base_days', '12')
        icp.set_param('garment_hr.leave_seniority_bonus', 'False')
        emp = self.env['hr.employee'].create({
            'name': 'Emp Policy NoSen', 'join_date': '2015-06-01'})
        self.assertAlmostEqual(emp.annual_leave_entitlement, 12.0, places=1)
