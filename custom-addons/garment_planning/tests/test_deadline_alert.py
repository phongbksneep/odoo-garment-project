from odoo.tests import TransactionCase, tagged
from datetime import date, timedelta


@tagged('post_install', '-at_install')
class TestDeadlineAlert(TransactionCase):
    """Tests for production plan deadline auto-alert cron."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Alert',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-ALR-001',
            'code': 'ST-ALR-001',
            'category': 'shirt',
        })
        cls.PlanModel = cls.env['garment.production.plan']

    def _create_plan(self, ship_date=None, state='confirmed', **kwargs):
        today = date.today()
        vals = {
            'style_id': self.style.id,
            'buyer_id': self.partner.id,
            'total_quantity': 5000,
            'smv': 10.0,
            'date_start': today - timedelta(days=10),
            'date_end': today + timedelta(days=20),
            'ship_date': ship_date,
        }
        vals.update(kwargs)
        plan = self.PlanModel.create(vals)
        if state != 'draft':
            # Create a line loading so we can confirm
            workers = self.env['hr.employee'].create(
                [{'name': f'AlertW-{i}'} for i in range(20)]
            )
            line = self.env['garment.sewing.line'].create({
                'name': f'Alert Line {plan.id}',
                'code': f'AL{plan.id:02d}',
                'worker_ids': [(6, 0, workers.ids)],
            })
            self.env['garment.line.loading'].create({
                'plan_id': plan.id,
                'sewing_line_id': line.id,
                'planned_qty': 5000,
                'date_start': today - timedelta(days=10),
                'date_end': today + timedelta(days=20),
            })
            plan.action_confirm()
            if state == 'in_progress':
                plan.action_start()
        return plan

    def _get_activities(self, plan):
        model_id = self.env['ir.model']._get_id('garment.production.plan')
        return self.env['mail.activity'].search([
            ('res_model_id', '=', model_id),
            ('res_id', '=', plan.id),
        ])

    # --- Tests ---
    def test_overdue_plan_creates_activity(self):
        """Overdue plan (ship_date in the past) should create alert activity."""
        plan = self._create_plan(
            ship_date=date.today() - timedelta(days=2),
            state='in_progress',
        )
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertTrue(activities, 'Should create activity for overdue plan')
        self.assertIn('QUÁ HẠN', activities[0].summary)

    def test_approaching_plan_creates_activity(self):
        """Plan with ship_date within 3 days should create alert activity."""
        plan = self._create_plan(
            ship_date=date.today() + timedelta(days=2),
            state='confirmed',
        )
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertTrue(activities, 'Should create activity for approaching deadline')
        self.assertIn('ngày đến hạn', activities[0].summary)

    def test_future_plan_no_activity(self):
        """Plan with ship_date > 3 days away should NOT create activity."""
        plan = self._create_plan(
            ship_date=date.today() + timedelta(days=10),
            state='confirmed',
        )
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertFalse(activities, 'Should not alert for far-future deadline')

    def test_done_plan_no_activity(self):
        """Completed plans should NOT receive deadline alerts."""
        plan = self._create_plan(
            ship_date=date.today() - timedelta(days=1),
            state='in_progress',
        )
        plan.action_done()
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertFalse(activities, 'Should not alert done plans')

    def test_no_duplicate_activity(self):
        """Running cron twice on same day should not create duplicate activities."""
        plan = self._create_plan(
            ship_date=date.today() + timedelta(days=1),
            state='confirmed',
        )
        self.PlanModel._cron_check_deadline_alerts()
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertEqual(len(activities), 1, 'Should not create duplicate activities')

    def test_no_ship_date_no_activity(self):
        """Plans without ship_date should not trigger alerts."""
        plan = self._create_plan(
            ship_date=False,
            state='confirmed',
        )
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertFalse(activities, 'Should not alert plans without ship_date')

    def test_cancelled_plan_no_activity(self):
        """Cancelled plans should NOT receive deadline alerts."""
        plan = self._create_plan(
            ship_date=date.today(),
            state='confirmed',
        )
        plan.action_cancel()
        self.PlanModel._cron_check_deadline_alerts()
        activities = self._get_activities(plan)
        self.assertFalse(activities, 'Should not alert cancelled plans')
