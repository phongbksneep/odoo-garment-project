from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestConfigSettings(TransactionCase):
    """Tests for garment res.config.settings."""

    def test_settings_default_values(self):
        """Settings have correct default values."""
        settings = self.env['res.config.settings'].create({})
        self.assertEqual(settings.garment_working_minutes_per_day, 480)
        self.assertAlmostEqual(settings.garment_default_efficiency_target, 80.0)
        self.assertEqual(settings.garment_default_aql_level, 'II')
        self.assertAlmostEqual(settings.garment_fabric_loss_warning_pct, 2.0)
        self.assertAlmostEqual(settings.garment_fabric_loss_critical_pct, 5.0)

    def test_settings_save_and_load(self):
        """Settings are persisted via ir.config_parameter."""
        settings = self.env['res.config.settings'].create({
            'garment_working_minutes_per_day': 510,
            'garment_default_efficiency_target': 85.0,
            'garment_default_aql_level': 'III',
            'garment_company_short_name': 'GMC',
        })
        settings.execute()

        ICP = self.env['ir.config_parameter'].sudo()
        self.assertEqual(ICP.get_param('garment_base.working_minutes_per_day'), '510')
        self.assertEqual(ICP.get_param('garment_base.default_aql_level'), 'III')
        self.assertEqual(ICP.get_param('garment_base.company_short_name'), 'GMC')

    def test_settings_reload(self):
        """New settings wizard reads saved values from ir.config_parameter."""
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('garment_base.working_minutes_per_day', '500')
        ICP.set_param('garment_base.default_aql_level', 'I')

        settings = self.env['res.config.settings'].create({})
        self.assertEqual(settings.garment_working_minutes_per_day, 500)
        self.assertEqual(settings.garment_default_aql_level, 'I')


@tagged('post_install', '-at_install')
class TestConfigModels(TransactionCase):
    """Tests for config model constraints and behavior."""

    def test_color_unique_code(self):
        """Color code must be unique."""
        self.env['garment.color'].create({
            'name': 'Test Red CFG',
            'code': 'RED-CFG-UNQ',
        })
        with self.assertRaises(Exception):
            self.env['garment.color'].create({
                'name': 'Another Red CFG',
                'code': 'RED-CFG-UNQ',
            })

    def test_size_unique_code(self):
        """Size code must be unique."""
        self.env['garment.size'].create({
            'name': 'XS CFG',
            'code': 'XS-CFG-UNQ',
            'size_type': 'letter',
        })
        with self.assertRaises(Exception):
            self.env['garment.size'].create({
                'name': 'XS-2 CFG',
                'code': 'XS-CFG-UNQ',
                'size_type': 'letter',
            })

    def test_color_active_default(self):
        """Color active field defaults to True."""
        color = self.env['garment.color'].create({
            'name': 'Active Test CFG',
            'code': 'ACT-CFG',
        })
        self.assertTrue(color.active)

    def test_size_type_values(self):
        """Size type accepts valid values."""
        for st in ('letter', 'number', 'age', 'custom'):
            size = self.env['garment.size'].create({
                'name': f'Size {st} CFG',
                'code': f'SZ-{st}-CFG',
                'size_type': st,
            })
            self.assertEqual(size.size_type, st)

    def test_wash_symbol_categories(self):
        """Wash symbol accepts all category values."""
        for cat in ('wash', 'bleach', 'dry', 'iron', 'dryclean'):
            ws = self.env['garment.wash.symbol'].create({
                'name': f'WS {cat} CFG',
                'code': f'WS-{cat}-CFG',
                'category': cat,
            })
            self.assertEqual(ws.category, cat)

    def test_defect_type_severity(self):
        """Defect type stores severity correctly."""
        dt = self.env['garment.defect.type'].create({
            'name': 'Test Defect CFG',
            'code': 'TD-CFG',
            'category': 'sewing',
            'severity': 'critical',
        })
        self.assertEqual(dt.severity, 'critical')
        self.assertTrue(dt.active)
