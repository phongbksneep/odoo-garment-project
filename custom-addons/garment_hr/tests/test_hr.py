from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


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
