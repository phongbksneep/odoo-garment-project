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
