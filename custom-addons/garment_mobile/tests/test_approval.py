from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestGarmentApproval(TransactionCase):
    """Test order approval workflow added by garment_mobile."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Approval Test Customer',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Approval Test Style',
            'code': 'APR-001',
            'category': 'shirt',
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
            'delivery_date': '2025-12-31',
            'unit_price': 15.0,
        })

    # ----- field existence -----

    def test_01_approval_fields_exist(self):
        """Approval fields should be present on garment.order."""
        order = self.order
        self.assertTrue(hasattr(order, 'approval_state'))
        self.assertTrue(hasattr(order, 'approval_requested_by'))
        self.assertTrue(hasattr(order, 'approval_requested_date'))
        self.assertTrue(hasattr(order, 'approved_by'))
        self.assertTrue(hasattr(order, 'approval_date'))
        self.assertTrue(hasattr(order, 'rejection_reason'))
        self.assertTrue(hasattr(order, 'approval_note'))

    def test_02_default_approval_state(self):
        """New order should default to 'draft' approval state."""
        self.assertEqual(self.order.approval_state, 'draft')

    # ----- request approval -----

    def test_03_request_approval(self):
        """Test sending an order for approval."""
        self.order.action_request_approval()
        self.assertEqual(self.order.approval_state, 'pending')
        self.assertTrue(self.order.approval_requested_by)
        self.assertTrue(self.order.approval_requested_date)

    def test_04_request_approval_twice_raises(self):
        """Cannot request approval on an already-pending order."""
        self.order.action_request_approval()
        with self.assertRaises(UserError):
            self.order.action_request_approval()

    # ----- approve -----

    def test_05_approve_order(self):
        """Test approving a pending order."""
        self.order.action_request_approval()
        self.order.action_approve()
        self.assertEqual(self.order.approval_state, 'approved')
        self.assertEqual(self.order.state, 'confirmed')
        self.assertTrue(self.order.approved_by)
        self.assertTrue(self.order.approval_date)

    def test_06_approve_non_pending_raises(self):
        """Cannot approve an order not in 'pending' state."""
        with self.assertRaises(UserError):
            self.order.action_approve()

    # ----- reject -----

    def test_07_reject_opens_wizard(self):
        """Reject should return a wizard action."""
        self.order.action_request_approval()
        result = self.order.action_reject()
        self.assertEqual(result['res_model'], 'garment.rejection.wizard')
        self.assertEqual(result['target'], 'new')

    def test_08_rejection_wizard_confirm(self):
        """Test rejection wizard writes reason and changes state."""
        self.order.action_request_approval()
        wizard = self.env['garment.rejection.wizard'].create({
            'order_id': self.order.id,
            'reason': 'Giá quá cao',
        })
        wizard.action_confirm_reject()
        self.assertEqual(self.order.approval_state, 'rejected')
        self.assertEqual(self.order.rejection_reason, 'Giá quá cao')

    # ----- reset -----

    def test_09_reset_approval(self):
        """Test resetting approval back to draft."""
        self.order.action_request_approval()
        self.order.action_reset_approval()
        self.assertEqual(self.order.approval_state, 'draft')
        self.assertFalse(self.order.approved_by)

    # ----- re-submit after rejection -----

    def test_10_resubmit_after_rejection(self):
        """Order can be re-submitted after rejection."""
        self.order.action_request_approval()
        wizard = self.env['garment.rejection.wizard'].create({
            'order_id': self.order.id,
            'reason': 'Thiếu thông tin',
        })
        wizard.action_confirm_reject()
        self.assertEqual(self.order.approval_state, 'rejected')
        # Re-submit
        self.order.action_request_approval()
        self.assertEqual(self.order.approval_state, 'pending')
        # Rejection reason should be cleared
        self.assertFalse(self.order.rejection_reason)

    # ----- full workflow -----

    def test_11_full_approval_workflow(self):
        """Full cycle: draft -> pending -> rejected -> pending -> approved."""
        self.assertEqual(self.order.approval_state, 'draft')
        # Request
        self.order.action_request_approval()
        self.assertEqual(self.order.approval_state, 'pending')
        # Reject
        wizard = self.env['garment.rejection.wizard'].create({
            'order_id': self.order.id,
            'reason': 'Cần xem lại mẫu',
        })
        wizard.action_confirm_reject()
        self.assertEqual(self.order.approval_state, 'rejected')
        # Re-request
        self.order.action_request_approval()
        self.assertEqual(self.order.approval_state, 'pending')
        # Approve
        self.order.action_approve()
        self.assertEqual(self.order.approval_state, 'approved')
        self.assertEqual(self.order.state, 'confirmed')

    # ----- batch operations -----

    def test_12_batch_request_approval(self):
        """Test requesting approval on multiple orders."""
        order2 = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'delivery_date': '2025-11-30',
            'unit_price': 20.0,
        })
        orders = self.order | order2
        orders.action_request_approval()
        for o in orders:
            self.assertEqual(o.approval_state, 'pending')

    def test_13_batch_approve(self):
        """Test approving multiple orders at once."""
        order2 = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'delivery_date': '2025-11-30',
            'unit_price': 20.0,
        })
        orders = self.order | order2
        orders.action_request_approval()
        orders.action_approve()
        for o in orders:
            self.assertEqual(o.approval_state, 'approved')
