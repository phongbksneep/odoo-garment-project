from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestCrmLead(TransactionCase):
    """Tests for garment.crm.lead."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer CRM',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Style CRM Test',
            'code': 'ST-CRM-01',
            'category': 'shirt',
        })

    def _create_lead(self, **kwargs):
        vals = {
            'name': 'Test Lead',
            'lead_type': 'lead',
            'partner_id': self.partner.id,
            'expected_qty': 5000,
            'expected_revenue': 25000.0,
        }
        vals.update(kwargs)
        return self.env['garment.crm.lead'].create(vals)

    def test_create_lead(self):
        lead = self._create_lead()
        self.assertTrue(lead.code.startswith('LEAD-'))
        self.assertEqual(lead.stage, 'new')
        self.assertEqual(lead.lead_type, 'lead')

    def test_lead_sequence(self):
        lead1 = self._create_lead(name='Lead 1')
        lead2 = self._create_lead(name='Lead 2')
        self.assertNotEqual(lead1.code, lead2.code)

    def test_convert_to_opportunity(self):
        lead = self._create_lead()
        lead.action_convert_opportunity()
        self.assertEqual(lead.lead_type, 'opportunity')
        self.assertEqual(lead.stage, 'qualified')

    def test_cannot_convert_already_opportunity(self):
        lead = self._create_lead(lead_type='opportunity')
        with self.assertRaises(UserError):
            lead.action_convert_opportunity()

    def test_pipeline_flow(self):
        lead = self._create_lead(lead_type='opportunity')
        lead.action_qualify()
        self.assertEqual(lead.stage, 'qualified')
        lead.action_propose()
        self.assertEqual(lead.stage, 'proposal')
        lead.action_negotiate()
        self.assertEqual(lead.stage, 'negotiation')
        lead.action_won()
        self.assertEqual(lead.stage, 'won')
        self.assertEqual(lead.probability, 100.0)

    def test_lost(self):
        lead = self._create_lead(lead_type='opportunity')
        lead.action_qualify()
        lead.action_lost()
        self.assertEqual(lead.stage, 'lost')
        self.assertEqual(lead.probability, 0.0)

    def test_reset_from_lost(self):
        lead = self._create_lead(lead_type='opportunity')
        lead.action_qualify()
        lead.action_lost()
        lead.action_reset()
        self.assertEqual(lead.stage, 'new')
        self.assertFalse(lead.lost_reason)

    def test_create_order_from_won(self):
        lead = self._create_lead(lead_type='opportunity')
        lead.action_qualify()
        lead.action_propose()
        lead.action_won()
        result = lead.action_create_order()
        self.assertTrue(lead.garment_order_id)
        self.assertEqual(result['res_model'], 'garment.order')

    def test_cannot_create_order_if_not_won(self):
        lead = self._create_lead(lead_type='opportunity')
        with self.assertRaises(UserError):
            lead.action_create_order()

    def test_cannot_create_order_twice(self):
        lead = self._create_lead(lead_type='opportunity')
        lead.action_qualify()
        lead.action_propose()
        lead.action_won()
        lead.action_create_order()
        with self.assertRaises(UserError):
            lead.action_create_order()

    def test_cannot_create_order_without_partner(self):
        lead = self._create_lead(partner_id=False)
        lead.write({'stage': 'won'})
        with self.assertRaises(UserError):
            lead.action_create_order()

    # --- Constraint tests ---

    def test_negative_qty_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_lead(expected_qty=-100)

    def test_negative_revenue_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_lead(expected_revenue=-5000)

    def test_probability_over_100_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_lead(probability=150)

    def test_probability_negative_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_lead(probability=-10)

    # --- Computed field tests ---

    def test_weighted_revenue(self):
        lead = self._create_lead(expected_revenue=10000, probability=30)
        self.assertAlmostEqual(lead.weighted_revenue, 3000.0)

    def test_weighted_revenue_zero_probability(self):
        lead = self._create_lead(expected_revenue=10000, probability=0)
        self.assertAlmostEqual(lead.weighted_revenue, 0.0)

    def test_days_in_pipeline(self):
        lead = self._create_lead()
        self.assertEqual(lead.days_in_pipeline, 0)

    def test_is_overdue_past_close_date(self):
        lead = self._create_lead(
            expected_close_date=fields.Date.today() - timedelta(days=5),
        )
        self.assertTrue(lead.is_overdue)

    def test_is_not_overdue_won(self):
        lead = self._create_lead(
            expected_close_date=fields.Date.today() - timedelta(days=5),
        )
        lead.action_won()
        self.assertFalse(lead.is_overdue)

    def test_is_not_overdue_future(self):
        lead = self._create_lead(
            expected_close_date=fields.Date.today() + timedelta(days=10),
        )
        self.assertFalse(lead.is_overdue)

    def test_search_is_overdue(self):
        lead = self._create_lead(
            name='Overdue Lead Test',
            expected_close_date=fields.Date.today() - timedelta(days=5),
        )
        self.assertTrue(lead.is_overdue)
        # Verify search domain directly
        domain = [
            ('expected_close_date', '<', fields.Date.today()),
            ('stage', 'not in', ['won', 'lost']),
            ('id', '=', lead.id),
        ]
        found = self.env['garment.crm.lead'].search(domain)
        self.assertIn(lead.id, found.ids)


@tagged('post_install', '-at_install')
class TestCrmFeedback(TransactionCase):
    """Tests for garment.crm.feedback."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Feedback',
            'customer_rank': 1,
        })

    def _create_feedback(self, **kwargs):
        vals = {
            'name': 'Test Feedback',
            'feedback_type': 'complaint',
            'partner_id': self.partner.id,
            'category': 'quality',
            'severity': 'high',
            'description': '<p>Lỗi chất lượng đơn hàng</p>',
        }
        vals.update(kwargs)
        return self.env['garment.crm.feedback'].create(vals)

    def test_create_feedback(self):
        fb = self._create_feedback()
        self.assertTrue(fb.code.startswith('FB-'))
        self.assertEqual(fb.state, 'draft')

    def test_process_requires_assigned_to(self):
        fb = self._create_feedback()
        with self.assertRaises(UserError):
            fb.action_process()

    def test_process_flow(self):
        fb = self._create_feedback(assigned_to=self.env.user.id)
        fb.action_process()
        self.assertEqual(fb.state, 'processing')

    def test_resolve_requires_resolution(self):
        fb = self._create_feedback(assigned_to=self.env.user.id)
        fb.action_process()
        with self.assertRaises(UserError):
            fb.action_resolve()

    def test_full_flow(self):
        fb = self._create_feedback(assigned_to=self.env.user.id)
        fb.action_process()
        fb.write({'resolution': '<p>Đã xử lý</p>'})
        fb.action_resolve()
        self.assertEqual(fb.state, 'resolved')
        self.assertTrue(fb.resolution_date)
        fb.action_close()
        self.assertEqual(fb.state, 'closed')

    def test_reopen(self):
        fb = self._create_feedback(assigned_to=self.env.user.id)
        fb.action_process()
        fb.write({'resolution': '<p>Fix</p>'})
        fb.action_resolve()
        fb.action_reopen()
        self.assertEqual(fb.state, 'processing')
        self.assertFalse(fb.resolution_date)

    # --- Computed field tests ---

    def test_days_open_for_open_feedback(self):
        fb = self._create_feedback(
            assigned_to=self.env.user.id,
            date=fields.Date.today() - timedelta(days=10),
        )
        self.assertEqual(fb.days_open, 10)

    def test_days_open_zero_for_resolved(self):
        fb = self._create_feedback(
            assigned_to=self.env.user.id,
            date=fields.Date.today() - timedelta(days=5),
        )
        fb.action_process()
        fb.write({'resolution': '<p>Done</p>'})
        fb.action_resolve()
        self.assertEqual(fb.days_open, 0)

    def test_resolution_days(self):
        fb = self._create_feedback(
            assigned_to=self.env.user.id,
            date=fields.Date.today() - timedelta(days=7),
        )
        fb.action_process()
        fb.write({'resolution': '<p>Done</p>'})
        fb.action_resolve()
        self.assertEqual(fb.resolution_days, 7)

    def test_is_overdue_follow_up(self):
        fb = self._create_feedback(
            follow_up_date=fields.Date.today() - timedelta(days=3),
        )
        self.assertTrue(fb.is_overdue)

    def test_not_overdue_future_follow_up(self):
        fb = self._create_feedback(
            follow_up_date=fields.Date.today() + timedelta(days=3),
        )
        self.assertFalse(fb.is_overdue)

    def test_search_is_overdue(self):
        fb = self._create_feedback(
            name='Overdue FB',
            follow_up_date=fields.Date.today() - timedelta(days=3),
        )
        self.assertTrue(fb.is_overdue)
        # Verify search domain directly
        domain = [
            ('follow_up_date', '<', fields.Date.today()),
            ('state', 'in', ['draft', 'processing']),
            ('id', '=', fb.id),
        ]
        found = self.env['garment.crm.feedback'].search(domain)
        self.assertIn(fb.id, found.ids)


@tagged('post_install', '-at_install')
class TestCustomerProfile(TransactionCase):
    """Tests for res.partner garment buyer fields."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = cls.env['garment.style'].create({
            'name': 'Style Count Test',
            'code': 'ST-CNT-01',
            'category': 'shirt',
        })
        cls.buyer = cls.env['res.partner'].create({
            'name': 'Buyer Count Test',
            'customer_rank': 1,
            'is_garment_buyer': True,
            'buyer_code': 'BUY-001',
            'buyer_type': 'brand',
        })

    def test_buyer_fields(self):
        self.assertTrue(self.buyer.is_garment_buyer)
        self.assertEqual(self.buyer.buyer_code, 'BUY-001')
        self.assertEqual(self.buyer.buyer_type, 'brand')

    def test_garment_order_count(self):
        self.env['garment.order'].create({
            'customer_id': self.buyer.id,
            'style_id': self.style.id,
        })
        self.buyer._compute_garment_counts()
        self.assertEqual(self.buyer.garment_order_count, 1)

    def test_crm_lead_count(self):
        self.env['garment.crm.lead'].create({
            'name': 'Lead Count Test',
            'partner_id': self.buyer.id,
        })
        self.buyer._compute_garment_counts()
        self.assertEqual(self.buyer.crm_lead_count, 1)

    def test_feedback_count(self):
        self.env['garment.crm.feedback'].create({
            'name': 'FB Count Test',
            'partner_id': self.buyer.id,
            'category': 'quality',
            'description': '<p>Test</p>',
        })
        self.buyer._compute_garment_counts()
        self.assertEqual(self.buyer.feedback_count, 1)

    def test_action_view_orders(self):
        result = self.buyer.action_view_garment_orders()
        self.assertEqual(result['res_model'], 'garment.order')
        self.assertIn(('customer_id', '=', self.buyer.id), result['domain'])

    def test_action_view_leads(self):
        result = self.buyer.action_view_crm_leads()
        self.assertEqual(result['res_model'], 'garment.crm.lead')

    def test_action_view_feedbacks(self):
        result = self.buyer.action_view_feedbacks()
        self.assertEqual(result['res_model'], 'garment.crm.feedback')
