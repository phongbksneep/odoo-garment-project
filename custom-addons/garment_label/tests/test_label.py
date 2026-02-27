from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestGarmentLabel(TransactionCase):
    """Tests for garment.label."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = cls.env['garment.style'].create({
            'name': 'Style Label Test',
            'code': 'ST-LBL-01',
            'category': 'shirt',
        })
        cls.buyer = cls.env['res.partner'].create({
            'name': 'Buyer Label Test',
            'customer_rank': 1,
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.buyer.id,
            'style_id': cls.style.id,
        })

    def _create_label(self, label_type='product', **kwargs):
        vals = {
            'label_type': label_type,
            'garment_order_id': self.order.id,
            'style_id': self.style.id,
            'quantity': 100,
        }
        vals.update(kwargs)
        return self.env['garment.label'].create(vals)

    def test_create_product_label(self):
        label = self._create_label('product')
        self.assertTrue(label.code.startswith('LP-'))
        self.assertEqual(label.state, 'draft')

    def test_create_carton_label(self):
        label = self._create_label('carton')
        self.assertTrue(label.code.startswith('LC-'))

    def test_create_pallet_label(self):
        label = self._create_label('pallet')
        self.assertTrue(label.code.startswith('LT-'))

    def test_qr_content(self):
        label = self._create_label('product')
        self.assertIn(label.code, label.qr_content)
        self.assertIn('product', label.qr_content)

    def test_print_label(self):
        label = self._create_label()
        label.action_print()
        self.assertEqual(label.state, 'printed')
        self.assertEqual(label.print_count, 1)
        self.assertTrue(label.last_print_date)

    def test_print_increments_count(self):
        label = self._create_label()
        label.action_print()
        label.action_print()
        self.assertEqual(label.print_count, 2)

    def test_apply_label(self):
        label = self._create_label()
        label.action_print()
        label.action_apply()
        self.assertEqual(label.state, 'applied')

    def test_cannot_apply_unprinted(self):
        label = self._create_label()
        with self.assertRaises(UserError):
            label.action_apply()

    def test_scan_label(self):
        label = self._create_label()
        label.action_print()
        label.action_scan()
        self.assertTrue(label.last_scan_date)

    def test_cancel_label(self):
        label = self._create_label()
        label.action_cancel()
        self.assertEqual(label.state, 'cancelled')

    def test_cannot_cancel_applied(self):
        label = self._create_label()
        label.action_print()
        label.action_apply()
        with self.assertRaises(UserError):
            label.action_cancel()


@tagged('post_install', '-at_install')
class TestGarmentPallet(TransactionCase):
    """Tests for garment.pallet."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = cls.env['garment.style'].create({
            'name': 'Style Pallet Test',
            'code': 'ST-PLT-01',
            'category': 'shirt',
        })
        cls.buyer = cls.env['res.partner'].create({
            'name': 'Buyer Pallet Test',
            'customer_rank': 1,
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.buyer.id,
            'style_id': cls.style.id,
        })

    def _create_pallet(self, **kwargs):
        vals = {
            'garment_order_id': self.order.id,
        }
        vals.update(kwargs)
        return self.env['garment.pallet'].create(vals)

    def _create_carton_box(self, pallet=None, **kwargs):
        vals = {
            'garment_order_id': self.order.id,
            'style_code': 'ST-PLT-01',
            'quantity': 50,
            'gross_weight': 10.0,
        }
        if pallet:
            vals['pallet_id'] = pallet.id
        vals.update(kwargs)
        return self.env['garment.carton.box'].create(vals)

    def test_create_pallet(self):
        pallet = self._create_pallet()
        self.assertTrue(pallet.name.startswith('PLT-'))
        self.assertEqual(pallet.state, 'draft')

    def test_pallet_totals(self):
        pallet = self._create_pallet()
        self._create_carton_box(pallet, quantity=50, gross_weight=10.0)
        self._create_carton_box(pallet, quantity=30, gross_weight=7.0)
        pallet.invalidate_recordset()
        self.assertEqual(pallet.carton_count, 2)
        self.assertEqual(pallet.total_pcs, 80)
        self.assertAlmostEqual(pallet.total_weight, 17.0)

    def test_pallet_close_requires_cartons(self):
        pallet = self._create_pallet()
        pallet.action_open()
        with self.assertRaises(UserError):
            pallet.action_close()

    def test_pallet_flow(self):
        pallet = self._create_pallet()
        pallet.action_open()
        self._create_carton_box(pallet)
        pallet.action_close()
        self.assertEqual(pallet.state, 'closed')
        pallet.action_ship()
        self.assertEqual(pallet.state, 'shipped')

    def test_cannot_ship_open_pallet(self):
        pallet = self._create_pallet()
        pallet.action_open()
        self._create_carton_box(pallet)
        with self.assertRaises(UserError):
            pallet.action_ship()

    def test_cannot_cancel_shipped(self):
        pallet = self._create_pallet()
        pallet.action_open()
        self._create_carton_box(pallet)
        pallet.action_close()
        pallet.action_ship()
        with self.assertRaises(UserError):
            pallet.action_cancel()

    def test_merge_pallets(self):
        p1 = self._create_pallet()
        p2 = self._create_pallet()
        self._create_carton_box(p1, quantity=50)
        self._create_carton_box(p2, quantity=30)
        (p1 | p2).action_merge_pallets()
        p1.invalidate_recordset()
        p2.invalidate_recordset()
        self.assertEqual(p1.carton_count, 2)
        self.assertEqual(p2.state, 'cancelled')

    def test_merge_requires_two(self):
        p1 = self._create_pallet()
        with self.assertRaises(UserError):
            p1.action_merge_pallets()

    def test_split_pallet(self):
        pallet = self._create_pallet()
        self._create_carton_box(pallet, quantity=50)
        self._create_carton_box(pallet, quantity=30)
        result = pallet.action_split_pallet()
        new_pallet = self.env['garment.pallet'].browse(result['res_id'])
        pallet.invalidate_recordset()
        self.assertEqual(pallet.carton_count, 1)
        self.assertEqual(new_pallet.carton_count, 1)

    def test_split_requires_two_cartons(self):
        pallet = self._create_pallet()
        self._create_carton_box(pallet)
        with self.assertRaises(UserError):
            pallet.action_split_pallet()


@tagged('post_install', '-at_install')
class TestCartonBox(TransactionCase):
    """Tests for garment.carton.box."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = cls.env['garment.style'].create({
            'name': 'Style Carton Test',
            'code': 'ST-CTN-01',
            'category': 'shirt',
        })
        cls.buyer = cls.env['res.partner'].create({
            'name': 'Buyer Carton Test',
            'customer_rank': 1,
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.buyer.id,
            'style_id': cls.style.id,
        })

    def _create_box(self, **kwargs):
        vals = {
            'garment_order_id': self.order.id,
            'style_code': 'ST-CTN-01',
            'color': 'Red',
            'size': 'M',
            'quantity': 100,
            'length_cm': 60,
            'width_cm': 40,
            'height_cm': 30,
            'gross_weight': 15.0,
            'net_weight': 12.0,
        }
        vals.update(kwargs)
        return self.env['garment.carton.box'].create(vals)

    def test_create_carton(self):
        box = self._create_box()
        self.assertTrue(box.name.startswith('CTN-'))
        self.assertEqual(box.state, 'draft')

    def test_cbm_computed(self):
        box = self._create_box()
        expected = 60 * 40 * 30 / 1_000_000
        self.assertAlmostEqual(box.cbm, expected, places=4)

    def test_pack_and_put_on_pallet(self):
        pallet = self.env['garment.pallet'].create({
            'garment_order_id': self.order.id,
        })
        box = self._create_box()
        box.action_pack()
        self.assertEqual(box.state, 'packed')
        box.write({'pallet_id': pallet.id})
        box.action_put_on_pallet()
        self.assertEqual(box.state, 'on_pallet')

    def test_put_on_pallet_requires_pallet(self):
        box = self._create_box()
        box.action_pack()
        with self.assertRaises(UserError):
            box.action_put_on_pallet()

    def test_put_on_pallet_requires_packed(self):
        pallet = self.env['garment.pallet'].create({
            'garment_order_id': self.order.id,
        })
        box = self._create_box(pallet_id=pallet.id)
        with self.assertRaises(UserError):
            box.action_put_on_pallet()

    def test_cannot_cancel_shipped(self):
        box = self._create_box()
        box.action_pack()
        box.action_ship()
        with self.assertRaises(UserError):
            box.action_cancel()

    def test_merge_cartons(self):
        b1 = self._create_box(quantity=60, gross_weight=10.0, net_weight=8.0)
        b2 = self._create_box(quantity=40, gross_weight=7.0, net_weight=5.0)
        (b1 | b2).action_merge_cartons()
        b1.invalidate_recordset()
        b2.invalidate_recordset()
        self.assertEqual(b1.quantity, 100)
        self.assertAlmostEqual(b1.gross_weight, 17.0)
        self.assertEqual(b2.state, 'cancelled')

    def test_merge_requires_two(self):
        b1 = self._create_box()
        with self.assertRaises(UserError):
            b1.action_merge_cartons()

    def test_split_carton(self):
        box = self._create_box(quantity=100, gross_weight=20.0, net_weight=16.0)
        result = box.action_split_carton()
        new_box = self.env['garment.carton.box'].browse(result['res_id'])
        self.assertEqual(box.quantity, 50)
        self.assertEqual(new_box.quantity, 50)
        self.assertAlmostEqual(box.gross_weight, 10.0)
        self.assertAlmostEqual(new_box.gross_weight, 10.0)

    def test_split_requires_min_two(self):
        box = self._create_box(quantity=1)
        with self.assertRaises(UserError):
            box.action_split_carton()

    def test_generate_label(self):
        box = self._create_box()
        result = box.action_generate_label()
        self.assertTrue(box.qr_label_id)
        self.assertEqual(box.qr_label_id.label_type, 'carton')
        self.assertEqual(result['res_model'], 'garment.label')

    def test_cannot_generate_label_twice(self):
        box = self._create_box()
        box.action_generate_label()
        with self.assertRaises(UserError):
            box.action_generate_label()
