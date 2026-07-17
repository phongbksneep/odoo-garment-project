from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestQCInspection(TransactionCase):
    """Workflow, guard và compute của phiếu kiểm tra chất lượng."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspector = cls.env['hr.employee'].create({'name': 'QC Tester'})
        cls.defect_stain = cls.env['garment.defect.type'].create({
            'name': 'Vết Bẩn Test',
            'code': 'DEF-STAIN-T',
            'category': 'fabric',
            'severity': 'minor',
        })
        cls.defect_seam = cls.env['garment.defect.type'].create({
            'name': 'Lệch Đường May Test',
            'code': 'DEF-SEAM-T',
            'category': 'sewing',
            'severity': 'major',
        })
        cls.defect_broken = cls.env['garment.defect.type'].create({
            'name': 'Rách Test',
            'code': 'DEF-BROKEN-T',
            'category': 'fabric',
            'severity': 'critical',
        })

    def _create_inspection(self, **kwargs):
        vals = {
            'inspection_type': 'inline',
            'inspector_id': self.inspector.id,
            'inspected_qty': 100,
            'passed_qty': 90,
        }
        vals.update(kwargs)
        return self.env['garment.qc.inspection'].create(vals)

    def _add_defect(self, inspection, defect_type, qty):
        # severity là related tới defect_type_id.severity
        return self.env['garment.qc.defect.line'].create({
            'inspection_id': inspection.id,
            'defect_type_id': defect_type.id,
            'quantity': qty,
        })

    # ----- Workflow -----
    def test_happy_path(self):
        insp = self._create_inspection()
        self.assertEqual(insp.state, 'draft')
        insp.action_start()
        self.assertEqual(insp.state, 'in_progress')
        insp.action_done()
        self.assertEqual(insp.state, 'done')

    def test_cannot_done_from_draft(self):
        insp = self._create_inspection()
        with self.assertRaises(UserError):
            insp.action_done()

    def test_cannot_start_twice(self):
        insp = self._create_inspection()
        insp.action_start()
        with self.assertRaises(UserError):
            insp.action_start()

    def test_cannot_cancel_done(self):
        insp = self._create_inspection()
        insp.action_start()
        insp.action_done()
        with self.assertRaises(UserError):
            insp.action_cancel()

    def test_cancel_draft_ok(self):
        insp = self._create_inspection()
        insp.action_cancel()
        self.assertEqual(insp.state, 'cancelled')

    # ----- Computes -----
    def test_failed_qty(self):
        insp = self._create_inspection(inspected_qty=100, passed_qty=88)
        self.assertEqual(insp.failed_qty, 12)

    def test_pass_rate(self):
        insp = self._create_inspection(inspected_qty=200, passed_qty=150)
        self.assertAlmostEqual(insp.pass_rate, 75.0)

    def test_pass_rate_zero_inspected(self):
        insp = self._create_inspection(inspected_qty=0, passed_qty=0)
        self.assertEqual(insp.pass_rate, 0.0)

    def test_defect_summary(self):
        insp = self._create_inspection()
        self._add_defect(insp, self.defect_stain, 3)
        self._add_defect(insp, self.defect_seam, 2)
        self._add_defect(insp, self.defect_broken, 1)
        self.assertEqual(insp.total_defects, 6)
        self.assertEqual(insp.minor_defects, 3)
        self.assertEqual(insp.major_defects, 2)
        self.assertEqual(insp.critical_defects, 1)
