from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestGarmentVehicle(TransactionCase):
    """Tests for garment.vehicle."""

    def test_create_vehicle(self):
        vehicle = self.env['garment.vehicle'].create({
            'name': 'Xe Tải 1.5T',
            'plate_number': '51C-12345',
            'vehicle_type': 'truck_small',
            'max_weight': 1500,
        })
        self.assertEqual(vehicle.state, 'available')
        self.assertEqual(vehicle.delivery_count, 0)

    def test_plate_unique(self):
        self.env['garment.vehicle'].create({
            'name': 'Xe 1',
            'plate_number': '51C-99999',
            'vehicle_type': 'truck_small',
        })
        with self.assertRaises(Exception):
            self.env['garment.vehicle'].create({
                'name': 'Xe 2',
                'plate_number': '51C-99999',
                'vehicle_type': 'van',
            })


@tagged('post_install', '-at_install')
class TestDeliveryOrder(TransactionCase):
    """Tests for garment.delivery.order."""

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
        })

    def test_create_delivery(self):
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Ho Chi Minh City',
        })
        self.assertTrue(delivery.name.startswith('GH-'))
        self.assertEqual(delivery.state, 'draft')

    def test_full_workflow(self):
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Ha Noi',
            'line_ids': [(0, 0, {
                'style_code': 'POLO-001',
                'color': 'White',
                'size': 'M',
                'quantity': 500,
            })],
        })
        delivery.action_confirm()
        self.assertEqual(delivery.state, 'confirmed')
        delivery.action_loading()
        self.assertEqual(delivery.state, 'loading')
        delivery.action_in_transit()
        self.assertEqual(delivery.state, 'in_transit')
        delivery.action_delivered()
        self.assertEqual(delivery.state, 'delivered')

    def test_confirm_requires_lines(self):
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Da Nang',
        })
        with self.assertRaises(UserError):
            delivery.action_confirm()

    def test_cannot_cancel_delivered(self):
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Can Tho',
            'line_ids': [(0, 0, {
                'style_code': 'SHIRT-001',
                'color': 'Blue',
                'size': 'L',
                'quantity': 300,
            })],
        })
        delivery.action_confirm()
        delivery.action_loading()
        delivery.action_in_transit()
        delivery.action_delivered()
        with self.assertRaises(UserError):
            delivery.action_cancel()

    def test_total_qty_compute(self):
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Hai Phong',
            'line_ids': [
                (0, 0, {'style_code': 'T01', 'quantity': 200}),
                (0, 0, {'style_code': 'T02', 'quantity': 300}),
            ],
        })
        self.assertEqual(delivery.total_qty, 500)

    def test_line_quantity_positive(self):
        """Delivery line quantity must be > 0."""
        with self.assertRaises(ValidationError):
            self.env['garment.delivery.order'].create({
                'delivery_type': 'customer',
                'partner_id': self.partner.id,
                'ship_to': 'Test',
                'line_ids': [(0, 0, {
                    'style_code': 'T01',
                    'quantity': 0,
                })],
            })

    def test_line_quantity_negative(self):
        """Delivery line quantity cannot be negative."""
        with self.assertRaises(ValidationError):
            self.env['garment.delivery.order'].create({
                'delivery_type': 'customer',
                'partner_id': self.partner.id,
                'ship_to': 'Test',
                'line_ids': [(0, 0, {
                    'style_code': 'T01',
                    'quantity': -10,
                })],
            })

    def test_expected_date_validation(self):
        """Expected date must be >= delivery date."""
        from datetime import date
        with self.assertRaises(ValidationError):
            self.env['garment.delivery.order'].create({
                'delivery_type': 'customer',
                'partner_id': self.partner.id,
                'ship_to': 'Test',
                'date': date(2026, 3, 15),
                'expected_date': date(2026, 3, 10),
            })

    def test_expected_date_same_ok(self):
        """Expected date = delivery date is valid."""
        from datetime import date
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Test',
            'date': date(2026, 3, 15),
            'expected_date': date(2026, 3, 15),
        })
        self.assertEqual(delivery.expected_date, date(2026, 3, 15))

    def test_reset_draft_from_cancelled(self):
        """Can reset to draft from cancelled state."""
        delivery = self.env['garment.delivery.order'].create({
            'delivery_type': 'customer',
            'partner_id': self.partner.id,
            'ship_to': 'Test',
            'line_ids': [(0, 0, {'style_code': 'T01', 'quantity': 100})],
        })
        delivery.action_confirm()
        delivery.action_cancel()
        self.assertEqual(delivery.state, 'cancelled')
        delivery.action_reset_draft()
        self.assertEqual(delivery.state, 'draft')
