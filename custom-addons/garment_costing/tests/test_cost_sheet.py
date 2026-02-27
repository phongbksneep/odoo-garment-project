from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestCostSheet(TransactionCase):
    """Unit tests and E2E tests for garment.cost.sheet."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-TEST-001',
            'code': 'ST-CST-001',
            'category': 'shirt',
        })

    def _create_cost_sheet(self, **kwargs):
        vals = {
            'buyer_id': self.partner.id,
            'style_id': self.style.id,
            'order_qty': 1000,
            'smv': 15.0,
            'target_efficiency': 65.0,
        }
        vals.update(kwargs)
        return self.env['garment.cost.sheet'].create(vals)

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_cost_sheet_sequence(self):
        """Test that cost sheet gets a sequence number on creation."""
        cs = self._create_cost_sheet()
        self.assertNotEqual(cs.name, 'New')
        self.assertTrue(cs.name.startswith('CST/'))

    def test_compute_cm_cost(self):
        """Test CM cost computation: actual_min = SMV / (eff/100), cm = actual_min * rate."""
        cs = self._create_cost_sheet(
            smv=15.0,
            cm_rate_per_minute=5000,
            target_efficiency=65.0,
        )
        # actual_min = 15 / 0.65 ≈ 23.077, cm = 23.077 * 5000 ≈ 115384.62
        self.assertGreater(cs.cm_cost, 0)

    def test_compute_material_costs(self):
        """Test material cost totals from cost lines."""
        cs = self._create_cost_sheet()
        self.env['garment.cost.line'].create([
            {
                'cost_sheet_id': cs.id,
                'description': 'Main Fabric',
                'cost_type': 'fabric',
                'consumption': 1.5,
                'unit_price': 50000,
            },
            {
                'cost_sheet_id': cs.id,
                'description': 'Buttons',
                'cost_type': 'accessory',
                'consumption': 6,
                'unit_price': 500,
            },
        ])
        cs.invalidate_recordset()
        self.assertEqual(cs.fabric_cost_per_pc, 75000)
        self.assertEqual(cs.accessory_cost_per_pc, 3000)

    def test_state_transitions(self):
        """Test cost sheet workflow transitions."""
        cs = self._create_cost_sheet()
        self.assertEqual(cs.state, 'draft')

        cs.action_confirm()
        self.assertEqual(cs.state, 'confirmed')

        cs.action_approve()
        self.assertEqual(cs.state, 'approved')

    def test_cannot_approve_without_confirm(self):
        """Test that approve fails from draft state."""
        cs = self._create_cost_sheet()
        with self.assertRaises(UserError):
            cs.action_approve()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_costing_workflow(self):
        """E2E: Create cost sheet → add lines → confirm → approve."""
        # Step 1: Create cost sheet
        cs = self._create_cost_sheet(
            smv=12.0,
            cm_rate_per_minute=4500,
            order_qty=5000,
        )
        self.assertEqual(cs.state, 'draft')

        # Step 2: Add material cost lines
        self.env['garment.cost.line'].create([
            {
                'cost_sheet_id': cs.id,
                'description': 'Cotton Fabric',
                'cost_type': 'fabric',
                'consumption': 1.8,
                'unit_price': 60000,
            },
            {
                'cost_sheet_id': cs.id,
                'description': 'Zipper',
                'cost_type': 'accessory',
                'consumption': 1,
                'unit_price': 5000,
            },
            {
                'cost_sheet_id': cs.id,
                'description': 'Polybag',
                'cost_type': 'packing',
                'consumption': 1,
                'unit_price': 1000,
            },
        ])

        # Step 3: Verify computations
        cs.invalidate_recordset()
        self.assertEqual(cs.fabric_cost_per_pc, 108000)
        self.assertEqual(cs.accessory_cost_per_pc, 5000)
        self.assertEqual(cs.packing_cost_per_pc, 1000)
        self.assertGreater(cs.cm_cost, 0)
        self.assertGreater(cs.selling_price, 0)

        # Step 4: Confirm
        cs.action_confirm()
        self.assertEqual(cs.state, 'confirmed')

        # Step 5: Approve
        cs.action_approve()
        self.assertEqual(cs.state, 'approved')
