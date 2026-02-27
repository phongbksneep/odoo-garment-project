from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestCuttingAdvanced(TransactionCase):
    """Unit tests and E2E tests for garment.cutting.order.adv."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-CUT-001',
            'code': 'ST-CUT-001',
            'category': 'shirt',
        })
        cls.fabric = cls.env['garment.fabric'].create({
            'name': 'Cotton 100%',
            'code': 'FAB-CUT-001',
            'fabric_type': 'woven',
            'composition': '100% Cotton',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Cutting',
            'customer_rank': 1,
        })
        # Create garment order (required by production order)
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })
        # Create sewing line for production order
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Line CUT-Test',
            'code': 'LC01',
        })
        # Create production order (required by cutting order)
        cls.production_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.garment_order.id,
            'sewing_line_id': cls.sewing_line.id,
            'planned_qty': 1000,
        })

    def _create_cutting_order(self, **kwargs):
        vals = {
            'production_order_id': self.production_order.id,
            'fabric_id': self.fabric.id,
            'marker_length': 8.5,
            'marker_width': 150.0,
        }
        vals.update(kwargs)
        return self.env['garment.cutting.order.adv'].create(vals)

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_cutting_order_sequence(self):
        co = self._create_cutting_order()
        self.assertNotEqual(co.name, 'New')
        self.assertTrue(co.name.startswith('CUTX/'))

    def test_default_state_is_draft(self):
        co = self._create_cutting_order()
        self.assertEqual(co.state, 'draft')

    def test_marker_efficiency_field(self):
        """Test marker efficiency can be set."""
        co = self._create_cutting_order(
            marker_length=8.5,
            marker_width=150.0,
            marker_efficiency=85.0,
        )
        self.assertEqual(co.marker_efficiency, 85.0)

    def test_add_layers(self):
        co = self._create_cutting_order()
        self.env['garment.cutting.layer'].create({
            'cutting_order_id': co.id,
            'fabric_roll_no': 'ROLL-001',
            'length': 8.5,
        })
        self.assertEqual(len(co.layer_ids), 1)

    def test_add_bundles(self):
        co = self._create_cutting_order()
        size = self.env['garment.size'].search([], limit=1)
        if not size:
            size = self.env['garment.size'].create({
                'name': 'M', 'code': 'M', 'size_type': 'letter',
            })
        self.env['garment.cutting.bundle'].create({
            'cutting_order_id': co.id,
            'bundle_no': 'B001',
            'size_id': size.id,
            'quantity': 25,
        })
        self.assertEqual(len(co.bundle_ids), 1)

    def test_state_transitions(self):
        co = self._create_cutting_order()
        # Add layers before spreading
        self.env['garment.cutting.layer'].create({
            'cutting_order_id': co.id,
            'fabric_roll_no': 'ROLL-001',
            'length': 8.5,
        })

        co.action_start_spreading()
        self.assertEqual(co.state, 'spreading')

        co.action_start_cutting()
        self.assertEqual(co.state, 'cutting')

        co.action_start_numbering()
        self.assertEqual(co.state, 'numbering')

        # Add bundles before done
        size = self.env['garment.size'].search([], limit=1)
        if not size:
            size = self.env['garment.size'].create({
                'name': 'M', 'code': 'M', 'size_type': 'letter',
            })
        self.env['garment.cutting.bundle'].create({
            'cutting_order_id': co.id,
            'bundle_no': 'B001',
            'size_id': size.id,
            'quantity': 25,
        })

        co.action_done()
        self.assertEqual(co.state, 'done')

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_cutting_workflow(self):
        """E2E: Create → add layers → spread → cut → add bundles → number → done."""
        # Step 1: Create order
        co = self._create_cutting_order(
            marker_length=10.0,
        )

        # Step 2: Add layers (spreading)
        for i in range(1, 4):
            self.env['garment.cutting.layer'].create({
                'cutting_order_id': co.id,
                'fabric_roll_no': f'ROLL-00{i}',
                'length': 10.0,
            })
        self.assertEqual(len(co.layer_ids), 3)

        # Step 3: Start spreading
        co.action_start_spreading()
        self.assertEqual(co.state, 'spreading')

        # Step 4: Start cutting
        co.action_start_cutting()
        self.assertEqual(co.state, 'cutting')

        # Step 5: Add bundles
        sizes = self.env['garment.size'].search([], limit=3)
        if not sizes:
            sizes = self.env['garment.size'].create([
                {'name': 'S', 'code': 'S', 'size_type': 'letter'},
                {'name': 'M', 'code': 'M2', 'size_type': 'letter'},
                {'name': 'L', 'code': 'L', 'size_type': 'letter'},
            ])
        for idx, size in enumerate(sizes, 1):
            self.env['garment.cutting.bundle'].create({
                'cutting_order_id': co.id,
                'bundle_no': f'B{idx:03d}',
                'size_id': size.id,
                'quantity': 30,
            })

        # Step 6: Numbering
        co.action_start_numbering()
        self.assertEqual(co.state, 'numbering')

        # Step 7: Done
        co.action_done()
        self.assertEqual(co.state, 'done')
