from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestStockMoveCreate(TransactionCase):
    """Tests for garment.stock.move creation."""

    def test_create_stock_in(self):
        move = self.env['garment.stock.move'].create({
            'move_type': 'in',
            'warehouse_type': 'material',
            'reason': 'purchase',
        })
        self.assertTrue(move.name.startswith('NK-'))
        self.assertEqual(move.state, 'draft')

    def test_create_stock_out(self):
        move = self.env['garment.stock.move'].create({
            'move_type': 'out',
            'warehouse_type': 'finished',
            'reason': 'delivery',
        })
        self.assertTrue(move.name.startswith('XK-'))

    def test_create_stock_transfer(self):
        move = self.env['garment.stock.move'].create({
            'move_type': 'transfer',
            'warehouse_type': 'wip',
            'reason': 'production',
        })
        self.assertTrue(move.name.startswith('CK-'))


@tagged('post_install', '-at_install')
class TestStockMoveWorkflow(TransactionCase):
    """Tests for garment.stock.move workflow."""

    def setUp(self):
        super().setUp()
        self.move = self.env['garment.stock.move'].create({
            'move_type': 'in',
            'warehouse_type': 'material',
            'reason': 'purchase',
            'line_ids': [(0, 0, {
                'product_type': 'fabric',
                'description': 'Vải Cotton 100%',
                'unit': 'm',
                'quantity': 500,
                'unit_price': 80000,
            })],
        })

    def test_full_workflow(self):
        self.move.action_confirm()
        self.assertEqual(self.move.state, 'confirmed')
        self.move.action_done()
        self.assertEqual(self.move.state, 'done')

    def test_confirm_requires_lines(self):
        empty_move = self.env['garment.stock.move'].create({
            'move_type': 'in',
            'warehouse_type': 'material',
            'reason': 'purchase',
        })
        with self.assertRaises(UserError):
            empty_move.action_confirm()

    def test_cannot_cancel_done(self):
        self.move.action_confirm()
        self.move.action_done()
        with self.assertRaises(UserError):
            self.move.action_cancel()

    def test_reset_draft(self):
        self.move.action_confirm()
        self.move.action_reset_draft()
        self.assertEqual(self.move.state, 'draft')


@tagged('post_install', '-at_install')
class TestStockMoveTotals(TransactionCase):
    """Tests for stock move computed totals."""

    def test_totals_compute(self):
        move = self.env['garment.stock.move'].create({
            'move_type': 'in',
            'warehouse_type': 'material',
            'reason': 'purchase',
            'line_ids': [
                (0, 0, {
                    'product_type': 'fabric',
                    'description': 'Vải Cotton',
                    'unit': 'm',
                    'quantity': 100,
                    'unit_price': 50000,
                }),
                (0, 0, {
                    'product_type': 'thread',
                    'description': 'Chỉ May',
                    'unit': 'pcs',
                    'quantity': 50,
                    'unit_price': 20000,
                }),
            ],
        })
        self.assertEqual(move.total_qty, 150)
        self.assertEqual(move.total_value, 6000000)

    def test_line_value_compute(self):
        move = self.env['garment.stock.move'].create({
            'move_type': 'out',
            'warehouse_type': 'finished',
            'reason': 'delivery',
            'line_ids': [(0, 0, {
                'product_type': 'finished',
                'description': 'Áo Polo Size M',
                'unit': 'pcs',
                'quantity': 200,
                'unit_price': 150000,
            })],
        })
        line = move.line_ids[0]
        self.assertEqual(line.value, 30000000)
