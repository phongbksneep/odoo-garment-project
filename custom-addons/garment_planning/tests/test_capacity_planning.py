from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import math


@tagged('post_install', '-at_install')
class TestCapacityPlanning(TransactionCase):
    """Unit tests and E2E tests for Capacity Planning nâng cao."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Capacity',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-CAP-001',
            'code': 'ST-CAP-001',
            'category': 'shirt',
            'sam': 10.0,
        })
        # Create workers for sewing lines
        workers_a = cls.env['hr.employee'].create(
            [{'name': 'Cap Worker A-%d' % i} for i in range(30)]
        )
        workers_b = cls.env['hr.employee'].create(
            [{'name': 'Cap Worker B-%d' % i} for i in range(40)]
        )
        cls.line_a = cls.env['garment.sewing.line'].create({
            'name': 'Cap Line A',
            'code': 'CLA01',
            'worker_ids': [(6, 0, workers_a.ids)],
        })
        cls.line_b = cls.env['garment.sewing.line'].create({
            'name': 'Cap Line B',
            'code': 'CLB01',
            'worker_ids': [(6, 0, workers_b.ids)],
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
            'delivery_date': date.today() + timedelta(days=30),
        })

    def _create_planning(self, **kwargs):
        vals = {
            'style_id': self.style.id,
            'sam': 10.0,
            'total_quantity': 10000,
            'working_minutes_per_day': 480,
            'break_minutes': 60,
            'overtime_minutes': 0,
            'ship_date': date.today() + timedelta(days=30),
        }
        vals.update(kwargs)
        return self.env['garment.capacity.planning'].create(vals)

    # =========================================================================
    # Unit Tests
    # =========================================================================
    def test_01_sequence_generation(self):
        """Capacity planning gets a CAP/YYYY/XXXXX sequence."""
        planning = self._create_planning()
        self.assertTrue(planning.name.startswith('CAP/'))

    def test_02_sam_from_style(self):
        """SAM is loaded from style via onchange."""
        planning = self._create_planning(sam=0.1)
        planning.style_id = self.style
        planning._onchange_style_id()
        self.assertEqual(planning.sam, 10.0)

    def test_03_available_minutes(self):
        """Available = working - break + overtime."""
        planning = self._create_planning(
            working_minutes_per_day=480,
            break_minutes=60,
            overtime_minutes=120,
        )
        self.assertEqual(planning.available_minutes, 540)

    def test_04_available_minutes_default(self):
        """Default: 480 - 60 + 0 = 420."""
        planning = self._create_planning()
        self.assertEqual(planning.available_minutes, 420)

    def test_05_daily_capacity_calculation(self):
        """Daily output = (workers × available_minutes × efficiency%) / SAM."""
        planning = self._create_planning(sam=10.0)
        cap_line = self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        # 30 workers × 420 min × 70% / 10 SAM = 882
        expected = int(30 * 420 * 0.70 / 10)
        self.assertEqual(cap_line.daily_output, expected)

    def test_06_hourly_output(self):
        """Hourly output = (workers × 60 × efficiency%) / SAM."""
        planning = self._create_planning(sam=10.0)
        cap_line = self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        expected = round(30 * 60 * 0.70 / 10, 1)
        self.assertEqual(cap_line.hourly_output, expected)

    def test_07_pieces_per_worker(self):
        """Pieces per worker = daily_output / workers."""
        planning = self._create_planning(sam=10.0)
        cap_line = self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        daily = int(30 * 420 * 0.70 / 10)
        expected = round(daily / 30, 1)
        self.assertEqual(cap_line.pieces_per_worker, expected)

    def test_08_required_days(self):
        """Required days = ceil(total_qty / daily_output)."""
        planning = self._create_planning(sam=10.0, total_quantity=5000)
        cap_line = self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        daily = int(30 * 420 * 0.70 / 10)
        expected = math.ceil(5000 / daily)
        self.assertEqual(cap_line.required_days, expected)

    def test_09_summary_total_daily(self):
        """Total daily output sums all lines."""
        planning = self._create_planning(sam=10.0)
        self.env['garment.capacity.line'].create([
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_a.id,
                'target_efficiency': 70.0,
            },
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_b.id,
                'target_efficiency': 65.0,
            },
        ])
        planning.invalidate_recordset()
        daily_a = int(30 * 420 * 0.70 / 10)
        daily_b = int(40 * 420 * 0.65 / 10)
        self.assertEqual(planning.total_daily_output, daily_a + daily_b)

    def test_10_total_workers(self):
        """Total workers sums all lines."""
        planning = self._create_planning()
        self.env['garment.capacity.line'].create([
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_a.id,
            },
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_b.id,
            },
        ])
        planning.invalidate_recordset()
        self.assertEqual(planning.total_workers, 70)

    def test_11_overtime_increases_capacity(self):
        """Adding overtime increases daily output."""
        planning_no_ot = self._create_planning(
            sam=10.0, overtime_minutes=0,
        )
        planning_with_ot = self._create_planning(
            sam=10.0, overtime_minutes=120,
        )
        cap_no_ot = self.env['garment.capacity.line'].create({
            'planning_id': planning_no_ot.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        cap_with_ot = self.env['garment.capacity.line'].create({
            'planning_id': planning_with_ot.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        self.assertGreater(cap_with_ot.daily_output, cap_no_ot.daily_output)

    def test_12_bottleneck_detection(self):
        """Bottleneck line is the one with lowest pieces_per_worker."""
        planning = self._create_planning(sam=10.0)
        self.env['garment.capacity.line'].create([
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_a.id,
                'target_efficiency': 50.0,  # Lower efficiency = bottleneck
            },
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_b.id,
                'target_efficiency': 80.0,
            },
        ])
        planning.invalidate_recordset()
        # Line A has lower efficiency → lower pieces/worker → bottleneck
        self.assertEqual(
            planning.bottleneck_line_id.sewing_line_id, self.line_a
        )

    def test_13_can_meet_deadline_true(self):
        """Can meet deadline when required_days <= available_days."""
        planning = self._create_planning(
            total_quantity=1000,
            sam=10.0,
            ship_date=date.today() + timedelta(days=30),
        )
        self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 70.0,
        })
        planning.invalidate_recordset()
        # 30 workers × 420 × 70% / 10 = 882/day → 1000/882 ≈ 2 days
        self.assertTrue(planning.can_meet_deadline)

    def test_14_can_meet_deadline_false(self):
        """Cannot meet deadline when required_days > available_days."""
        planning = self._create_planning(
            total_quantity=100000,
            sam=10.0,
            ship_date=date.today() + timedelta(days=3),
        )
        self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 50.0,
        })
        planning.invalidate_recordset()
        self.assertFalse(planning.can_meet_deadline)

    def test_15_sam_validation(self):
        """SAM must be > 0."""
        with self.assertRaises(ValidationError):
            self._create_planning(sam=0)

    def test_16_quantity_validation(self):
        """Quantity must be > 0."""
        with self.assertRaises(ValidationError):
            self._create_planning(total_quantity=0)

    def test_17_simulate_requires_lines(self):
        """Simulate raises error without lines."""
        planning = self._create_planning()
        with self.assertRaises(UserError):
            planning.action_simulate()

    def test_18_approve_requires_simulated(self):
        """Cannot approve without simulation."""
        planning = self._create_planning()
        self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': self.line_a.id,
        })
        with self.assertRaises(UserError):
            planning.action_approve()

    def test_19_line_share_percentage(self):
        """Line share % adds up to ~100% across all lines."""
        planning = self._create_planning(sam=10.0)
        self.env['garment.capacity.line'].create([
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_a.id,
                'target_efficiency': 70.0,
            },
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_b.id,
                'target_efficiency': 70.0,
            },
        ])
        planning.invalidate_recordset()
        total_share = sum(planning.line_ids.mapped('line_share_pct'))
        self.assertAlmostEqual(total_share, 100.0, delta=1.0)

    def test_20_zero_workers_zero_output(self):
        """Line with 0 workers has 0 output."""
        planning = self._create_planning(sam=10.0)
        # Create a line with no workers
        empty_line = self.env['garment.sewing.line'].create({
            'name': 'Empty Line',
            'code': 'EMP01',
        })
        cap_line = self.env['garment.capacity.line'].create({
            'planning_id': planning.id,
            'sewing_line_id': empty_line.id,
            'target_efficiency': 70.0,
        })
        self.assertEqual(cap_line.daily_output, 0)
        self.assertEqual(cap_line.hourly_output, 0)

    # =========================================================================
    # E2E Test
    # =========================================================================
    def test_e2e_full_capacity_planning_workflow(self):
        """E2E: Create → add lines → simulate → approve → create plan."""
        # Step 1: Create capacity planning from order
        planning = self.env['garment.capacity.planning'].create({
            'garment_order_id': self.order.id,
            'style_id': self.style.id,
            'sam': 10.0,
            'total_quantity': 10000,
            'working_minutes_per_day': 480,
            'break_minutes': 60,
            'overtime_minutes': 0,
            'ship_date': date.today() + timedelta(days=30),
        })
        self.assertEqual(planning.state, 'draft')
        self.assertTrue(planning.name.startswith('CAP/'))

        # Step 2: Add sewing lines
        self.env['garment.capacity.line'].create([
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_a.id,
                'target_efficiency': 70.0,
            },
            {
                'planning_id': planning.id,
                'sewing_line_id': self.line_b.id,
                'target_efficiency': 65.0,
            },
        ])

        # Step 3: Verify capacity calculations
        planning.invalidate_recordset()
        daily_a = int(30 * 420 * 0.70 / 10)  # 882
        daily_b = int(40 * 420 * 0.65 / 10)  # 1092
        self.assertEqual(planning.total_daily_output, daily_a + daily_b)
        self.assertEqual(planning.total_workers, 70)
        self.assertGreater(planning.required_days, 0)
        self.assertGreater(planning.pieces_per_worker_day, 0)

        # Step 4: Simulate
        planning.action_simulate()
        self.assertEqual(planning.state, 'simulated')

        # Step 5: Approve
        planning.action_approve()
        self.assertEqual(planning.state, 'approved')

        # Step 6: Create production plan
        result = planning.action_create_production_plan()
        self.assertEqual(result['res_model'], 'garment.production.plan')

        plan = self.env['garment.production.plan'].browse(result['res_id'])
        self.assertEqual(plan.style_id, self.style)
        self.assertEqual(plan.total_quantity, 10000)
        self.assertEqual(plan.smv, 10.0)
        self.assertEqual(len(plan.loading_ids), 2)
        # Total planned should equal total quantity
        total_planned = sum(plan.loading_ids.mapped('planned_qty'))
        self.assertEqual(total_planned, 10000)

    def test_e2e_overtime_scenario(self):
        """E2E: Compare capacity with and without overtime."""
        # Without overtime
        plan_normal = self._create_planning(
            sam=15.0, total_quantity=20000,
            overtime_minutes=0,
        )
        self.env['garment.capacity.line'].create({
            'planning_id': plan_normal.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 65.0,
        })
        plan_normal.invalidate_recordset()
        days_normal = plan_normal.required_days

        # With 2 hours overtime
        plan_ot = self._create_planning(
            sam=15.0, total_quantity=20000,
            overtime_minutes=120,
        )
        self.env['garment.capacity.line'].create({
            'planning_id': plan_ot.id,
            'sewing_line_id': self.line_a.id,
            'target_efficiency': 65.0,
        })
        plan_ot.invalidate_recordset()
        days_ot = plan_ot.required_days

        # Overtime should reduce required days
        self.assertGreater(days_normal, days_ot)
