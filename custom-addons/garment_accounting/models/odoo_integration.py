from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentOrderSaleIntegration(models.Model):
    """Extend garment.order to link with sale.order."""
    _inherit = 'garment.order'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Đơn Bán Hàng (SO)',
        help='Liên kết đến Sale Order của Odoo',
        copy=False,
        tracking=True,
    )
    sale_order_name = fields.Char(
        related='sale_order_id.name',
        string='Mã SO',
    )

    def action_create_sale_order(self):
        """Create a Sale Order from garment order data."""
        self.ensure_one()
        if self.sale_order_id:
            raise UserError(_('Đơn hàng này đã có Sale Order: %s') % self.sale_order_id.name)

        # Build order lines
        order_lines = []
        for line in self.line_ids:
            product = self.env.ref(
                'garment_base.product_garment_service', raise_if_not_found=False
            )
            if not product:
                # Create a generic garment product if not found
                product = self.env['product.product'].search(
                    [('name', '=', 'Garment Product')], limit=1,
                )
                if not product:
                    product = self.env['product.product'].create({
                        'name': 'Garment Product',
                        'type': 'service',
                        'list_price': self.unit_price or 0,
                    })
            order_lines.append((0, 0, {
                'product_id': product.id,
                'name': '%s - %s - %s' % (
                    self.style_id.name or '',
                    line.color_id.name if hasattr(line, 'color_id') and line.color_id else '',
                    line.size_id.name if hasattr(line, 'size_id') and line.size_id else '',
                ),
                'product_uom_qty': line.quantity,
                'price_unit': self.unit_price or 0,
            }))

        if not order_lines:
            # No detail lines → create single line
            product = self.env['product.product'].search(
                [('name', '=', 'Garment Product')], limit=1,
            )
            if not product:
                product = self.env['product.product'].create({
                    'name': 'Garment Product',
                    'type': 'service',
                    'list_price': self.unit_price or 0,
                })
            order_lines.append((0, 0, {
                'product_id': product.id,
                'name': '%s - %s' % (self.name, self.style_id.name or ''),
                'product_uom_qty': self.total_qty or 1,
                'price_unit': self.unit_price or 0,
            }))

        so = self.env['sale.order'].create({
            'partner_id': self.customer_id.id,
            'client_order_ref': self.customer_po or self.name,
            'origin': self.name,
            'order_line': order_lines,
        })
        self.sale_order_id = so.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': so.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_sale_order(self):
        """Open linked Sale Order."""
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError(_('Chưa có Sale Order liên kết!'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class GarmentInvoiceAccountIntegration(models.Model):
    """Extend garment.invoice to link with account.move."""
    _inherit = 'garment.invoice'

    account_move_id = fields.Many2one(
        'account.move',
        string='Bút Toán Kế Toán',
        help='Liên kết đến Account Move / Invoice của Odoo',
        copy=False,
        tracking=True,
    )
    account_move_name = fields.Char(
        related='account_move_id.name',
        string='Mã Bút Toán',
    )

    def action_create_account_move(self):
        """Create an Account Move (Invoice/Bill) from garment invoice."""
        self.ensure_one()
        if self.account_move_id:
            raise UserError(
                _('Hóa đơn này đã có bút toán: %s') % self.account_move_id.name
            )
        if self.state == 'draft':
            raise UserError(_('Hãy xác nhận hóa đơn trước khi tạo bút toán!'))

        move_type = 'out_invoice' if self.invoice_type == 'sale' else 'in_invoice'

        # Build invoice lines
        move_lines = []
        for line in self.line_ids:
            product = self.env['product.product'].search(
                [('name', '=', 'Garment Product')], limit=1,
            )
            if not product:
                product = self.env['product.product'].create({
                    'name': 'Garment Product',
                    'type': 'service',
                })
            move_lines.append((0, 0, {
                'product_id': product.id,
                'name': line.description,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
            }))

        move_vals = {
            'move_type': move_type,
            'partner_id': self.partner_id.id,
            'invoice_date': self.date,
            'invoice_date_due': self.due_date or self.date,
            'ref': self.name,
            'invoice_line_ids': move_lines,
        }

        move = self.env['account.move'].create(move_vals)
        self.account_move_id = move.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_account_move(self):
        """Open linked Account Move."""
        self.ensure_one()
        if not self.account_move_id:
            raise UserError(_('Chưa có bút toán liên kết!'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.account_move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class GarmentMaterialReceiptPurchaseIntegration(models.Model):
    """Extend garment.material.receipt to link with purchase.order."""
    _inherit = 'garment.material.receipt'

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Đơn Mua Hàng (PO)',
        help='Liên kết đến Purchase Order của Odoo',
        copy=False,
        tracking=True,
    )
    purchase_order_name = fields.Char(
        related='purchase_order_id.name',
        string='Mã PO',
    )

    def action_create_purchase_order(self):
        """Create a Purchase Order from material receipt data."""
        self.ensure_one()
        if self.purchase_order_id:
            raise UserError(
                _('Phiếu nhập này đã có PO: %s') % self.purchase_order_id.name
            )
        if not self.supplier_id:
            raise UserError(_('Hãy chọn nhà cung cấp trước!'))

        # Build PO lines from receipt lines
        po_lines = []
        for line in self.line_ids:
            product = self.env['product.product'].search(
                [('name', '=', line.description)], limit=1,
            )
            if not product:
                product = self.env['product.product'].create({
                    'name': line.description,
                    'type': 'consu',
                })
            uom = product.uom_id
            po_lines.append((0, 0, {
                'product_id': product.id,
                'name': line.description,
                'product_qty': line.quantity,
                'product_uom_id': uom.id,
                'price_unit': line.unit_price if hasattr(line, 'unit_price') and line.unit_price else 0,
            }))

        if not po_lines:
            raise UserError(_('Phiếu nhập chưa có dòng chi tiết!'))

        po = self.env['purchase.order'].create({
            'partner_id': self.supplier_id.id,
            'origin': self.name,
            'order_line': po_lines,
        })
        self.purchase_order_id = po.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_purchase_order(self):
        """Open linked Purchase Order."""
        self.ensure_one()
        if not self.purchase_order_id:
            raise UserError(_('Chưa có PO liên kết!'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': self.purchase_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
