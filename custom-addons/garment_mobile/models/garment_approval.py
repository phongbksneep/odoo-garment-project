from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GarmentOrderApproval(models.Model):
    """Extend garment.order with multi-level approval workflow."""
    _inherit = 'garment.order'

    # --- Approval fields ---
    approval_state = fields.Selection([
        ('draft', 'Chưa Gửi Duyệt'),
        ('pending', 'Chờ Duyệt'),
        ('approved', 'Đã Duyệt'),
        ('rejected', 'Từ Chối'),
    ], string='Trạng Thái Duyệt', default='draft',
       tracking=True, copy=False)

    approval_requested_by = fields.Many2one(
        'res.users', string='Người Gửi Duyệt',
        readonly=True, copy=False,
    )
    approval_requested_date = fields.Datetime(
        string='Ngày Gửi Duyệt', readonly=True, copy=False,
    )
    approved_by = fields.Many2one(
        'res.users', string='Người Duyệt',
        readonly=True, copy=False,
    )
    approval_date = fields.Datetime(
        string='Ngày Duyệt', readonly=True, copy=False,
    )
    rejection_reason = fields.Text(
        string='Lý Do Từ Chối', copy=False,
    )
    approval_note = fields.Text(
        string='Ghi Chú Duyệt', copy=False,
    )

    def action_request_approval(self):
        """Send order for approval."""
        for order in self:
            if order.approval_state not in ('draft', 'rejected'):
                raise UserError(_(
                    'Chỉ có thể gửi duyệt đơn hàng ở trạng thái Nháp hoặc Từ Chối.'
                ))
            order.write({
                'approval_state': 'pending',
                'approval_requested_by': self.env.uid,
                'approval_requested_date': fields.Datetime.now(),
                'rejection_reason': False,
            })
            order.message_post(
                body=_('📋 Đơn hàng được gửi duyệt bởi %s') %
                     self.env.user.name,
                subtype_xmlid='mail.mt_comment',
            )
        return True

    def action_approve(self):
        """Approve the order."""
        for order in self:
            if order.approval_state != 'pending':
                raise UserError(_(
                    'Chỉ có thể duyệt đơn hàng đang ở trạng thái Chờ Duyệt.'
                ))
            order.write({
                'approval_state': 'approved',
                'approved_by': self.env.uid,
                'approval_date': fields.Datetime.now(),
                'state': 'confirmed',
            })
            order.message_post(
                body=_('✅ Đơn hàng đã được duyệt bởi %s') %
                     self.env.user.name,
                subtype_xmlid='mail.mt_comment',
            )
        return True

    def action_reject(self):
        """Reject the order — opens a wizard for reason."""
        self.ensure_one()
        return {
            'name': _('Lý Do Từ Chối'),
            'type': 'ir.actions.act_window',
            'res_model': 'garment.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_reset_approval(self):
        """Reset approval to draft."""
        for order in self:
            order.write({
                'approval_state': 'draft',
                'approved_by': False,
                'approval_date': False,
                'rejection_reason': False,
            })
        return True


class GarmentRejectionWizard(models.TransientModel):
    """Wizard to enter rejection reason."""
    _name = 'garment.rejection.wizard'
    _description = 'Từ Chối Đơn Hàng'

    order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng',
        required=True, readonly=True,
    )
    reason = fields.Text(
        string='Lý Do Từ Chối', required=True,
    )

    def action_confirm_reject(self):
        """Confirm rejection with reason."""
        self.ensure_one()
        self.order_id.write({
            'approval_state': 'rejected',
            'rejection_reason': self.reason,
            'approved_by': self.env.uid,
            'approval_date': fields.Datetime.now(),
        })
        self.order_id.message_post(
            body=_('❌ Đơn hàng bị từ chối bởi %s<br/>Lý do: %s') % (
                self.env.user.name, self.reason
            ),
            subtype_xmlid='mail.mt_comment',
        )
        return {'type': 'ir.actions.act_window_close'}
