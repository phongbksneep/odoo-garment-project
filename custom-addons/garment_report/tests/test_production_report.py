from datetime import date
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestProductionReport(TransactionCase):
    """Tests for garment.production.report wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Report Test Line',
            'code': 'RPT1',
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-RPT-001',
            'code': 'ST-RPT-001',
            'category': 'shirt',
        })

    def test_date_validation(self):
        """date_from must be <= date_to."""
        with self.assertRaises(ValidationError):
            self.env['garment.production.report'].create({
                'date_from': date(2026, 3, 15),
                'date_to': date(2026, 3, 1),
            })

    def test_same_date_ok(self):
        """Same from/to date is valid (single day report)."""
        today = date.today()
        wizard = self.env['garment.production.report'].create({
            'date_from': today,
            'date_to': today,
        })
        self.assertEqual(wizard.date_from, today)

    def test_generate_report_action(self):
        """Wizard should return an action dict with proper domain."""
        wizard = self.env['garment.production.report'].create({
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 1, 31),
            'sewing_line_ids': [(6, 0, [self.sewing_line.id])],
        })
        result = wizard.action_generate_report()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'garment.efficiency.analysis')
        # Should have date range + sewing_line filter
        self.assertTrue(len(result['domain']) >= 3)

    def test_generate_report_with_style_filter(self):
        """Style filter should be applied in domain."""
        wizard = self.env['garment.production.report'].create({
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 1, 31),
            'style_ids': [(6, 0, [self.style.id])],
        })
        result = wizard.action_generate_report()
        # Should have date range + style filter
        domain_str = str(result['domain'])
        self.assertIn('style_id', domain_str)

    def test_generate_report_no_filters(self):
        """Without sewing_line/style, domain should only have dates."""
        wizard = self.env['garment.production.report'].create({
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 1, 31),
        })
        result = wizard.action_generate_report()
        self.assertEqual(len(result['domain']), 2)
