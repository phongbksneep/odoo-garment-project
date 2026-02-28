from datetime import timedelta

from odoo.tests.common import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestMobileDashboard(TransactionCase):
    """Test mobile dashboard data provider."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Mobile Dashboard Test Customer',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Mobile Dashboard Style',
            'code': 'MOB-001',
            'category': 'shirt',
        })
        cls.color = cls.env['garment.color'].create({'name': 'Mob Red', 'code': 'MRED'})
        cls.size = cls.env['garment.size'].create({'name': 'Mob M', 'code': 'MM', 'size_type': 'letter'})
        # Create a confirmed order
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
            'delivery_date': fields.Date.today() + timedelta(days=2),
            'unit_price': 12.0,
        })
        cls.env['garment.order.line'].create({
            'order_id': cls.order.id,
            'color_id': cls.color.id,
            'size_id': cls.size.id,
            'quantity': 100,
        })
        cls.order.action_confirm()

    def _get_data(self):
        """Shortcut to get dashboard data."""
        return self.env['garment.mobile.dashboard'].get_dashboard_data()

    # ----- structure tests -----

    def test_01_dashboard_data_structure(self):
        """Dashboard data should contain expected keys."""
        data = self._get_data()
        self.assertIn('order', data)
        self.assertIn('production', data)
        self.assertIn('quality', data)
        self.assertIn('delivery', data)
        self.assertIn('upcoming', data)
        self.assertIn('late', data)
        self.assertIn('pending_approvals', data)

    def test_02_order_data_keys(self):
        """Order section should have all expected keys."""
        data = self._get_data()
        order = data['order']
        for key in ('total', 'active', 'done', 'late'):
            self.assertIn(key, order)

    def test_03_production_data_keys(self):
        """Production section should have all expected keys."""
        data = self._get_data()
        prod = data['production']
        for key in ('active', 'done', 'planned_qty', 'completed_qty', 'completion_pct'):
            self.assertIn(key, prod)

    def test_04_quality_data_keys(self):
        """Quality section should have all expected keys."""
        data = self._get_data()
        quality = data['quality']
        for key in ('total', 'pass_count', 'pass_rate'):
            self.assertIn(key, quality)

    def test_05_delivery_data_keys(self):
        """Delivery section should have all expected keys."""
        data = self._get_data()
        delivery = data['delivery']
        for key in ('pending', 'done'):
            self.assertIn(key, delivery)

    # ----- value tests -----

    def test_06_order_total_positive(self):
        """There should be at least 1 order in the system."""
        data = self._get_data()
        self.assertGreaterEqual(data['order']['total'], 1)

    def test_07_upcoming_is_list(self):
        """Upcoming should be a list."""
        data = self._get_data()
        self.assertIsInstance(data['upcoming'], list)

    def test_08_late_is_list(self):
        """Late should be a list."""
        data = self._get_data()
        self.assertIsInstance(data['late'], list)

    def test_09_pending_approvals_integer(self):
        """Pending approvals should be an integer >= 0."""
        data = self._get_data()
        self.assertIsInstance(data['pending_approvals'], int)
        self.assertGreaterEqual(data['pending_approvals'], 0)

    def test_10_completion_pct_range(self):
        """Completion percentage should be between 0 and 100."""
        data = self._get_data()
        pct = data['production']['completion_pct']
        self.assertGreaterEqual(pct, 0)
        self.assertLessEqual(pct, 100)

    # ----- upcoming order detection -----

    def test_11_upcoming_order_detected(self):
        """Order with delivery in 2 days should appear in upcoming."""
        data = self._get_data()
        upcoming_names = [u['name'] for u in data['upcoming']]
        # Our test order has delivery_date = today + 2 days
        self.assertIn(self.order.name, upcoming_names)

    def test_12_upcoming_item_structure(self):
        """Each upcoming item should have expected fields."""
        data = self._get_data()
        if data['upcoming']:
            item = data['upcoming'][0]
            for key in ('name', 'customer', 'date', 'days'):
                self.assertIn(key, item)

    # ----- late order detection -----

    def test_13_late_order_detected(self):
        """Order with past delivery date should appear in late list."""
        late_order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'order_date': fields.Date.today() - timedelta(days=30),
            'delivery_date': fields.Date.today() - timedelta(days=5),
            'unit_price': 8.0,
        })
        self.env['garment.order.line'].create({
            'order_id': late_order.id,
            'color_id': self.color.id,
            'size_id': self.size.id,
            'quantity': 100,
        })
        late_order.action_confirm()
        data = self._get_data()
        late_names = [l['name'] for l in data['late']]
        self.assertIn(late_order.name, late_names)

    def test_14_late_item_structure(self):
        """Each late item should have expected fields."""
        late_order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'order_date': fields.Date.today() - timedelta(days=30),
            'delivery_date': fields.Date.today() - timedelta(days=3),
            'unit_price': 8.0,
        })
        self.env['garment.order.line'].create({
            'order_id': late_order.id,
            'color_id': self.color.id,
            'size_id': self.size.id,
            'quantity': 100,
        })
        late_order.action_confirm()
        data = self._get_data()
        if data['late']:
            item = data['late'][0]
            for key in ('name', 'customer', 'date', 'days_late'):
                self.assertIn(key, item)

    # ----- pending approvals count -----

    def test_15_pending_approvals_count(self):
        """Pending approval count should increase when an order is sent for approval."""
        data_before = self._get_data()
        before_count = data_before['pending_approvals']

        new_order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'delivery_date': fields.Date.today() + timedelta(days=10),
            'unit_price': 25.0,
        })
        new_order.action_request_approval()

        data_after = self._get_data()
        self.assertEqual(data_after['pending_approvals'], before_count + 1)
