from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta


@tagged('post_install', '-at_install')
class TestProductionPlan(TransactionCase):
    """Unit tests and E2E tests for garment.production.plan."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Planning',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-PLN-001',
            'code': 'ST-PLN-001',
            'category': 'shirt',
        })
        # Create workers for sewing lines
        workers_a = cls.env['hr.employee'].create(
            [{'name': f'Worker A-{i}'} for i in range(35)]
        )
        workers_b = cls.env['hr.employee'].create(
            [{'name': f'Worker B-{i}'} for i in range(40)]
        )
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Line A',
            'code': 'LA01',
            'worker_ids': [(6, 0, workers_a.ids)],
        })
        cls.sewing_line_2 = cls.env['garment.sewing.line'].create({
            'name': 'Line B',
            'code': 'LB01',
            'worker_ids': [(6, 0, workers_b.ids)],
        })

    def _create_plan(self, **kwargs):
        vals = {
            'style_id': self.style.id,
            'buyer_id': self.partner.id,
            'total_quantity': 10000,
            'smv': 12.0,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
        }
        vals.update(kwargs)
        return self.env['garment.production.plan'].create(vals)

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_plan_sequence(self):
        plan = self._create_plan()
        self.assertTrue(plan.name.startswith('PLAN/'))

    def test_dates_validation(self):
        """End date must be after start date."""
        with self.assertRaises(ValidationError):
            self._create_plan(
                date_start=date.today(),
                date_end=date.today() - timedelta(days=1),
            )

    def test_line_loading_daily_capacity(self):
        """Capacity = (workers × 480 × efficiency%) / SMV."""
        plan = self._create_plan()
        loading = self.env['garment.line.loading'].create({
            'plan_id': plan.id,
            'sewing_line_id': self.sewing_line.id,
            'target_efficiency': 65.0,
        })
        # 35 workers × 480 × 65% / 12 = 910
        self.assertEqual(loading.daily_capacity, 910)

    def test_planned_qty_and_remaining(self):
        plan = self._create_plan(total_quantity=5000)
        self.env['garment.line.loading'].create({
            'plan_id': plan.id,
            'sewing_line_id': self.sewing_line.id,
            'planned_qty': 3000,
        })
        plan.invalidate_recordset()
        self.assertEqual(plan.total_planned, 3000)
        self.assertEqual(plan.remaining_qty, 2000)

    def test_cannot_confirm_without_loading(self):
        plan = self._create_plan()
        with self.assertRaises(UserError):
            plan.action_confirm()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_planning_workflow(self):
        """E2E: Create → add lines → auto-schedule → confirm → start → done."""
        # Step 1: Create plan
        plan = self._create_plan(total_quantity=10000, smv=12.0)
        self.assertEqual(plan.state, 'draft')

        # Step 2: Assign lines
        self.env['garment.line.loading'].create([
            {
                'plan_id': plan.id,
                'sewing_line_id': self.sewing_line.id,
                'target_efficiency': 65.0,
            },
            {
                'plan_id': plan.id,
                'sewing_line_id': self.sewing_line_2.id,
                'target_efficiency': 70.0,
            },
        ])

        # Step 3: Auto-schedule
        plan.action_auto_schedule()
        plan.invalidate_recordset()
        self.assertGreater(plan.total_planned, 0)
        self.assertEqual(plan.total_planned, plan.total_quantity)

        # Step 4: Confirm
        plan.action_confirm()
        self.assertEqual(plan.state, 'confirmed')

        # Step 5: Start production
        plan.action_start()
        self.assertEqual(plan.state, 'in_progress')

        # Step 6: Complete
        plan.action_done()
        self.assertEqual(plan.state, 'done')
