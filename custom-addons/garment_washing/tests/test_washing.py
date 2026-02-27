from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestWashChemical(TransactionCase):
    """Tests for garment.wash.chemical."""

    def test_create_chemical(self):
        chem = self.env['garment.wash.chemical'].create({
            'name': 'Test Detergent',
            'code': 'TD-01',
            'chemical_type': 'detergent',
            'unit_price': 50000,
        })
        self.assertEqual(chem.chemical_type, 'detergent')

    def test_low_stock_compute(self):
        chem = self.env['garment.wash.chemical'].create({
            'name': 'Test Low Stock',
            'code': 'TLS-01',
            'chemical_type': 'softener',
            'stock_qty': 5,
            'min_stock': 10,
        })
        self.assertTrue(chem.is_low_stock)

    def test_not_low_stock(self):
        chem = self.env['garment.wash.chemical'].create({
            'name': 'Test OK Stock',
            'code': 'TOK-01',
            'chemical_type': 'enzyme',
            'stock_qty': 50,
            'min_stock': 10,
        })
        self.assertFalse(chem.is_low_stock)


@tagged('post_install', '-at_install')
class TestWashRecipe(TransactionCase):
    """Tests for garment.wash.recipe and recipe steps."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.chemical = cls.env['garment.wash.chemical'].create({
            'name': 'Test Chemical',
            'code': 'TC-01',
            'chemical_type': 'detergent',
            'unit_price': 40000,  # 40,000 VND/kg
        })

    def _create_recipe(self, **kwargs):
        vals = {
            'name': 'Test Recipe',
            'code': 'TR-001',
            'wash_type': 'normal',
            'temperature': 40,
            'duration_minutes': 30,
        }
        vals.update(kwargs)
        return self.env['garment.wash.recipe'].create(vals)

    def test_create_recipe(self):
        recipe = self._create_recipe()
        self.assertEqual(recipe.wash_type, 'normal')

    def test_total_time_compute(self):
        recipe = self._create_recipe()
        self.env['garment.wash.recipe.step'].create([
            {
                'recipe_id': recipe.id,
                'name': 'Step 1',
                'step_type': 'pre_wash',
                'duration_minutes': 5,
            },
            {
                'recipe_id': recipe.id,
                'name': 'Step 2',
                'step_type': 'main_wash',
                'duration_minutes': 15,
            },
            {
                'recipe_id': recipe.id,
                'name': 'Step 3',
                'step_type': 'rinse',
                'duration_minutes': 5,
            },
        ])
        recipe.invalidate_recordset()
        self.assertEqual(recipe.total_time, 25)

    def test_chemical_cost_compute(self):
        recipe = self._create_recipe()
        self.env['garment.wash.recipe.step'].create({
            'recipe_id': recipe.id,
            'name': 'Main Wash',
            'step_type': 'main_wash',
            'chemical_id': self.chemical.id,
            'chemical_dosage': 5.0,  # 5 g/kg
            'duration_minutes': 15,
        })
        recipe.invalidate_recordset()
        # cost = (5 / 1000) * 40000 = 200 VND per kg
        self.assertAlmostEqual(recipe.total_chemical_cost, 200.0, places=2)

    def test_code_unique_constraint(self):
        self._create_recipe(code='UNIQUE-001')
        with self.assertRaises(Exception):
            self._create_recipe(code='UNIQUE-001')


@tagged('post_install', '-at_install')
class TestWashOrder(TransactionCase):
    """Tests for garment.wash.order."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = cls.env['res.partner'].create({
            'name': 'Wash Client Co.',
            'customer_rank': 1,
        })
        cls.chemical = cls.env['garment.wash.chemical'].create({
            'name': 'Det X',
            'code': 'DX-01',
            'chemical_type': 'detergent',
            'unit_price': 30000,
        })
        cls.recipe = cls.env['garment.wash.recipe'].create({
            'name': 'Test Wash Recipe',
            'code': 'TWR-001',
            'wash_type': 'normal',
        })

    def _create_order(self, **kwargs):
        vals = {
            'order_type': 'internal',
            'recipe_id': self.recipe.id,
            'qty_received': 500,
        }
        vals.update(kwargs)
        return self.env['garment.wash.order'].create(vals)

    def test_sequence_generation(self):
        order = self._create_order()
        self.assertTrue(order.name.startswith('WASH-'))

    def test_total_cost_compute(self):
        order = self._create_order(unit_price=2000, qty_received=100)
        self.assertEqual(order.total_cost, 200000)

    def test_confirm_external_requires_client(self):
        order = self._create_order(order_type='external_in')
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_confirm_requires_recipe(self):
        order = self._create_order(recipe_id=False)
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_full_workflow_internal(self):
        """E2E: draft → confirmed → washing → qc → done → delivered."""
        order = self._create_order()
        self.assertEqual(order.state, 'draft')

        order.action_confirm()
        self.assertEqual(order.state, 'confirmed')

        order.action_start_washing()
        self.assertEqual(order.state, 'washing')
        self.assertTrue(order.date_start)

        order.qty_washed = 490
        order.action_qc()
        self.assertEqual(order.state, 'qc')
        self.assertTrue(order.date_end)

        order.action_done()
        self.assertEqual(order.state, 'done')

        order.action_delivered()
        self.assertEqual(order.state, 'delivered')
        self.assertTrue(order.date_delivered)

    def test_full_workflow_external(self):
        """E2E: External wash order from draft to delivered."""
        order = self._create_order(
            order_type='external_in',
            client_id=self.client.id,
            client_po='EXT-PO-001',
            unit_price=3000,
        )
        order.action_confirm()
        order.action_start_washing()
        order.qty_washed = 500
        order.action_qc()
        order.action_done()
        order.action_delivered()
        self.assertEqual(order.state, 'delivered')
        self.assertEqual(order.total_cost, 1500000)  # 500 × 3000

    def test_cannot_cancel_delivered(self):
        order = self._create_order()
        order.action_confirm()
        order.action_start_washing()
        order.qty_washed = 500
        order.action_qc()
        order.action_done()
        order.action_delivered()
        with self.assertRaises(UserError):
            order.action_cancel()

    def test_qty_validation(self):
        order = self._create_order(qty_received=100)
        with self.assertRaises(ValidationError):
            order.qty_washed = 150

    def test_qc_requires_qty_washed(self):
        order = self._create_order()
        order.action_confirm()
        order.action_start_washing()
        with self.assertRaises(UserError):
            order.action_qc()

    def test_wash_pass_rate(self):
        order = self._create_order(qty_received=200)
        order.qty_washed = 190
        self.assertAlmostEqual(order.wash_pass_rate, 95.0, places=1)

    def test_rewash_rate(self):
        order = self._create_order(qty_received=200)
        order.qty_rewash = 10
        self.assertAlmostEqual(order.rewash_rate, 5.0, places=1)
