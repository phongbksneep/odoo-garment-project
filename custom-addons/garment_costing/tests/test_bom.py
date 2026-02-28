from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestGarmentBOM(TransactionCase):
    """Tests for garment.bom and garment.bom.line models."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = cls.env['garment.style'].create({
            'name': 'BOM Test Style',
            'code': 'BOM-TST-001',
            'category': 'shirt',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'BOM Test Buyer',
            'customer_rank': 1,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'BOM Test Supplier',
            'supplier_rank': 1,
        })

    def _create_bom(self, **kwargs):
        vals = {
            'style_id': self.style.id,
        }
        vals.update(kwargs)
        return self.env['garment.bom'].create(vals)

    def _add_bom_lines(self, bom):
        """Add sample BOM lines."""
        self.env['garment.bom.line'].create([
            {
                'bom_id': bom.id,
                'material_type': 'fabric',
                'description': 'Vải Cotton TC',
                'uom': 'm',
                'consumption': 1.5,
                'wastage_pct': 3.0,
                'unit_price': 55000,
                'supplier_id': self.supplier.id,
            },
            {
                'bom_id': bom.id,
                'material_type': 'interlining',
                'description': 'Mex Cổ + Manchette',
                'uom': 'm',
                'consumption': 0.15,
                'wastage_pct': 5.0,
                'unit_price': 12000,
            },
            {
                'bom_id': bom.id,
                'material_type': 'button',
                'description': 'Nút Sừng 4 Lỗ',
                'uom': 'pcs',
                'consumption': 8,
                'wastage_pct': 2.0,
                'unit_price': 800,
            },
            {
                'bom_id': bom.id,
                'material_type': 'thread',
                'description': 'Chỉ May Polyester',
                'uom': 'cone',
                'consumption': 0.02,
                'wastage_pct': 5.0,
                'unit_price': 25000,
            },
            {
                'bom_id': bom.id,
                'material_type': 'label',
                'description': 'Nhãn Chính + Nhãn Size',
                'uom': 'set',
                'consumption': 1,
                'wastage_pct': 2.0,
                'unit_price': 1500,
            },
            {
                'bom_id': bom.id,
                'material_type': 'packing',
                'description': 'Polybag + Carton',
                'uom': 'set',
                'consumption': 1,
                'wastage_pct': 0,
                'unit_price': 3000,
            },
        ])

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_bom_sequence(self):
        """BOM gets auto-generated name from sequence."""
        bom = self._create_bom()
        self.assertNotEqual(bom.name, 'New')
        self.assertTrue(bom.name.startswith('BOM/'))

    def test_bom_line_amount_compute(self):
        """Amount per piece = consumption * (1 + wastage%) * unit_price."""
        bom = self._create_bom()
        line = self.env['garment.bom.line'].create({
            'bom_id': bom.id,
            'material_type': 'fabric',
            'description': 'Test Fabric',
            'consumption': 1.5,
            'wastage_pct': 10.0,
            'unit_price': 100000,
        })
        # 1.5 * 1.10 * 100000 = 165000
        self.assertAlmostEqual(line.amount_per_pc, 165000, places=2)

    def test_bom_totals(self):
        """Total fabric consumption and total material cost."""
        bom = self._create_bom()
        self._add_bom_lines(bom)
        bom.invalidate_recordset()
        self.assertEqual(bom.total_lines, 6)
        # Fabric lines: fabric(1.5) + interlining is NOT fabric type
        # Actually fabric = 1.5, lining = 0, interlining != fabric/lining
        self.assertAlmostEqual(bom.total_fabric_consumption, 1.5, places=2)
        self.assertGreater(bom.total_material_cost, 0)

    def test_bom_state_transitions(self):
        """Test BOM workflow: draft → confirmed → approved."""
        bom = self._create_bom()
        self._add_bom_lines(bom)
        self.assertEqual(bom.state, 'draft')

        bom.action_confirm()
        self.assertEqual(bom.state, 'confirmed')

        bom.action_approve()
        self.assertEqual(bom.state, 'approved')

    def test_bom_confirm_requires_lines(self):
        """Cannot confirm BOM without lines."""
        bom = self._create_bom()
        with self.assertRaises(UserError):
            bom.action_confirm()

    def test_bom_approve_requires_confirmed(self):
        """Cannot approve BOM from draft state."""
        bom = self._create_bom()
        self._add_bom_lines(bom)
        with self.assertRaises(UserError):
            bom.action_approve()

    def test_bom_new_version(self):
        """Creating a new version copies the BOM."""
        bom = self._create_bom()
        self._add_bom_lines(bom)
        bom.action_confirm()
        bom.action_approve()

        result = bom.action_new_version()
        new_bom = self.env['garment.bom'].browse(result['res_id'])
        self.assertEqual(new_bom.version, 2)
        self.assertEqual(new_bom.state, 'draft')
        self.assertEqual(len(new_bom.line_ids), len(bom.line_ids))

    def test_bom_cancel_and_reset(self):
        """Cancel and reset draft."""
        bom = self._create_bom()
        self._add_bom_lines(bom)
        bom.action_confirm()
        bom.action_cancel()
        self.assertEqual(bom.state, 'cancelled')
        bom.action_reset_draft()
        self.assertEqual(bom.state, 'draft')

    def _get_cost_lines(self, cost_sheet):
        """Get all cost lines for a cost sheet."""
        return self.env['garment.cost.line'].search([
            ('cost_sheet_id', '=', cost_sheet.id),
        ])

    # -------------------------------------------------------------------------
    # Integration: BOM → Cost Sheet
    # -------------------------------------------------------------------------
    def test_load_bom_into_cost_sheet(self):
        """Load approved BOM lines into cost sheet."""
        bom = self._create_bom()
        self._add_bom_lines(bom)
        bom.action_confirm()
        bom.action_approve()

        cs = self.env['garment.cost.sheet'].create({
            'buyer_id': self.partner.id,
            'style_id': self.style.id,
            'order_qty': 1000,
            'smv': 15.0,
            'target_efficiency': 65.0,
        })
        cs.action_load_from_bom()
        cost_lines = self._get_cost_lines(cs)
        self.assertEqual(len(cost_lines), 6)

        # Check type mapping
        fabric_lines = cost_lines.filtered(lambda l: l.cost_type == 'fabric')
        accessory_lines = cost_lines.filtered(lambda l: l.cost_type == 'accessory')
        packing_lines = cost_lines.filtered(lambda l: l.cost_type == 'packing')
        self.assertEqual(len(fabric_lines), 1)   # fabric
        self.assertEqual(len(accessory_lines), 4)  # interlining, button, thread, label
        self.assertEqual(len(packing_lines), 1)   # packing

    def test_load_bom_no_bom_raises_error(self):
        """Error when no BOM exists for style."""
        style2 = self.env['garment.style'].create({
            'name': 'No BOM Style',
            'code': 'NO-BOM-001',
            'category': 'pants',
        })
        cs = self.env['garment.cost.sheet'].create({
            'buyer_id': self.partner.id,
            'style_id': style2.id,
            'order_qty': 500,
            'smv': 10.0,
            'target_efficiency': 65.0,
        })
        with self.assertRaises(UserError):
            cs.action_load_from_bom()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_bom_to_costing(self):
        """E2E: Create BOM → Approve → Create Cost Sheet → Load from BOM → Confirm."""
        # Step 1: Create and populate BOM
        bom = self._create_bom()
        self._add_bom_lines(bom)

        # Step 2: Approve BOM
        bom.action_confirm()
        bom.action_approve()
        self.assertEqual(bom.state, 'approved')

        # Step 3: Create cost sheet
        cs = self.env['garment.cost.sheet'].create({
            'buyer_id': self.partner.id,
            'style_id': self.style.id,
            'order_qty': 2000,
            'smv': 12.0,
            'target_efficiency': 60.0,
        })

        # Step 4: Load from BOM
        cs.action_load_from_bom()
        cost_lines = self._get_cost_lines(cs)
        self.assertEqual(len(cost_lines), 6)

        # Step 5: Verify cost calculations
        cs.invalidate_recordset()
        self.assertGreater(cs.fabric_cost_per_pc, 0)
        self.assertGreater(cs.accessory_cost_per_pc, 0)
        self.assertGreater(cs.packing_cost_per_pc, 0)

        # Step 6: Confirm cost sheet
        cs.action_confirm()
        self.assertEqual(cs.state, 'confirmed')
