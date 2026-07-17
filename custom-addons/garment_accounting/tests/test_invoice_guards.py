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


class TestIntegrationGates(TransactionCase):
    """Gate tích hợp: không tạo SO từ đơn nháp; khóa dòng hóa đơn."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'KH Gate ACC', 'customer_rank': 1})
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-GATE-001', 'code': 'ST-GATE-001',
            'category': 'shirt'})

    def test_cannot_create_so_from_draft_order(self):
        order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
        })
        with self.assertRaises(UserError):
            order.action_create_sale_order()

    def test_invoice_lines_locked_after_confirm(self):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': '10',
        })
        line = self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Item Gate',
            'quantity': 10,
            'unit_price': 100,
        })
        inv.action_confirm()
        with self.assertRaises(UserError):
            line.write({'quantity': 999})
        with self.assertRaises(UserError):
            line.unlink()
        with self.assertRaises(UserError):
            self.env['garment.invoice.line'].create({
                'invoice_id': inv.id,
                'description': 'Item Gate 2',
                'quantity': 1,
                'unit_price': 100,
            })
        # Về nháp thì sửa được
        inv.action_reset_draft()
        line.write({'quantity': 20})
        self.assertEqual(line.quantity, 20)
