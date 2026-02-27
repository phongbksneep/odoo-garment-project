from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from odoo import fields


@tagged('post_install', '-at_install')
class TestSample(TransactionCase):
    """Unit tests and E2E tests for garment.sample."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Sample',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-SMP-001',
            'code': 'ST-SMP-001',
            'category': 'shirt',
        })

    def _create_sample(self, **kwargs):
        vals = {
            'buyer_id': self.partner.id,
            'style_id': self.style.id,
            'sample_type': 'proto',
            'quantity': 3,
            'required_date': fields.Date.today(),
        }
        vals.update(kwargs)
        return self.env['garment.sample'].create(vals)

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_sample_sequence(self):
        """Test sample gets a sequence number."""
        sample = self._create_sample()
        self.assertNotEqual(sample.name, 'New')
        self.assertTrue(sample.name.startswith('SMP/'))

    def test_default_state_is_draft(self):
        sample = self._create_sample()
        self.assertEqual(sample.state, 'draft')

    def test_start_development(self):
        sample = self._create_sample()
        sample.action_start()
        self.assertEqual(sample.state, 'in_progress')

    def test_cannot_start_from_submitted(self):
        sample = self._create_sample()
        sample.action_start()
        sample.action_submit()
        with self.assertRaises(UserError):
            sample.action_start()

    def test_submit_sample(self):
        sample = self._create_sample()
        sample.action_start()
        sample.action_submit()
        self.assertEqual(sample.state, 'submitted')

    def test_approve_sample(self):
        sample = self._create_sample()
        sample.action_start()
        sample.action_submit()
        sample.action_approve()
        self.assertEqual(sample.state, 'approved')

    def test_reject_sample(self):
        sample = self._create_sample()
        sample.action_start()
        sample.action_submit()
        sample.action_reject()
        self.assertEqual(sample.state, 'rejected')

    def test_revise_increments_revision(self):
        sample = self._create_sample()
        sample.action_start()
        sample.action_submit()
        sample.action_reject()
        initial_rev = sample.revision
        sample.action_revise()
        self.assertEqual(sample.revision, initial_rev + 1)
        self.assertEqual(sample.state, 'in_progress')

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_sample_workflow(self):
        """E2E: Create → Start → Submit → Reject → Revise → Submit → Approve."""
        # Step 1: Create
        sample = self._create_sample(
            sample_type='fit',
            quantity=2,
        )
        self.assertEqual(sample.state, 'draft')
        self.assertEqual(sample.revision, 0)

        # Step 2: Start development
        sample.action_start()
        self.assertEqual(sample.state, 'in_progress')

        # Step 3: Submit for approval
        sample.action_submit()
        self.assertEqual(sample.state, 'submitted')

        # Step 4: Buyer rejects
        sample.action_reject()
        self.assertEqual(sample.state, 'rejected')

        # Step 5: Revise
        sample.action_revise()
        self.assertEqual(sample.state, 'in_progress')
        self.assertEqual(sample.revision, 1)

        # Step 6: Re-submit
        sample.action_submit()
        self.assertEqual(sample.state, 'submitted')

        # Step 7: Approve
        sample.action_approve()
        self.assertEqual(sample.state, 'approved')

    def test_e2e_add_comments(self):
        """E2E: Create sample, add buyer comments."""
        sample = self._create_sample()
        self.env['garment.sample.comment'].create({
            'sample_id': sample.id,
            'comment': 'Button color needs to match Pantone 1234',
            'user_id': self.env.user.id,
        })
        self.assertEqual(len(sample.comment_ids), 1)
