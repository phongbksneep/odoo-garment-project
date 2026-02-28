from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestOdooIntegration(TransactionCase):
    """Tests for Odoo Sale/Purchase/Account integration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Integration Test Customer',
            'customer_rank': 1,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Integration Test Supplier',
            'supplier_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Integration Style',
            'code': 'INT-001',
            'category': 'shirt',
        })

    # -------------------------------------------------------------------------
    # Sale Order Integration
    # -------------------------------------------------------------------------
    def test_garment_order_has_sale_order_field(self):
        """garment.order should have sale_order_id field after integration."""
        order = self.env['garment.order'].create({
            'customer_id': self.customer.id,
            'style_id': self.style.id,
            'unit_price': 5.0,
        })
        self.assertFalse(order.sale_order_id)

    def test_create_sale_order_from_garment_order(self):
        """Create a sale.order from garment.order."""
        order = self.env['garment.order'].create({
            'customer_id': self.customer.id,
            'style_id': self.style.id,
            'unit_price': 8.50,
        })
        result = order.action_create_sale_order()
        self.assertTrue(order.sale_order_id)
        self.assertEqual(order.sale_order_id.partner_id, self.customer)
        self.assertEqual(result['res_model'], 'sale.order')

    def test_cannot_create_duplicate_sale_order(self):
        """Cannot create SO twice for same garment order."""
        order = self.env['garment.order'].create({
            'customer_id': self.customer.id,
            'style_id': self.style.id,
            'unit_price': 5.0,
        })
        order.action_create_sale_order()
        with self.assertRaises(UserError):
            order.action_create_sale_order()

    def test_view_sale_order(self):
        """View linked sale order."""
        order = self.env['garment.order'].create({
            'customer_id': self.customer.id,
            'style_id': self.style.id,
            'unit_price': 5.0,
        })
        order.action_create_sale_order()
        result = order.action_view_sale_order()
        self.assertEqual(result['res_id'], order.sale_order_id.id)

    def test_view_sale_order_without_link_raises(self):
        """Error when viewing non-existent SO."""
        order = self.env['garment.order'].create({
            'customer_id': self.customer.id,
            'style_id': self.style.id,
        })
        with self.assertRaises(UserError):
            order.action_view_sale_order()

    # -------------------------------------------------------------------------
    # Account Move Integration
    # -------------------------------------------------------------------------
    def test_invoice_has_account_move_field(self):
        """garment.invoice should have account_move_id."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
            'tax_type': '10',
        })
        self.assertFalse(inv.account_move_id)

    def test_create_account_move_from_invoice(self):
        """Create account.move from confirmed garment.invoice."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
            'tax_type': '10',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'FOB Shirts',
            'quantity': 1000,
            'unit_price': 5.5,
        })
        inv.action_confirm()

        result = inv.action_create_account_move()
        self.assertTrue(inv.account_move_id)
        self.assertEqual(inv.account_move_id.move_type, 'out_invoice')
        self.assertEqual(result['res_model'], 'account.move')

    def test_create_account_move_purchase(self):
        """Create account.move (bill) from purchase invoice."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'purchase',
            'partner_id': self.supplier.id,
            'tax_type': '10',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Fabric Purchase',
            'quantity': 500,
            'unit_price': 50000,
        })
        inv.action_confirm()
        inv.action_create_account_move()
        self.assertEqual(inv.account_move_id.move_type, 'in_invoice')

    def test_cannot_create_account_move_draft(self):
        """Cannot create account move from draft invoice."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Test',
            'quantity': 1,
            'unit_price': 100,
        })
        with self.assertRaises(UserError):
            inv.action_create_account_move()

    def test_cannot_create_duplicate_account_move(self):
        """Cannot create account move twice."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Test',
            'quantity': 1,
            'unit_price': 100,
        })
        inv.action_confirm()
        inv.action_create_account_move()
        with self.assertRaises(UserError):
            inv.action_create_account_move()

    def test_view_account_move(self):
        """View linked account move."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Test',
            'quantity': 1,
            'unit_price': 100,
        })
        inv.action_confirm()
        inv.action_create_account_move()
        result = inv.action_view_account_move()
        self.assertEqual(result['res_id'], inv.account_move_id.id)

    # -------------------------------------------------------------------------
    # Purchase Order Integration
    # -------------------------------------------------------------------------
    def test_material_receipt_has_po_field(self):
        """garment.material.receipt should have purchase_order_id."""
        receipt = self.env['garment.material.receipt'].create({
            'receipt_type': 'purchase',
            'supplier_id': self.supplier.id,
        })
        self.assertFalse(receipt.purchase_order_id)

    def test_create_purchase_order_from_receipt(self):
        """Create purchase.order from material receipt."""
        receipt = self.env['garment.material.receipt'].create({
            'receipt_type': 'purchase',
            'supplier_id': self.supplier.id,
        })
        self.env['garment.material.receipt.line'].create({
            'receipt_id': receipt.id,
            'material_type': 'fabric',
            'description': 'Cotton Fabric TC-200',
            'unit': 'm',
            'quantity': 5000,
            'unit_price': 55000,
        })
        result = receipt.action_create_purchase_order()
        self.assertTrue(receipt.purchase_order_id)
        self.assertEqual(receipt.purchase_order_id.partner_id, self.supplier)
        self.assertEqual(result['res_model'], 'purchase.order')

    def test_cannot_create_po_without_supplier(self):
        """Cannot create PO without supplier."""
        receipt = self.env['garment.material.receipt'].create({
            'receipt_type': 'buyer_supplied',
            'buyer_id': self.customer.id,
        })
        self.env['garment.material.receipt.line'].create({
            'receipt_id': receipt.id,
            'material_type': 'fabric',
            'description': 'Test',
            'unit': 'm',
            'quantity': 100,
        })
        with self.assertRaises(UserError):
            receipt.action_create_purchase_order()

    def test_cannot_create_duplicate_po(self):
        """Cannot create PO twice."""
        receipt = self.env['garment.material.receipt'].create({
            'receipt_type': 'purchase',
            'supplier_id': self.supplier.id,
        })
        self.env['garment.material.receipt.line'].create({
            'receipt_id': receipt.id,
            'material_type': 'fabric',
            'description': 'Test Fabric',
            'unit': 'm',
            'quantity': 100,
            'unit_price': 50000,
        })
        receipt.action_create_purchase_order()
        with self.assertRaises(UserError):
            receipt.action_create_purchase_order()

    def test_view_purchase_order(self):
        """View linked purchase order."""
        receipt = self.env['garment.material.receipt'].create({
            'receipt_type': 'purchase',
            'supplier_id': self.supplier.id,
        })
        self.env['garment.material.receipt.line'].create({
            'receipt_id': receipt.id,
            'material_type': 'fabric',
            'description': 'Fabric',
            'unit': 'm',
            'quantity': 100,
            'unit_price': 50000,
        })
        receipt.action_create_purchase_order()
        result = receipt.action_view_purchase_order()
        self.assertEqual(result['res_id'], receipt.purchase_order_id.id)

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_integration_flow(self):
        """E2E: Garment Order → SO, Invoice → Account Move, Receipt → PO."""
        # 1. Create garment order and link to SO
        order = self.env['garment.order'].create({
            'customer_id': self.customer.id,
            'style_id': self.style.id,
            'unit_price': 10.0,
        })
        order.action_create_sale_order()
        self.assertTrue(order.sale_order_id)
        so = order.sale_order_id
        self.assertEqual(so.partner_id, self.customer)

        # 2. Create garment invoice and link to account move
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
            'garment_order_id': order.id,
            'tax_type': '0',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Export FOB',
            'quantity': order.total_qty or 100,
            'unit_price': 10.0,
        })
        inv.action_confirm()
        inv.action_create_account_move()
        self.assertTrue(inv.account_move_id)
        self.assertEqual(inv.account_move_id.move_type, 'out_invoice')

        # 3. Create material receipt and link to PO
        receipt = self.env['garment.material.receipt'].create({
            'receipt_type': 'purchase',
            'supplier_id': self.supplier.id,
            'garment_order_id': order.id,
        })
        self.env['garment.material.receipt.line'].create({
            'receipt_id': receipt.id,
            'material_type': 'fabric',
            'description': 'Main Fabric',
            'unit': 'm',
            'quantity': 2000,
            'unit_price': 55000,
        })
        receipt.action_create_purchase_order()
        self.assertTrue(receipt.purchase_order_id)
        po = receipt.purchase_order_id
        self.assertEqual(po.partner_id, self.supplier)

    # -------------------------------------------------------------------------
    # Payment → Account Payment Integration
    # -------------------------------------------------------------------------
    def test_payment_has_account_payment_field(self):
        """garment.payment should have account_payment_id."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer.id,
            'amount': 1000000,
        })
        self.assertFalse(payment.account_payment_id)

    def test_create_account_payment_inbound(self):
        """Create account.payment (inbound) from garment payment."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer.id,
            'amount': 5000000,
        })
        payment.action_confirm()
        result = payment.action_create_account_payment()
        self.assertTrue(payment.account_payment_id)
        self.assertEqual(payment.account_payment_id.payment_type, 'inbound')
        self.assertEqual(payment.account_payment_id.partner_id, self.customer)
        self.assertEqual(result['res_model'], 'account.payment')

    def test_create_account_payment_outbound(self):
        """Create account.payment (outbound) from garment payment."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.supplier.id,
            'amount': 3000000,
        })
        payment.action_confirm()
        result = payment.action_create_account_payment()
        self.assertTrue(payment.account_payment_id)
        self.assertEqual(payment.account_payment_id.payment_type, 'outbound')

    def test_cannot_create_account_payment_draft(self):
        """Cannot create account payment from draft garment payment."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer.id,
            'amount': 1000000,
        })
        with self.assertRaises(UserError):
            payment.action_create_account_payment()

    def test_cannot_create_duplicate_account_payment(self):
        """Cannot create account payment twice."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer.id,
            'amount': 1000000,
        })
        payment.action_confirm()
        payment.action_create_account_payment()
        with self.assertRaises(UserError):
            payment.action_create_account_payment()

    def test_view_account_payment(self):
        """View linked account payment."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer.id,
            'amount': 1000000,
        })
        payment.action_confirm()
        payment.action_create_account_payment()
        result = payment.action_view_account_payment()
        self.assertEqual(result['res_id'], payment.account_payment_id.id)

    def test_view_account_payment_without_link_raises(self):
        """Error when viewing non-existent account payment."""
        payment = self.env['garment.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer.id,
            'amount': 1000000,
        })
        with self.assertRaises(UserError):
            payment.action_view_account_payment()

    # -------------------------------------------------------------------------
    # Tax Mapping Test
    # -------------------------------------------------------------------------
    def test_account_move_with_tax_mapping(self):
        """Account move lines should include matching tax if available."""
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.customer.id,
            'tax_type': '10',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Product with 10% VAT',
            'quantity': 100,
            'unit_price': 50000,
        })
        inv.action_confirm()

        # Create a 10% sale tax for testing
        tax_10 = self.env['account.tax'].create({
            'name': 'GTGT 10%',
            'amount': 10,
            'type_tax_use': 'sale',
        })

        inv.action_create_account_move()
        move = inv.account_move_id
        invoice_lines = move.invoice_line_ids
        self.assertTrue(invoice_lines)
        # Tax should be mapped
        for line in invoice_lines:
            self.assertIn(tax_10, line.tax_ids)
