from datetime import date, timedelta
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestGarmentOrder(TransactionCase):
    """Tests for garment.order validations and improvements."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer GO',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-GO-001',
            'code': 'ST-GO-001',
            'category': 'shirt',
        })
        cls.color = cls.env['garment.color'].create({
            'name': 'Red GO',
            'code': 'RED-GO',
        })
        cls.color2 = cls.env['garment.color'].create({
            'name': 'Blue GO',
            'code': 'BLU-GO',
        })
        cls.size = cls.env['garment.size'].create({
            'name': 'M-GO',
            'code': 'MGO',
            'size_type': 'letter',
        })
        cls.size2 = cls.env['garment.size'].create({
            'name': 'L-GO',
            'code': 'LGO',
            'size_type': 'letter',
        })

    def _create_order(self, **kwargs):
        vals = {
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'unit_price': 5.0,
            'order_date': date.today(),
        }
        vals.update(kwargs)
        return self.env['garment.order'].create(vals)

    def _add_line(self, order, color=None, size=None, qty=100):
        return self.env['garment.order.line'].create({
            'order_id': order.id,
            'color_id': (color or self.color).id,
            'size_id': (size or self.size).id,
            'quantity': qty,
        })

    # -------------------------------------------------------------------------
    # Confirm validation
    # -------------------------------------------------------------------------
    def test_confirm_requires_lines(self):
        """Cannot confirm order without any lines."""
        order = self._create_order()
        with self.assertRaises(ValidationError):
            order.action_confirm()

    def test_confirm_requires_positive_qty(self):
        """Cannot confirm order with total_qty = 0."""
        order = self._create_order()
        self._add_line(order, qty=0)
        with self.assertRaises(ValidationError):
            order.action_confirm()

    def test_confirm_with_valid_lines(self):
        """Order with valid lines can be confirmed."""
        order = self._create_order()
        self._add_line(order, qty=100)
        order.action_confirm()
        self.assertEqual(order.state, 'confirmed')

    # -------------------------------------------------------------------------
    # Delivery date validation
    # -------------------------------------------------------------------------
    def test_delivery_date_before_order_date(self):
        """Delivery date cannot be before order date."""
        with self.assertRaises(ValidationError):
            self._create_order(
                order_date=date.today(),
                delivery_date=date.today() - timedelta(days=30),
            )

    def test_delivery_date_after_order_date(self):
        """Delivery date after order date is valid."""
        order = self._create_order(
            delivery_date=date.today() + timedelta(days=30),
        )
        self.assertTrue(order.delivery_date >= order.order_date)

    # -------------------------------------------------------------------------
    # Late order detection
    # -------------------------------------------------------------------------
    def test_is_late_past_delivery(self):
        """Order past delivery date and not done should be late."""
        order = self._create_order(
            order_date=date.today() - timedelta(days=30),
            delivery_date=date.today() - timedelta(days=1),
        )
        self.assertTrue(order.is_late)
        self.assertFalse(order.is_on_time)

    def test_is_not_late_done(self):
        """Done order past delivery date is not late."""
        order = self._create_order(
            order_date=date.today() - timedelta(days=30),
            delivery_date=date.today() - timedelta(days=1),
        )
        self._add_line(order, qty=100)
        order.action_confirm()
        order.write({'state': 'done'})
        self.assertFalse(order.is_late)

    def test_is_not_late_future(self):
        """Order with future delivery date is not late."""
        order = self._create_order(
            delivery_date=date.today() + timedelta(days=30),
        )
        self.assertFalse(order.is_late)
        self.assertTrue(order.is_on_time)

    def test_days_remaining_calculation(self):
        """Days remaining should be correct delta."""
        order = self._create_order(
            delivery_date=date.today() + timedelta(days=10),
        )
        self.assertEqual(order.days_remaining, 10)

    def test_search_is_late(self):
        """Late orders can be found via domain on delivery_date."""
        order = self._create_order(
            order_date=date.today() - timedelta(days=30),
            delivery_date=date.today() - timedelta(days=5),
        )
        # Verify order is truly late via computed field
        self.assertTrue(order.is_late)
        # Verify search by delivery_date domain finds the order
        late_orders = self.env['garment.order'].search([
            ('delivery_date', '<', date.today()),
            ('state', 'not in', ('done', 'cancelled')),
            ('id', '=', order.id),
        ])
        self.assertEqual(len(late_orders), 1)

    # -------------------------------------------------------------------------
    # Order line constraints
    # -------------------------------------------------------------------------
    def test_negative_quantity_rejected(self):
        """Negative quantity on order line should be rejected."""
        order = self._create_order()
        with self.assertRaises(ValidationError):
            self._add_line(order, qty=-10)

    def test_duplicate_color_size_rejected(self):
        """Duplicate color+size in same order should be rejected."""
        order = self._create_order()
        self._add_line(order, color=self.color, size=self.size, qty=100)
        with self.assertRaises(ValidationError):
            self._add_line(order, color=self.color, size=self.size, qty=50)

    def test_different_color_same_size_ok(self):
        """Different colors with same size is valid."""
        order = self._create_order()
        self._add_line(order, color=self.color, size=self.size, qty=100)
        self._add_line(order, color=self.color2, size=self.size, qty=50)
        self.assertEqual(len(order.line_ids), 2)

    def test_same_color_different_size_ok(self):
        """Same color with different sizes is valid."""
        order = self._create_order()
        self._add_line(order, color=self.color, size=self.size, qty=100)
        self._add_line(order, color=self.color, size=self.size2, qty=50)
        self.assertEqual(len(order.line_ids), 2)

    # -------------------------------------------------------------------------
    # Computed fields
    # -------------------------------------------------------------------------
    def test_total_qty_computed(self):
        """Total qty should sum order lines."""
        order = self._create_order()
        self._add_line(order, color=self.color, size=self.size, qty=100)
        self._add_line(order, color=self.color2, size=self.size, qty=200)
        self.assertEqual(order.total_qty, 300)

    def test_total_amount_computed(self):
        """Total amount should be qty × unit_price."""
        order = self._create_order(unit_price=5.0)
        self._add_line(order, color=self.color, size=self.size, qty=100)
        self.assertAlmostEqual(order.total_amount, 500.0, places=2)

    # -------------------------------------------------------------------------
    # Workflow
    # -------------------------------------------------------------------------
    def test_full_workflow(self):
        """Complete order workflow from draft to done."""
        order = self._create_order(
            delivery_date=date.today() + timedelta(days=60),
        )
        self._add_line(order, qty=500)
        self.assertEqual(order.state, 'draft')

        order.action_confirm()
        self.assertEqual(order.state, 'confirmed')
        order.action_material()
        self.assertEqual(order.state, 'material')
        order.action_cutting()
        self.assertEqual(order.state, 'cutting')
        order.action_sewing()
        self.assertEqual(order.state, 'sewing')
        order.action_finishing()
        self.assertEqual(order.state, 'finishing')
        order.action_qc()
        self.assertEqual(order.state, 'qc')
        order.action_packing()
        self.assertEqual(order.state, 'packing')
        order.action_shipped()
        self.assertEqual(order.state, 'shipped')
        order.action_done()
        self.assertEqual(order.state, 'done')

    def test_cancel_and_reset(self):
        """Cancel order and reset to draft."""
        order = self._create_order()
        self._add_line(order, qty=100)
        order.action_confirm()
        order.action_cancel()
        self.assertEqual(order.state, 'cancelled')
        order.action_reset_draft()
        self.assertEqual(order.state, 'draft')
