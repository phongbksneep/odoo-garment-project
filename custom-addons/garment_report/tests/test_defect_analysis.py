from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDefectAnalysis(TransactionCase):
    """Tests for garment.defect.analysis SQL view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Defect',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-DEF-001',
            'code': 'ST-DEF-001',
            'category': 'shirt',
        })
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Defect Test Line',
            'code': 'DEF1',
        })
        cls.prod_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.garment_order.id,
            'style_id': cls.style.id,
            'customer_id': cls.partner.id,
            'sewing_line_id': cls.sewing_line.id,
            'planned_qty': 1000,
        })
        cls.defect_type = cls.env['garment.defect.type'].create({
            'name': 'Broken Stitch Test',
            'code': 'BST-01',
            'category': 'sewing',
        })
        cls.inspector = cls.env['hr.employee'].create({
            'name': 'QC Inspector Test',
        })
        cls.inspection = cls.env['garment.qc.inspection'].create({
            'production_order_id': cls.prod_order.id,
            'style_id': cls.style.id,
            'inspector_id': cls.inspector.id,
            'inspection_type': 'inline',
            'inspected_qty': 100,
            'passed_qty': 95,
            'result': 'fail',
        })
        cls.defect_line = cls.env['garment.qc.defect.line'].create({
            'inspection_id': cls.inspection.id,
            'defect_type_id': cls.defect_type.id,
            'quantity': 5,
        })

    def _refresh_view(self):
        self.env.flush_all()
        self.env['garment.defect.analysis'].init()

    def test_sql_view_accessible(self):
        """Defect analysis SQL view should be queryable."""
        self._refresh_view()
        records = self.env['garment.defect.analysis'].search([])
        self.assertTrue(len(records) >= 1)

    def test_defect_rate_calculated(self):
        """Defect rate = defects / inspected * 100."""
        self._refresh_view()
        records = self.env['garment.defect.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertTrue(len(records) >= 1)
        rec = records[0]
        self.assertEqual(rec.total_inspected, 100)
        self.assertEqual(rec.total_defects, 5)
        self.assertAlmostEqual(rec.defect_rate, 5.0, places=1)

    def test_result_field(self):
        """Result field should match inspection result."""
        self._refresh_view()
        records = self.env['garment.defect.analysis'].search([
            ('production_order_id', '=', self.prod_order.id),
        ])
        self.assertEqual(records[0].result, 'fail')

    def test_defect_type_linked(self):
        """Defect type should be properly linked."""
        self._refresh_view()
        records = self.env['garment.defect.analysis'].search([
            ('defect_type_id', '=', self.defect_type.id),
        ])
        self.assertTrue(len(records) >= 1)
        self.assertEqual(records[0].style_id, self.style)
