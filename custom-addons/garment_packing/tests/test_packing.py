from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestPackingList(TransactionCase):
    """Unit tests and E2E tests for garment.packing.list."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Packing',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-PKL-001',
            'code': 'ST-PKL-001',
            'category': 'shirt',
        })

    def _create_packing_list(self, **kwargs):
        vals = {
            'buyer_id': self.partner.id,
            'style_id': self.style.id,
            'ship_mode': 'sea',
            'packing_type': 'ratio',
        }
        vals.update(kwargs)
        return self.env['garment.packing.list'].create(vals)

    def _add_cartons(self, packing_list, count=1):
        """Helper to add carton lines."""
        size = self.env['garment.size'].search([], limit=1)
        color = self.env['garment.color'].search([], limit=1)
        cartons = []
        start = 1
        for i in range(count):
            carton = self.env['garment.carton.line'].create({
                'packing_list_id': packing_list.id,
                'carton_from': start,
                'carton_to': start + 9,
                'size_id': size.id if size else False,
                'color_id': color.id if color else False,
                'pcs_per_carton': 20,
                'length_cm': 60,
                'width_cm': 40,
                'height_cm': 30,
                'gross_weight': 12.5,
                'net_weight': 11.0,
            })
            cartons.append(carton)
            start += 10
        return cartons

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_sequence(self):
        pl = self._create_packing_list()
        self.assertTrue(pl.name.startswith('PKL/'))

    def test_carton_count_compute(self):
        """Test carton_count = carton_to - carton_from + 1."""
        pl = self._create_packing_list()
        carton = self.env['garment.carton.line'].create({
            'packing_list_id': pl.id,
            'carton_from': 1,
            'carton_to': 10,
            'pcs_per_carton': 20,
        })
        self.assertEqual(carton.carton_count, 10)

    def test_total_pcs_compute(self):
        """total_pcs = carton_count × pcs_per_carton."""
        pl = self._create_packing_list()
        carton = self.env['garment.carton.line'].create({
            'packing_list_id': pl.id,
            'carton_from': 1,
            'carton_to': 5,
            'pcs_per_carton': 20,
        })
        self.assertEqual(carton.total_pcs, 100)

    def test_cbm_compute(self):
        """CBM = L × W × H / 1,000,000."""
        pl = self._create_packing_list()
        carton = self.env['garment.carton.line'].create({
            'packing_list_id': pl.id,
            'carton_from': 1,
            'carton_to': 1,
            'pcs_per_carton': 20,
            'length_cm': 60,
            'width_cm': 40,
            'height_cm': 30,
        })
        expected_cbm = 60 * 40 * 30 / 1_000_000  # 0.072
        self.assertAlmostEqual(carton.cbm_per_carton, expected_cbm, places=4)

    def test_totals_compute(self):
        """Test packing list totals from carton lines."""
        pl = self._create_packing_list()
        self._add_cartons(pl, count=3)
        pl.invalidate_recordset()
        self.assertEqual(pl.total_cartons, 30)  # 3 × 10
        self.assertEqual(pl.total_pieces, 600)  # 30 × 20

    def test_cannot_pack_without_cartons(self):
        pl = self._create_packing_list()
        pl.action_start_packing()
        with self.assertRaises(UserError):
            pl.action_packed()

    def test_cannot_cancel_shipped(self):
        pl = self._create_packing_list()
        pl.action_start_packing()
        self._add_cartons(pl)
        pl.action_packed()
        pl.action_shipped()
        with self.assertRaises(UserError):
            pl.action_cancel()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_packing_workflow(self):
        """E2E: Create → packing → add cartons → packed → shipped → delivered."""
        # Step 1: Create
        pl = self._create_packing_list(
            po_number='PO-2024-001',
            destination_port='Ho Chi Minh',
        )
        self.assertEqual(pl.state, 'draft')

        # Step 2: Start packing
        pl.action_start_packing()
        self.assertEqual(pl.state, 'packing')

        # Step 3: Add cartons
        self._add_cartons(pl, count=5)
        pl.invalidate_recordset()
        self.assertEqual(pl.total_cartons, 50)
        self.assertEqual(pl.total_pieces, 1000)
        self.assertGreater(pl.total_cbm, 0)
        self.assertGreater(pl.total_gross_weight, 0)

        # Step 4: Packed
        pl.action_packed()
        self.assertEqual(pl.state, 'packed')

        # Step 5: Shipped
        pl.action_shipped()
        self.assertEqual(pl.state, 'shipped')

        # Step 6: Delivered
        pl.action_delivered()
        self.assertEqual(pl.state, 'delivered')
