from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestGarmentInventory(TransactionCase):
    """Tests for garment.inventory model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inventory = cls.env['garment.inventory'].create({
            'warehouse_type': 'finished',
        })

    def test_create_sequence(self):
        self.assertTrue(self.inventory.name.startswith('KK-'))

    def test_default_state(self):
        self.assertEqual(self.inventory.state, 'draft')

    def test_start_requires_lines(self):
        with self.assertRaises(UserError):
            self.inventory.action_start()

    def test_add_line_and_start(self):
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'Test Product',
            'item_code': 'TP001',
            'expected_qty': 100,
            'actual_qty': 95,
        })
        self.inventory.action_start()
        self.assertEqual(self.inventory.state, 'in_progress')

    def test_line_diff_computation(self):
        line = self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'Test',
            'expected_qty': 100,
            'actual_qty': 90,
        })
        self.assertEqual(line.diff_qty, -10)
        self.assertEqual(line.status, 'deficit')
        self.assertAlmostEqual(line.diff_percent, -10.0)

    def test_line_surplus(self):
        line = self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'fabric',
            'item_name': 'Vải Test',
            'expected_qty': 50,
            'actual_qty': 55,
        })
        self.assertEqual(line.diff_qty, 5)
        self.assertEqual(line.status, 'surplus')

    def test_line_ok(self):
        line = self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'accessory',
            'item_name': 'Nút áo',
            'expected_qty': 200,
            'actual_qty': 200,
        })
        self.assertEqual(line.diff_qty, 0)
        self.assertEqual(line.status, 'ok')

    def test_totals_computation(self):
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'A',
            'expected_qty': 100,
            'actual_qty': 90,
        })
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'B',
            'expected_qty': 50,
            'actual_qty': 50,
        })
        self.assertEqual(self.inventory.total_expected_qty, 150)
        self.assertEqual(self.inventory.total_actual_qty, 140)
        self.assertEqual(self.inventory.total_diff_qty, -10)
        self.assertEqual(self.inventory.diff_count, 1)

    def test_workflow_full(self):
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'Test',
            'expected_qty': 100,
            'actual_qty': 100,
        })
        self.inventory.action_start()
        self.assertEqual(self.inventory.state, 'in_progress')
        self.inventory.action_done()
        self.assertEqual(self.inventory.state, 'done')
        self.inventory.action_validate()
        self.assertEqual(self.inventory.state, 'validated')

    def test_cancel_validated_raises(self):
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'Test',
            'expected_qty': 10,
            'actual_qty': 10,
        })
        self.inventory.action_start()
        self.inventory.action_done()
        self.inventory.action_validate()
        with self.assertRaises(UserError):
            self.inventory.action_cancel()

    def test_validate_creates_adjustment(self):
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'Test',
            'expected_qty': 100,
            'actual_qty': 90,
        })
        self.inventory.action_start()
        self.inventory.action_done()
        self.inventory.action_validate()
        self.assertTrue(self.inventory.adjustment_move_id)
        self.assertEqual(
            self.inventory.adjustment_move_id.state, 'confirmed'
        )

    def test_validate_requires_done_state(self):
        self.env['garment.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'item_type': 'product',
            'item_name': 'X',
            'expected_qty': 10,
            'actual_qty': 10,
        })
        self.inventory.action_start()
        with self.assertRaises(UserError):
            self.inventory.action_validate()

    def test_reset_draft(self):
        inv = self.env['garment.inventory'].create({
            'warehouse_type': 'material',
        })
        inv.write({'state': 'cancelled'})
        inv.action_reset_draft()
        self.assertEqual(inv.state, 'draft')


@tagged('post_install', '-at_install')
class TestInventoryScanWizard(TransactionCase):
    """Tests for QR scan wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inventory = cls.env['garment.inventory'].create({
            'warehouse_type': 'finished',
        })
        cls.inventory.write({'state': 'in_progress'})

    def test_scan_unknown_qr(self):
        wizard = self.env['garment.inventory.scan.wizard'].create({
            'inventory_id': self.inventory.id,
            'qr_content': 'UNKNOWN-QR-123',
            'actual_qty': 5,
        })
        wizard.action_scan()
        self.assertEqual(len(self.inventory.line_ids), 1)
        self.assertEqual(self.inventory.line_ids[0].item_code, 'UNKNOWN-QR-123')
        self.assertEqual(self.inventory.line_ids[0].actual_qty, 5)

    def test_scan_label_qr(self):
        label = self.env['garment.label'].create({
            'label_type': 'product',
            'quantity': 10,
        })
        wizard = self.env['garment.inventory.scan.wizard'].create({
            'inventory_id': self.inventory.id,
            'qr_content': label.code,
            'actual_qty': 10,
        })
        wizard.action_scan()
        self.assertEqual(len(self.inventory.line_ids), 1)
        self.assertEqual(self.inventory.line_ids[0].label_id, label)

    def test_scan_duplicate_increments(self):
        wizard1 = self.env['garment.inventory.scan.wizard'].create({
            'inventory_id': self.inventory.id,
            'qr_content': 'ITEM-001',
            'actual_qty': 5,
        })
        wizard1.action_scan()
        wizard2 = self.env['garment.inventory.scan.wizard'].create({
            'inventory_id': self.inventory.id,
            'qr_content': 'ITEM-001',
            'actual_qty': 3,
        })
        wizard2.action_scan()
        self.assertEqual(len(self.inventory.line_ids), 1)
        self.assertEqual(self.inventory.line_ids[0].actual_qty, 8)

    def test_scan_empty_raises(self):
        wizard = self.env['garment.inventory.scan.wizard'].create({
            'inventory_id': self.inventory.id,
            'qr_content': '   ',
            'actual_qty': 1,
        })
        with self.assertRaises(UserError):
            wizard.action_scan()
