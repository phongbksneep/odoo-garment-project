from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestMaterialReceipt(TransactionCase):
    """Tests for garment.material.receipt."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({
            'name': 'NCC Vải Test',
            'supplier_rank': 1,
        })
        cls.buyer = cls.env['res.partner'].create({
            'name': 'Buyer CMT Test',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Style Test MR',
            'code': 'ST-MR-01',
            'category': 'shirt',
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.buyer.id,
            'style_id': cls.style.id,
        })

    def _create_receipt(self, receipt_type='purchase', **kwargs):
        vals = {
            'receipt_type': receipt_type,
            'date': '2026-02-01',
            'warehouse_type': 'material',
        }
        if receipt_type == 'purchase':
            vals['supplier_id'] = self.supplier.id
        elif receipt_type == 'buyer_supplied':
            vals['buyer_id'] = self.buyer.id
        vals.update(kwargs)
        return self.env['garment.material.receipt'].create(vals)

    def _add_line(self, receipt, **kwargs):
        vals = {
            'receipt_id': receipt.id,
            'material_type': 'fabric',
            'description': 'Vải Cotton Oxford',
            'unit': 'm',
            'quantity': 1000,
        }
        vals.update(kwargs)
        return self.env['garment.material.receipt.line'].create(vals)

    # ----- PURCHASE RECEIPT -----
    def test_create_purchase_receipt(self):
        receipt = self._create_receipt('purchase')
        self.assertTrue(receipt.name.startswith('MR-'))
        self.assertEqual(receipt.state, 'draft')
        self.assertEqual(receipt.qc_status, 'pending')

    def test_purchase_receipt_requires_supplier(self):
        with self.assertRaises(ValidationError):
            self.env['garment.material.receipt'].create({
                'receipt_type': 'purchase',
                'date': '2026-02-01',
                'warehouse_type': 'material',
                # no supplier_id
            })

    # ----- BUYER-SUPPLIED RECEIPT -----
    def test_create_buyer_supplied_receipt(self):
        receipt = self._create_receipt('buyer_supplied')
        self.assertTrue(receipt.name.startswith('BS-'))
        self.assertEqual(receipt.receipt_type, 'buyer_supplied')

    def test_buyer_supplied_requires_buyer(self):
        with self.assertRaises(ValidationError):
            self.env['garment.material.receipt'].create({
                'receipt_type': 'buyer_supplied',
                'date': '2026-02-01',
                'warehouse_type': 'material',
                # no buyer_id
            })

    # ----- WORKFLOW -----
    def test_workflow_purchase(self):
        receipt = self._create_receipt('purchase')
        self._add_line(receipt)

        receipt.action_confirm()
        self.assertEqual(receipt.state, 'confirmed')

        receipt.action_inspect()
        self.assertEqual(receipt.state, 'inspecting')

        receipt.action_pass_qc()
        self.assertEqual(receipt.qc_status, 'pass')

        receipt.action_done()
        self.assertEqual(receipt.state, 'done')

    def test_cannot_done_without_qc(self):
        receipt = self._create_receipt('purchase')
        self._add_line(receipt)
        receipt.action_confirm()
        receipt.action_inspect()
        # qc_status still 'pending'
        with self.assertRaises(UserError):
            receipt.action_done()

    def test_cannot_cancel_done(self):
        receipt = self._create_receipt('purchase')
        self._add_line(receipt)
        receipt.action_confirm()
        receipt.action_inspect()
        receipt.action_pass_qc()
        receipt.action_done()
        with self.assertRaises(UserError):
            receipt.action_cancel()

    def test_confirm_requires_lines(self):
        receipt = self._create_receipt('purchase')
        with self.assertRaises(UserError):
            receipt.action_confirm()

    # ----- COMPUTED FIELDS -----
    def test_totals_computed(self):
        receipt = self._create_receipt('purchase')
        self._add_line(receipt, quantity=500, unit_price=50000)
        self._add_line(receipt, description='Chỉ may', material_type='thread',
                       unit='cone', quantity=200, unit_price=10000)
        self.assertEqual(receipt.total_lines, 2)
        self.assertEqual(receipt.total_qty, 700)
        self.assertEqual(receipt.total_value, 500 * 50000 + 200 * 10000)

    def test_shortage_computed(self):
        receipt = self._create_receipt('purchase')
        line = self._add_line(receipt, quantity_ordered=1200, quantity=1000)
        self.assertEqual(line.shortage, 200)

    def test_is_late(self):
        receipt = self._create_receipt(
            'purchase',
            expected_date='2026-01-25',
            date='2026-02-01',
        )
        self.assertTrue(receipt.is_late)

    def test_not_late(self):
        receipt = self._create_receipt(
            'purchase',
            expected_date='2026-02-05',
            date='2026-02-01',
        )
        self.assertFalse(receipt.is_late)


@tagged('post_install', '-at_install')
class TestMaterialAllocation(TransactionCase):
    """Tests for garment.material.allocation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.buyer = cls.env['res.partner'].create({
            'name': 'Buyer Alloc Test',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Style Test MA',
            'code': 'ST-MA-01',
            'category': 'shirt',
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.buyer.id,
            'style_id': cls.style.id,
        })

    def _create_allocation(self, **kwargs):
        vals = {
            'garment_order_id': self.order.id,
            'date': '2026-02-10',
        }
        vals.update(kwargs)
        return self.env['garment.material.allocation'].create(vals)

    def test_create_allocation(self):
        alloc = self._create_allocation()
        self.assertTrue(alloc.name.startswith('MA-'))
        self.assertEqual(alloc.state, 'draft')
        self.assertEqual(alloc.style_id, self.style)

    def test_allocation_workflow(self):
        alloc = self._create_allocation()
        self.env['garment.material.allocation.line'].create({
            'allocation_id': alloc.id,
            'material_type': 'fabric',
            'description': 'Vải chính',
            'unit': 'm',
            'quantity_required': 5000,
            'quantity_issued': 4800,
        })
        alloc.action_confirm()
        self.assertEqual(alloc.state, 'confirmed')
        alloc.action_issue()
        self.assertEqual(alloc.state, 'issued')

    def test_cannot_cancel_issued(self):
        alloc = self._create_allocation()
        self.env['garment.material.allocation.line'].create({
            'allocation_id': alloc.id,
            'material_type': 'fabric',
            'description': 'Vải test',
            'unit': 'm',
            'quantity_issued': 100,
        })
        alloc.action_confirm()
        alloc.action_issue()
        with self.assertRaises(UserError):
            alloc.action_cancel()

    def test_confirm_requires_lines(self):
        alloc = self._create_allocation()
        with self.assertRaises(UserError):
            alloc.action_confirm()
