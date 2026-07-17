from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestOrderWorkflowGuards(TransactionCase):
    """Guard máy trạng thái đơn hàng: không nhảy cóc, không lùi, không xóa."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Buyer Guard Test',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-GRD-001',
            'code': 'ST-GRD-001',
            'category': 'shirt',
        })
        cls.color = cls.env['garment.color'].create({
            'name': 'Đen Guard', 'code': 'BLK-GRD',
        })
        cls.size = cls.env['garment.size'].create({
            'name': 'M-GRD', 'code': 'M-GRD', 'size_type': 'letter',
        })

    def _create_order(self):
        order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'unit_price': 5.0,
        })
        self.env['garment.order.line'].create({
            'order_id': order.id,
            'color_id': self.color.id,
            'size_id': self.size.id,
            'quantity': 100,
        })
        return order

    def _walk_to(self, order, target):
        """Đi đúng pipeline tới trạng thái target."""
        flow = ['confirmed', 'material', 'cutting', 'sewing', 'finishing',
                'qc', 'packing', 'shipped', 'done']
        actions = {
            'confirmed': order.action_confirm,
            'material': order.action_material,
            'cutting': order.action_cutting,
            'sewing': order.action_sewing,
            'finishing': order.action_finishing,
            'qc': order.action_qc,
            'packing': order.action_packing,
            'shipped': order.action_shipped,
            'done': order.action_done,
        }
        for state in flow:
            actions[state]()
            if state == target:
                break

    def test_draft_cannot_jump_to_done(self):
        order = self._create_order()
        with self.assertRaises(UserError):
            order.action_done()

    def test_draft_cannot_jump_to_cutting(self):
        order = self._create_order()
        with self.assertRaises(UserError):
            order.action_cutting()

    def test_cannot_confirm_twice(self):
        order = self._create_order()
        order.action_confirm()
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_no_backward_transition(self):
        order = self._create_order()
        self._walk_to(order, 'cutting')
        with self.assertRaises(UserError):
            order.action_material()

    def test_forward_skip_allowed(self):
        """Cho phép đi tới bỏ qua giai đoạn (đơn không cần giặt/hoàn thiện)."""
        order = self._create_order()
        order.action_confirm()
        order.action_cutting()
        self.assertEqual(order.state, 'cutting')

    def test_done_is_terminal(self):
        order = self._create_order()
        self._walk_to(order, 'done')
        with self.assertRaises(UserError):
            order.action_cancel()
        with self.assertRaises(UserError):
            order.action_reset_draft()

    def test_cannot_cancel_shipped(self):
        order = self._create_order()
        self._walk_to(order, 'shipped')
        with self.assertRaises(UserError):
            order.action_cancel()

    def test_cancel_then_reset_draft_ok(self):
        order = self._create_order()
        order.action_confirm()
        order.action_cancel()
        order.action_reset_draft()
        self.assertEqual(order.state, 'draft')

    def test_reset_draft_only_from_confirmed_or_cancelled(self):
        order = self._create_order()
        self._walk_to(order, 'sewing')
        with self.assertRaises(UserError):
            order.action_reset_draft()

    def test_cannot_delete_confirmed(self):
        order = self._create_order()
        order.action_confirm()
        with self.assertRaises(UserError):
            order.unlink()

    def test_delete_draft_ok(self):
        order = self._create_order()
        order.unlink()
        self.assertFalse(order.exists())

    def test_delete_cancelled_ok(self):
        order = self._create_order()
        order.action_confirm()
        order.action_cancel()
        order.unlink()
        self.assertFalse(order.exists())
