from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCostAnalysis(TransactionCase):
    """Tests for garment.cost.analysis SQL view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Cost',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-CST-001',
            'code': 'ST-CST-001',
            'category': 'shirt',
            'sam': 10.0,
        })
        # Create approved cost sheet for the style
        cls.cost_sheet = cls.env['garment.cost.sheet'].create({
            'style_id': cls.style.id,
            'buyer_id': cls.partner.id,
            'order_qty': 5000,
            'costing_type': 'fob',
            'smv': 10.0,
            'target_efficiency': 60.0,
            'cm_rate_per_minute': 0.05,
        })
        # Add a fabric cost line
        cls.env['garment.cost.line'].create({
            'cost_sheet_id': cls.cost_sheet.id,
            'cost_type': 'fabric',
            'description': 'Cotton Jersey',
            'consumption': 0.5,
            'unit_price': 3.0,
        })
        cls.cost_sheet.action_confirm()
        cls.cost_sheet.action_approve()

        # Create sewing line with workers
        workers = cls.env['hr.employee'].create(
            [{'name': f'CostW-{i}'} for i in range(30)]
        )
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Cost Line A',
            'code': 'CLA1',
            'worker_ids': [(6, 0, workers.ids)],
        })

        # Create garment order (required for production order)
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })

        # Create production order
        cls.prod_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.garment_order.id,
            'style_id': cls.style.id,
            'customer_id': cls.partner.id,
            'sewing_line_id': cls.sewing_line.id,
            'planned_qty': 5000,
            'start_date': '2026-01-01',
            'end_date': '2026-01-31',
        })

    def test_sql_view_accessible(self):
        """Cost analysis SQL view should be queryable."""
        records = self.env['garment.cost.analysis'].search([])
        self.assertTrue(len(records) >= 1)

    def test_cost_sheet_linked(self):
        """Production order should link to approved cost sheet via style."""
        analysis = self.env['garment.cost.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertEqual(len(analysis), 1)
        self.assertEqual(analysis.cost_sheet_id, self.cost_sheet)
        self.assertEqual(analysis.style_id, self.style)
        self.assertEqual(analysis.customer_id, self.partner)

    def test_planned_values(self):
        """Planned values should come from cost sheet."""
        analysis = self.env['garment.cost.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertEqual(analysis.planned_qty, 5000)
        self.assertGreater(analysis.cost_per_pc, 0)
        self.assertGreater(analysis.planned_total_cost, 0)

    def test_zero_completion_variance(self):
        """With 0 completed qty, variance should be 100%."""
        analysis = self.env['garment.cost.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertEqual(analysis.completed_qty, 0)
        self.assertAlmostEqual(analysis.variance_pct, 100.0, places=1)

    def test_with_daily_output(self):
        """After adding daily output, actual values should update."""
        self.prod_order.action_confirm()
        self.prod_order.action_start()

        # Add daily output
        self.env['garment.daily.output'].create({
            'production_order_id': self.prod_order.id,
            'date': '2026-01-15',
            'target_qty': 500,
            'output_qty': 450,
            'worker_count': 30,
        })

        # Force recompute of stored fields and flush to DB
        self.prod_order.invalidate_recordset()
        self.env.flush_all()

        # Re-init the SQL view to reflect updated data
        self.env['garment.cost.analysis'].init()

        # Refresh SQL view
        analysis = self.env['garment.cost.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertEqual(analysis.completed_qty, 450)
        self.assertGreater(analysis.actual_total_cost, 0)
        self.assertLess(analysis.variance_pct, 100)

    def test_search_filters(self):
        """Search domain filters should work on SQL view."""
        # Filter by style
        results = self.env['garment.cost.analysis'].search([
            ('style_id', '=', self.style.id),
        ])
        self.assertTrue(len(results) >= 1)

        # Filter by customer
        results = self.env['garment.cost.analysis'].search([
            ('customer_id', '=', self.partner.id),
        ])
        self.assertTrue(len(results) >= 1)
