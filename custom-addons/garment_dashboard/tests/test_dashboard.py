from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestGarmentDashboard(TransactionCase):
    """Test dashboard SQL views."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create basic test data
        cls.partner = cls.env['res.partner'].create({
            'name': 'Dashboard Test Customer',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Dashboard Test Style',
            'code': 'DASH-001',
            'category': 'shirt',
        })
        cls.color = cls.env['garment.color'].create({'name': 'Dash Red', 'code': 'DRED'})
        cls.size = cls.env['garment.size'].create({'name': 'Dash M', 'code': 'DM', 'size_type': 'letter'})
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
            'delivery_date': fields.Date.today() + timedelta(days=30),
            'unit_price': 10.0,
        })
        cls.env['garment.order.line'].create({
            'order_id': cls.order.id,
            'color_id': cls.color.id,
            'size_id': cls.size.id,
            'quantity': 100,
        })
        cls.order.action_confirm()

    def test_01_dashboard_kpi_exists(self):
        """Test dashboard KPI SQL view has data."""
        kpis = self.env['garment.dashboard'].search([])
        self.assertTrue(len(kpis) > 0, "Dashboard KPI should have records")

    def test_02_dashboard_kpi_order_total(self):
        """Test order total KPI."""
        kpi = self.env['garment.dashboard'].search([
            ('kpi_type', '=', 'order_total')
        ])
        self.assertEqual(len(kpi), 1)
        self.assertTrue(kpi.value >= 1, "Should have at least 1 order")

    def test_03_dashboard_kpi_types(self):
        """Test all expected KPI types exist."""
        expected_types = [
            'order_total', 'order_active', 'order_done', 'order_late',
            'prod_total', 'prod_active', 'prod_done',
            'qty_planned', 'qty_completed', 'qty_defect',
            'qc_total', 'qc_pass', 'qc_fail',
            'delivery_total', 'delivery_done',
            'material_total', 'material_done',
        ]
        kpis = self.env['garment.dashboard'].search([])
        kpi_types = kpis.mapped('kpi_type')
        for kpi_type in expected_types:
            self.assertIn(kpi_type, kpi_types,
                          f"KPI type '{kpi_type}' should exist")

    def test_04_order_overview_exists(self):
        """Test order overview SQL view."""
        overviews = self.env['garment.order.overview'].search([])
        self.assertTrue(len(overviews) >= 1, "Should have at least 1 order in overview")

    def test_05_order_overview_data(self):
        """Test order overview has correct data."""
        overview = self.env['garment.order.overview'].search([
            ('name', '=', self.order.name)
        ])
        self.assertEqual(len(overview), 1)
        self.assertEqual(overview.customer_id.id, self.partner.id)
        self.assertEqual(overview.style_id.id, self.style.id)
        self.assertEqual(overview.state, 'confirmed')

    def test_06_order_overview_late_detection(self):
        """Test late order detection in overview."""
        late_order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'order_date': fields.Date.today() - timedelta(days=30),
            'delivery_date': fields.Date.today() - timedelta(days=5),
            'unit_price': 5.0,
        })
        self.env['garment.order.line'].create({
            'order_id': late_order.id,
            'color_id': self.color.id,
            'size_id': self.size.id,
            'quantity': 100,
        })
        late_order.action_confirm()
        late_order.action_material()

        overview = self.env['garment.order.overview'].search([
            ('name', '=', late_order.name)
        ])
        self.assertTrue(overview.is_late, "Order with past deadline should be late")
        self.assertTrue(overview.days_remaining < 0, "Days remaining should be negative")

    def test_07_production_progress_view(self):
        """Test production progress SQL view."""
        # Create a production order
        prod = self.env['garment.production.order'].create({
            'garment_order_id': self.order.id,
            'planned_qty': 500,
        })
        prod.action_confirm()
        prod.action_start()
        self.env.flush_all()
        self.env.invalidate_all()

        progress = self.env['garment.production.progress'].search([
            ('name', '=', prod.name)
        ])
        self.assertEqual(len(progress), 1)
        self.assertEqual(progress.planned_qty, 500)
        self.assertEqual(progress.state, 'in_progress')
        self.assertEqual(progress.remaining_qty, 500)

    def test_08_production_progress_with_output(self):
        """Test production progress after daily output."""
        prod = self.env['garment.production.order'].create({
            'garment_order_id': self.order.id,
            'planned_qty': 1000,
        })
        prod.action_confirm()
        prod.action_start()

        # Add daily output
        self.env['garment.daily.output'].create({
            'production_order_id': prod.id,
            'date': '2025-01-15',
            'output_qty': 200,
            'defect_qty': 5,
            'worker_count': 30,
            'working_hours': 8,
        })
        self.env.flush_all()
        self.env.invalidate_all()

        progress = self.env['garment.production.progress'].search([
            ('name', '=', prod.name)
        ])
        self.assertEqual(progress.completed_qty, 200)
        self.assertEqual(progress.defect_qty, 5)
        self.assertEqual(progress.remaining_qty, 800)
        self.assertTrue(progress.working_days >= 1)

    def test_09_order_overview_production_count(self):
        """Test production count in order overview."""
        # Create 2 production orders for same garment order
        for i in range(2):
            prod = self.env['garment.production.order'].create({
                'garment_order_id': self.order.id,
                'planned_qty': 250,
            })
            prod.action_confirm()
        self.env.flush_all()
        self.env.invalidate_all()

        overview = self.env['garment.order.overview'].search([
            ('name', '=', self.order.name)
        ])
        self.assertTrue(overview.production_count >= 2)

    def test_10_dashboard_search_read(self):
        """Test dashboard can be read via search_read (for UI)."""
        result = self.env['garment.dashboard'].search_read(
            [], ['name', 'kpi_type', 'value']
        )
        self.assertTrue(len(result) > 0)
        # Check structure
        for r in result:
            self.assertIn('name', r)
            self.assertIn('kpi_type', r)
            self.assertIn('value', r)
