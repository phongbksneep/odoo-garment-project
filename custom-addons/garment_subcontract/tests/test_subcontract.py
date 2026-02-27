from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestSubcontractPartner(TransactionCase):
    """Tests for res.partner subcontract extension."""

    def test_partner_subcontractor_fields(self):
        partner = self.env['res.partner'].create({
            'name': 'Test Subcontractor',
            'is_subcontractor': True,
            'subcontract_type': 'sewing',
            'subcontract_capacity': 500,
            'subcontract_rating': 'b',
        })
        self.assertTrue(partner.is_subcontractor)
        self.assertEqual(partner.subcontract_type, 'sewing')
        self.assertEqual(partner.subcontract_order_count, 0)


@tagged('post_install', '-at_install')
class TestSubcontractOrder(TransactionCase):
    """Tests for garment.subcontract.order."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'GC Company ABC',
            'is_subcontractor': True,
            'subcontract_type': 'sewing',
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-SUB-001',
            'code': 'ST-SUB-001',
            'category': 'shirt',
        })

    def _create_order(self, with_lines=True, **kwargs):
        vals = {
            'direction': 'outgoing',
            'work_type': 'sewing',
            'partner_id': self.partner.id,
            'style_id': self.style.id,
            'unit_price': 5000,
            'date_expected': '2026-03-15',
        }
        vals.update(kwargs)
        order = self.env['garment.subcontract.order'].create(vals)
        if with_lines:
            self.env['garment.subcontract.order.line'].create([
                {
                    'order_id': order.id,
                    'description': 'Áo sơ mi trắng - Size M',
                    'qty_ordered': 200,
                    'unit_price': 5000,
                },
                {
                    'order_id': order.id,
                    'description': 'Áo sơ mi trắng - Size L',
                    'qty_ordered': 300,
                    'unit_price': 5000,
                },
            ])
        return order

    def test_sequence_generation(self):
        order = self._create_order()
        self.assertTrue(order.name.startswith('SUB-'))

    def test_totals_compute(self):
        order = self._create_order()
        order.invalidate_recordset()
        self.assertEqual(order.total_qty, 500)
        self.assertEqual(order.total_cost, 2500000)  # 500 × 5000

    def test_completion_rate(self):
        order = self._create_order()
        # Simulate partial receipt
        order.line_ids[0].qty_received = 200
        order.line_ids[1].qty_received = 100
        order.invalidate_recordset()
        self.assertEqual(order.total_received, 300)
        self.assertAlmostEqual(order.completion_rate, 60.0, places=1)

    def test_confirm_requires_lines(self):
        order = self._create_order(with_lines=False)
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_cannot_cancel_done(self):
        order = self._create_order()
        order.action_confirm()
        order.action_send()
        order.action_in_progress()
        order.action_received()
        order.action_qc()
        order.action_done()
        with self.assertRaises(UserError):
            order.action_cancel()

    def test_full_workflow_outgoing(self):
        """E2E: Gửi gia công từ draft → done."""
        order = self._create_order(direction='outgoing')
        self.assertEqual(order.state, 'draft')

        order.action_confirm()
        self.assertEqual(order.state, 'confirmed')

        order.action_send()
        self.assertEqual(order.state, 'sent')
        self.assertTrue(order.date_sent)

        order.action_in_progress()
        self.assertEqual(order.state, 'in_progress')

        order.action_partial_received()
        self.assertEqual(order.state, 'partial_received')

        order.action_received()
        self.assertEqual(order.state, 'received')
        self.assertTrue(order.date_received)

        order.action_qc()
        self.assertEqual(order.state, 'qc')

        order.action_done()
        self.assertEqual(order.state, 'done')

    def test_full_workflow_incoming(self):
        """E2E: Nhận gia công từ draft → done."""
        order = self._create_order(direction='incoming')
        order.action_confirm()
        order.action_send()
        order.action_in_progress()
        order.action_received()
        order.action_qc()
        order.action_done()
        self.assertEqual(order.state, 'done')

    def test_line_qty_validation(self):
        order = self._create_order()
        line = order.line_ids[0]
        with self.assertRaises(ValidationError):
            line.qty_received = 999  # > qty_ordered (200)

    def test_line_accepted_compute(self):
        order = self._create_order()
        line = order.line_ids[0]
        line.qty_received = 190
        line.qty_rejected = 10
        self.assertEqual(line.qty_accepted, 180)

    def test_line_subtotal_compute(self):
        order = self._create_order()
        line = order.line_ids[0]
        # qty_ordered=200, unit_price=5000
        self.assertEqual(line.subtotal, 1000000)

    def test_partner_order_count(self):
        self._create_order()
        self._create_order()
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.subcontract_order_count, 2)

    def test_overdue_detection(self):
        from datetime import date, timedelta
        order = self._create_order(
            date_expected=date.today() - timedelta(days=5)
        )
        order.action_confirm()
        self.assertTrue(order.is_overdue)

    def test_not_overdue_when_done(self):
        from datetime import date, timedelta
        order = self._create_order(
            date_expected=date.today() - timedelta(days=5)
        )
        order.action_confirm()
        order.action_send()
        order.action_in_progress()
        order.action_received()
        order.action_qc()
        order.action_done()
        self.assertFalse(order.is_overdue)
