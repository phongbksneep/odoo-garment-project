from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestGarmentInvoice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'KH Test ACC'})

    def _create_invoice(self, **kwargs):
        vals = {
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': '10',
        }
        vals.update(kwargs)
        return self.env['garment.invoice'].create(vals)

    def _add_line(self, inv, desc='Test Item', qty=1, price=100):
        return self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': desc,
            'quantity': qty,
            'unit_price': price,
        })

    def test_create_sale_invoice(self):
        inv = self._create_invoice()
        self.assertTrue(inv.name.startswith('INV-S-'))
        self.assertEqual(inv.state, 'draft')

    def test_create_purchase_invoice(self):
        inv = self._create_invoice(invoice_type='purchase')
        self.assertTrue(inv.name.startswith('INV-P-'))

    def test_totals_compute(self):
        inv = self._create_invoice()
        self._add_line(inv, 'T-Shirt FOB', 1000, 5.5)
        self._add_line(inv, 'Polo Shirt FOB', 500, 7.0)
        self.assertEqual(inv.subtotal, 9000)  # 5500 + 3500
        self.assertEqual(inv.tax_amount, 900)  # 10%
        self.assertEqual(inv.total_amount, 9900)

    def test_export_zero_tax(self):
        inv = self._create_invoice(tax_type='0')
        self._add_line(inv, 'Export goods', 100, 10.0)
        self.assertEqual(inv.tax_amount, 0)
        self.assertEqual(inv.total_amount, 1000)

    def test_confirm_requires_lines(self):
        inv = self._create_invoice()
        with self.assertRaises(UserError):
            inv.action_confirm()

    def test_cannot_cancel_paid(self):
        inv = self._create_invoice()
        self._add_line(inv)
        inv.action_confirm()
        inv.action_paid()
        with self.assertRaises(UserError):
            inv.action_cancel()

    def test_payment_residual(self):
        inv = self._create_invoice(tax_type='none')
        self._add_line(inv, 'Goods', 10, 1000)
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

    # --- New tests for Vietnamese compliance improvements ---

    def test_tax_5_percent(self):
        """Test VAT 5% (nội địa - hàng thiết yếu)."""
        inv = self._create_invoice(tax_type='5')
        self._add_line(inv, 'Hàng nội địa', 100, 200)
        self.assertEqual(inv.subtotal, 20000)
        self.assertEqual(inv.tax_amount, 1000)
        self.assertEqual(inv.total_amount, 21000)

    def test_tax_8_percent(self):
        """Test VAT 8% (thuế suất giảm theo NQ)."""
        inv = self._create_invoice(tax_type='8')
        self._add_line(inv, 'Hàng giảm thuế', 50, 100)
        self.assertEqual(inv.tax_amount, 400)

    def test_due_date_before_date_rejected(self):
        """Hạn TT không được trước ngày HĐ."""
        with self.assertRaises(ValidationError):
            self._create_invoice(
                date=date.today(),
                due_date=date.today() - timedelta(days=10),
            )

    def test_due_date_same_as_date_ok(self):
        """Hạn TT = ngày HĐ (thanh toán ngay) là hợp lệ."""
        today = date.today()
        inv = self._create_invoice(date=today, due_date=today)
        self.assertEqual(inv.due_date, today)

    def test_is_overdue_confirmed_past_due(self):
        """HĐ xác nhận quá hạn phải được đánh dấu."""
        inv = self._create_invoice(
            tax_type='none',
            date=date.today() - timedelta(days=10),
            due_date=date.today() - timedelta(days=5),
        )
        self._add_line(inv, 'Test', 1, 1000)
        inv.action_confirm()
        self.assertTrue(inv.is_overdue)
        self.assertEqual(inv.overdue_days, 5)

    def test_not_overdue_when_paid(self):
        """HĐ đã thanh toán đủ không tính quá hạn."""
        inv = self._create_invoice(
            tax_type='none',
            date=date.today() - timedelta(days=10),
            due_date=date.today() - timedelta(days=5),
        )
        self._add_line(inv, 'Test', 1, 1000)
        inv.action_confirm()
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 1000,
            'payment_type': 'inbound',
        })
        pay.action_confirm()
        # residual is 0, so not overdue
        self.assertFalse(inv.is_overdue)

    def test_not_overdue_draft(self):
        """HĐ nháp không tính quá hạn."""
        inv = self._create_invoice(
            date=date.today() - timedelta(days=10),
            due_date=date.today() - timedelta(days=5),
        )
        self.assertFalse(inv.is_overdue)

    def test_payment_status_not_paid(self):
        """Mới tạo -> chưa thanh toán."""
        inv = self._create_invoice(tax_type='none')
        self._add_line(inv, 'Test', 1, 1000)
        self.assertEqual(inv.payment_status, 'not_paid')

    def test_payment_status_partial(self):
        """TT một phần."""
        inv = self._create_invoice(tax_type='none')
        self._add_line(inv, 'Test', 1, 1000)
        inv.action_confirm()
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 500,
            'payment_type': 'inbound',
        })
        pay.action_confirm()
        self.assertEqual(inv.payment_status, 'partial')

    def test_payment_status_paid(self):
        """TT đủ."""
        inv = self._create_invoice(tax_type='none')
        self._add_line(inv, 'Test', 1, 1000)
        inv.action_confirm()
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 1000,
            'payment_type': 'inbound',
        })
        pay.action_confirm()
        self.assertEqual(inv.payment_status, 'paid')

    def test_line_quantity_must_be_positive(self):
        """Số lượng dòng HĐ phải > 0."""
        inv = self._create_invoice()
        with self.assertRaises(ValidationError):
            self._add_line(inv, 'Bad', 0, 100)

    def test_line_quantity_negative_rejected(self):
        """Số lượng âm bị từ chối."""
        inv = self._create_invoice()
        with self.assertRaises(ValidationError):
            self._add_line(inv, 'Bad', -5, 100)

    def test_line_unit_price_negative_rejected(self):
        """Đơn giá âm bị từ chối."""
        inv = self._create_invoice()
        with self.assertRaises(ValidationError):
            self._add_line(inv, 'Bad', 1, -100)

    def test_line_unit_price_zero_ok(self):
        """Đơn giá = 0 (hàng tặng) là hợp lệ."""
        inv = self._create_invoice()
        line = self._add_line(inv, 'Free sample', 10, 0)
        self.assertEqual(line.subtotal, 0)

    def test_partner_tax_code(self):
        """MST đối tác auto-fill từ partner.vat."""
        partner = self.env['res.partner'].create({
            'name': 'Test Corp',
            'vat': '0312345678',
        })
        inv = self._create_invoice(partner_id=partner.id)
        inv._onchange_partner_id()
        self.assertEqual(inv.partner_tax_code, '0312345678')

    def test_payment_term_field(self):
        """Điều khoản thanh toán."""
        inv = self._create_invoice(payment_term='lc')
        self.assertEqual(inv.payment_term, 'lc')

    def test_reset_draft(self):
        """Về nháp từ confirmed."""
        inv = self._create_invoice()
        self._add_line(inv)
        inv.action_confirm()
        inv.action_reset_draft()
        self.assertEqual(inv.state, 'draft')


class TestGarmentPayment(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'KH Test PAY'})

    def _create_invoice_with_line(self, amount=10000):
        inv = self.env['garment.invoice'].create({
            'invoice_type': 'sale',
            'partner_id': self.partner.id,
            'tax_type': 'none',
        })
        self.env['garment.invoice.line'].create({
            'invoice_id': inv.id,
            'description': 'Goods',
            'quantity': 1,
            'unit_price': amount,
        })
        inv.action_confirm()
        return inv

    def test_payment_amount_must_be_positive(self):
        """Số tiền TT phải > 0."""
        with self.assertRaises(ValidationError):
            self.env['garment.payment'].create({
                'partner_id': self.partner.id,
                'amount': 0,
                'payment_type': 'inbound',
            })

    def test_payment_negative_amount_rejected(self):
        """Số tiền âm bị từ chối."""
        with self.assertRaises(ValidationError):
            self.env['garment.payment'].create({
                'partner_id': self.partner.id,
                'amount': -500,
                'payment_type': 'inbound',
            })

    def test_payment_name_auto(self):
        """Số phiếu tự sinh."""
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'amount': 1000,
            'payment_type': 'inbound',
        })
        self.assertTrue(pay.name.startswith('PAY-'))

    def test_overpayment_rejected(self):
        """Không thể TT vượt số còn nợ."""
        inv = self._create_invoice_with_line(5000)
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 6000,
            'payment_type': 'inbound',
        })
        with self.assertRaises(ValidationError):
            pay.action_confirm()

    def test_exact_payment_ok(self):
        """TT đúng số nợ là hợp lệ."""
        inv = self._create_invoice_with_line(5000)
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 5000,
            'payment_type': 'inbound',
        })
        pay.action_confirm()
        self.assertEqual(pay.state, 'confirmed')
        self.assertEqual(inv.residual, 0)

    def test_partial_then_full_payment(self):
        """TT 2 lần: partial + full."""
        inv = self._create_invoice_with_line(10000)
        pay1 = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 3000,
            'payment_type': 'inbound',
        })
        pay1.action_confirm()
        self.assertEqual(inv.residual, 7000)

        pay2 = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'invoice_id': inv.id,
            'amount': 7000,
            'payment_type': 'inbound',
        })
        pay2.action_confirm()
        self.assertEqual(inv.residual, 0)
        self.assertEqual(inv.payment_status, 'paid')

    def test_payment_without_invoice(self):
        """TT không gắn HĐ → OK (advance payment)."""
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'amount': 5000,
            'payment_type': 'outbound',
        })
        pay.action_confirm()
        self.assertEqual(pay.state, 'confirmed')

    def test_cancel_payment(self):
        """Hủy phiếu TT."""
        pay = self.env['garment.payment'].create({
            'partner_id': self.partner.id,
            'amount': 1000,
            'payment_type': 'inbound',
        })
        pay.action_cancel()
        self.assertEqual(pay.state, 'cancelled')
