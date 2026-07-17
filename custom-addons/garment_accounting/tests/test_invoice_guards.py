from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestInvoiceGuards(TransactionCase):
    """Guard trạng thái hóa đơn: không trả 2 lần, không reset/xóa khi đã trả."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'KH Guard ACC'})

    def _create_invoice(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': '10',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Item Guard',
            'quantity': 10,
            'unit_price': 100,
        })
        return inv

    def test_cannot_confirm_twice(self):
        inv = self._create_invoice()
        inv.action_confirm()
        with self.assertRaises(UserError):
            inv.action_confirm()

    def test_cannot_pay_draft(self):
        inv = self._create_invoice()
        with self.assertRaises(UserError):
            inv.action_paid()

    def test_cannot_pay_twice(self):
        inv = self._create_invoice()
        inv.action_confirm()
        inv.action_paid()
        with self.assertRaises(UserError):
            inv.action_paid()

    def test_cannot_reset_paid(self):
        inv = self._create_invoice()
        inv.action_confirm()
        inv.action_paid()
        with self.assertRaises(UserError):
            inv.action_reset_draft()

    def test_reset_confirmed_ok(self):
        inv = self._create_invoice()
        inv.action_confirm()
        inv.action_reset_draft()
        self.assertEqual(inv.state, 'draft')

    def test_cannot_delete_confirmed(self):
        inv = self._create_invoice()
        inv.action_confirm()
        with self.assertRaises(UserError):
            inv.unlink()

    def test_cannot_delete_paid(self):
        inv = self._create_invoice()
        inv.action_confirm()
        inv.action_paid()
        with self.assertRaises(UserError):
            inv.unlink()

    def test_delete_draft_ok(self):
        inv = self._create_invoice()
        inv.unlink()
        self.assertFalse(inv.exists())
