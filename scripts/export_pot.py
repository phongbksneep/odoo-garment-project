#!/usr/bin/env python3
"""
Generate .pot template files for all garment modules using Odoo internal API.
Must be run inside the Odoo container.
"""
import odoo
from odoo.tools import config
from odoo.tools.translate import trans_export
import io
import os

config.parse_config(['-d', 'garment_db', '--no-http'])
from odoo.modules.registry import Registry

ADDONS_PATH = '/mnt/extra-addons'

reg = Registry('garment_db')
with reg.cursor() as cr:
    from odoo.api import Environment
    env = Environment(cr, 1, {})

    # Get all installed garment modules
    modules = env['ir.module.module'].search([
        ('name', 'like', 'garment_'),
        ('state', '=', 'installed'),
    ])

    for mod in modules:
        mod_name = mod.name
        i18n_dir = os.path.join(ADDONS_PATH, mod_name, 'i18n')
        os.makedirs(i18n_dir, exist_ok=True)
        pot_file = os.path.join(i18n_dir, '%s.pot' % mod_name)

        buf = io.BytesIO()
        try:
            trans_export(None, [mod_name], buf, 'po', env)
            content = buf.getvalue()
            if content:
                with open(pot_file, 'wb') as f:
                    f.write(content)
                print('OK: %s (%d bytes)' % (mod_name, len(content)))
            else:
                print('EMPTY: %s' % mod_name)
        except Exception as e:
            print('ERROR: %s - %s' % (mod_name, e))
        finally:
            buf.close()
