from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEfficiencyAnalysis(TransactionCase):
    """Tests for garment.efficiency.analysis SQL view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Eff',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-EFF-001',
            'code': 'ST-EFF-001',
            'category': 'shirt',
            'sam': 8.0,
        })
        workers = cls.env['hr.employee'].create(
            [{'name': f'EffW-{i}'} for i in range(20)]
        )
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Eff Test Line',
            'code': 'EFL1',
            'worker_ids': [(6, 0, workers.ids)],
        })
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })
        cls.prod_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.garment_order.id,
            'style_id': cls.style.id,
            'customer_id': cls.partner.id,
            'sewing_line_id': cls.sewing_line.id,
            'planned_qty': 2000,
            'start_date': '2026-01-01',
            'end_date': '2026-01-31',
        })
        cls.daily_output = cls.env['garment.daily.output'].create({
            'production_order_id': cls.prod_order.id,
            'sewing_line_id': cls.sewing_line.id,
            'date': '2026-01-15',
            'output_qty': 500,
        })

    def _refresh_view(self):
        self.env.flush_all()
        self.env['garment.efficiency.analysis'].init()

    def test_sql_view_accessible(self):
        """Efficiency analysis SQL view should be queryable."""
        self._refresh_view()
        records = self.env['garment.efficiency.analysis'].search([])
        self.assertTrue(len(records) >= 1)

    def test_fields_populated(self):
        """Check key fields are populated correctly."""
        self._refresh_view()
        analysis = self.env['garment.efficiency.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertEqual(len(analysis), 1)
        self.assertEqual(analysis.sewing_line_id, self.sewing_line)
        self.assertEqual(analysis.style_id, self.style)
        self.assertEqual(analysis.total_output, 500)
        self.assertEqual(analysis.worker_count, 20)

    def test_efficiency_calculated(self):
        """Efficiency = (output * SAM) / (workers * 480) * 100."""
        self._refresh_view()
        analysis = self.env['garment.efficiency.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        # 500 * 8.0 / (20 * 480) * 100 = 4000 / 9600 * 100 = 41.67%
        expected = 500 * 8.0 / (20 * 480.0) * 100
        self.assertAlmostEqual(analysis.efficiency, expected, places=1)

    def test_earned_minutes(self):
        """Earned minutes = output * SAM."""
        self._refresh_view()
        analysis = self.env['garment.efficiency.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertAlmostEqual(analysis.earned_minutes, 500 * 8.0, places=0)
        self.assertAlmostEqual(analysis.working_minutes, 20 * 480, places=0)
