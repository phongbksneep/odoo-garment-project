from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestBarcodeScannerRPC(TransactionCase):
    """Tests for the process_barcode_scan RPC method used by the camera scanner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inventory = cls.env['garment.inventory'].create({
            'warehouse_type': 'finished',
        })
        # Start inventory to allow scanning
        cls.env['garment.inventory.line'].create({
            'inventory_id': cls.inventory.id,
            'item_type': 'product',
            'item_name': 'Placeholder',
            'expected_qty': 0,
            'actual_qty': 0,
        })
        cls.inventory.action_start()

    def test_01_scan_unknown_barcode(self):
        """Scanning an unknown barcode creates a new line."""
        result = self.inventory.process_barcode_scan('BARCODE-UNKNOWN-001', 5)
        self.assertTrue(result['success'])
        self.assertTrue(result['is_new'])
        self.assertEqual(result['item_name'], 'BARCODE-UNKNOWN-001')
        self.assertEqual(result['total_qty'], 5)

    def test_02_scan_duplicate_increments(self):
        """Scanning the same barcode twice increments qty."""
        self.inventory.process_barcode_scan('ITEM-DUP-001', 3)
        result = self.inventory.process_barcode_scan('ITEM-DUP-001', 2)
        self.assertTrue(result['success'])
        self.assertFalse(result['is_new'])
        self.assertEqual(result['total_qty'], 5)

    def test_03_scan_empty_barcode(self):
        """Empty barcode returns error."""
        result = self.inventory.process_barcode_scan('', 1)
        self.assertFalse(result['success'])

    def test_04_scan_whitespace_barcode(self):
        """Whitespace-only barcode returns error."""
        result = self.inventory.process_barcode_scan('   ', 1)
        self.assertFalse(result['success'])

    def test_05_scan_label_barcode(self):
        """Scanning a label code links the label."""
        label = self.env['garment.label'].create({
            'label_type': 'product',
            'quantity': 10,
        })
        result = self.inventory.process_barcode_scan(label.code, 10)
        self.assertTrue(result['success'])
        self.assertTrue(result['is_new'])
        # Check line was created with label reference
        line = self.inventory.line_ids.filtered(
            lambda l: l.label_id == label
        )
        self.assertEqual(len(line), 1)
        self.assertEqual(line.actual_qty, 10)

    def test_06_scan_label_duplicate_increments(self):
        """Scanning same label barcode twice increments qty."""
        label = self.env['garment.label'].create({
            'label_type': 'carton',
            'quantity': 50,
        })
        self.inventory.process_barcode_scan(label.code, 5)
        result = self.inventory.process_barcode_scan(label.code, 3)
        self.assertFalse(result['is_new'])
        self.assertEqual(result['total_qty'], 8)

    def test_07_multiple_different_barcodes(self):
        """Multiple unique barcodes create separate lines."""
        initial_count = len(self.inventory.line_ids)
        self.inventory.process_barcode_scan('CODE-A', 1)
        self.inventory.process_barcode_scan('CODE-B', 2)
        self.inventory.process_barcode_scan('CODE-C', 3)
        new_lines = len(self.inventory.line_ids) - initial_count
        self.assertEqual(new_lines, 3)

    def test_08_scan_default_qty(self):
        """Default qty is 1 when not specified."""
        result = self.inventory.process_barcode_scan('SINGLE-SCAN')
        self.assertTrue(result['success'])
        self.assertEqual(result['total_qty'], 1)

    def test_09_action_open_camera_scanner(self):
        """Camera scanner action returns correct client action."""
        result = self.inventory.action_open_camera_scanner()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'garment_barcode_scanner')
        self.assertEqual(
            result['params']['inventory_id'], self.inventory.id
        )
        self.assertEqual(
            result['params']['inventory_name'], self.inventory.name
        )

    def test_10_action_scan_qr_still_works(self):
        """Original QR scan wizard action still works."""
        result = self.inventory.action_scan_qr()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'garment.inventory.scan.wizard')

    def test_11_label_with_style_info(self):
        """Scanning label with style populates item_name from style."""
        style = self.env['garment.style'].create({
            'name': 'Áo Polo Test Scanner',
            'code': 'ST-SCAN-01',
            'category': 'shirt',
        })
        label = self.env['garment.label'].create({
            'label_type': 'product',
            'style_id': style.id,
            'quantity': 20,
        })
        result = self.inventory.process_barcode_scan(label.code, 20)
        self.assertTrue(result['success'])
        self.assertEqual(result['item_name'], 'Áo Polo Test Scanner')
        line = self.inventory.line_ids.filtered(
            lambda l: l.item_code == label.code
        )
        self.assertEqual(line.style_code, 'ST-SCAN-01')

    def test_12_carton_label_type(self):
        """Carton label sets item_type to 'carton'."""
        label = self.env['garment.label'].create({
            'label_type': 'carton',
            'quantity': 100,
        })
        self.inventory.process_barcode_scan(label.code, 1)
        line = self.inventory.line_ids.filtered(
            lambda l: l.item_code == label.code
        )
        self.assertEqual(line.item_type, 'carton')
