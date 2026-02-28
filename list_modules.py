#!/usr/bin/env python3
"""Export .pot files for all garment modules using Odoo's translation export."""
import xmlrpc.client
import os
import base64

URL = 'http://localhost:8069'
DB = 'garment_db'
USER = 'admin'
PASS = 'admin'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

# Get all garment modules
module_ids = models.execute_kw(DB, uid, PASS, 'ir.module.module', 'search_read',
    [[('name', 'like', 'garment_'), ('state', '=', 'installed')]],
    {'fields': ['name']})

print(f"Found {len(module_ids)} installed garment modules:")
for m in module_ids:
    print(f"  - {m['name']}")
