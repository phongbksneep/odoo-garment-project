from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestGarmentInvoice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'KH Test ACC'})

    def test_create_sale_invoice(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': '10',
        })
        self.assertTrue(inv.name.startswith('INV-S-'))
        self.assertEqual(inv.state, 'draft')

    def test_create_purchase_invoice(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'purchase',
            'partner_id': self.partner.id,
            'tax_type': '10',
        })
        self.assertTrue(inv.name.startswith('INV-P-'))

    def test_totals_compute(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': '10',
        })
        self.env['garment.invoice.line'].create([
            {
                'invoice_id': inv.id,
                'description': 'T-Shirt FOB',
                'quantity': 1000,
                'unit_price': 5.5,
            },
            {
                'invoice_id': inv.id,
                'description': 'Polo Shirt FOB',
                'quantity': 500,
                'unit_price': 7.0,
            },
        ])
        self.assertEqual(inv.subtotal, 9000)  # 5500 + 3500
        self.assertEqual(inv.tax_amount, 900)  # 10%
        self.assertEqual(inv.total_amount, 9900)

    def test_export_zero_tax(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': '0',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Export goods',
            'quantity': 100,
            'unit_price': 10.0,
        })
        self.assertEqual(inv.tax_amount, 0)
        self.assertEqual(inv.total_amount, 1000)

    def test_confirm_requires_lines(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
        })
        with self.assertRaises(UserError):
            inv.action_confirm()

    def test_cannot_cancel_paid(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Test',
            'quantity': 1,
            'unit_price': 100,
        })
        inv.action_confirm()
        inv.action_paid()
        with self.assertRaises(UserError):
            inv.action_cancel()

    def test_payment_residual(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': 'none',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Goods',
            'quantity': 10,
            'unit_price': 1000,
        })
        inv.action_confirm()
        self.assertEqual(inv.total_amount, 10000)
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 6000,
            'payment_type': 'inbound',
        })
        pay.action_confirm()
        self.assertEqual(inv.paid_amount, 6000)
        self.assertEqual(inv.residual, 4000)
