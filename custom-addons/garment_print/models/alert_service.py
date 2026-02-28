import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class GarmentAlertService(models.Model):
    """Service for scheduled alert actions in garment manufacturing."""
    _name = 'garment.alert.service'
    _description = 'Garment Alert Service'
    _log_access = False

    # ------------------------------------------------------------------
    # 1) Late Order Alerts
    # ------------------------------------------------------------------
    @api.model
    def _cron_check_late_orders(self):
        """Check for garment orders past their delivery date."""
        today = fields.Date.today()
        late_orders = self.env['garment.order'].search([
            ('delivery_date', '<', today),
            ('state', 'not in', ['done', 'cancelled', 'shipped']),
        ])
        if not late_orders:
            _logger.info("Garment Alert: No late orders found.")
            return True

        # Build message
        body_lines = [
            _('<h3>⚠️ Cảnh Báo Đơn Hàng Trễ Hạn — %s</h3>') % today,
            '<table style="border-collapse:collapse;width:100%">',
            '<tr style="background:#f44336;color:#fff">'
            '<th style="padding:8px;border:1px solid #ddd">Đơn Hàng</th>'
            '<th style="padding:8px;border:1px solid #ddd">Khách Hàng</th>'
            '<th style="padding:8px;border:1px solid #ddd">Ngày Giao</th>'
            '<th style="padding:8px;border:1px solid #ddd">Trễ (Ngày)</th>'
            '<th style="padding:8px;border:1px solid #ddd">Trạng Thái</th>'
            '</tr>',
        ]
        for order in late_orders:
            days_late = (today - order.delivery_date).days
            body_lines.append(
                '<tr>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd;color:red;font-weight:bold">%d</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '</tr>' % (
                    order.name,
                    order.customer_id.name or '',
                    order.delivery_date,
                    days_late,
                    dict(order._fields['state'].selection).get(order.state, ''),
                )
            )
        body_lines.append('</table>')
        body_lines.append(
            _('<p>Tổng: <b>%d đơn hàng trễ hạn</b></p>') % len(late_orders)
        )
        body = '\n'.join(body_lines)

        # Post to first late order's chatter + send notification to managers
        self._send_notification(
            subject=_('⚠️ %d Đơn Hàng Trễ Hạn — %s') % (len(late_orders), today),
            body=body,
        )
        _logger.info("Garment Alert: Found %d late orders.", len(late_orders))
        return True

    # ------------------------------------------------------------------
    # 2) High QC Fail Rate Alerts
    # ------------------------------------------------------------------
    @api.model
    def _cron_check_qc_fail_rate(self):
        """Check for QC inspections with high fail rate in last 7 days."""
        date_from = fields.Datetime.now() - timedelta(days=7)
        inspections = self.env['garment.qc.inspection'].search([
            ('inspection_date', '>=', date_from),
            ('state', '=', 'done'),
            ('inspected_qty', '>', 0),
        ])
        high_fail = inspections.filtered(
            lambda i: i.pass_rate < 90.0
        )
        if not high_fail:
            _logger.info("Garment Alert: No high QC fail rate inspections.")
            return True

        body_lines = [
            _('<h3>🔍 Cảnh Báo QC Tỷ Lệ Lỗi Cao (7 ngày qua)</h3>'),
            '<table style="border-collapse:collapse;width:100%">',
            '<tr style="background:#ff9800;color:#fff">'
            '<th style="padding:8px;border:1px solid #ddd">Phiếu QC</th>'
            '<th style="padding:8px;border:1px solid #ddd">Loại</th>'
            '<th style="padding:8px;border:1px solid #ddd">SL Kiểm</th>'
            '<th style="padding:8px;border:1px solid #ddd">Tỷ Lệ Đạt (%)</th>'
            '<th style="padding:8px;border:1px solid #ddd">Tổng Lỗi</th>'
            '</tr>',
        ]
        for qc in high_fail:
            color = 'red' if qc.pass_rate < 80 else 'orange'
            body_lines.append(
                '<tr>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd">%d</td>'
                '<td style="padding:6px;border:1px solid #ddd;color:%s;font-weight:bold">%.1f%%</td>'
                '<td style="padding:6px;border:1px solid #ddd">%d</td>'
                '</tr>' % (
                    qc.name,
                    dict(qc._fields['inspection_type'].selection).get(qc.inspection_type, ''),
                    qc.inspected_qty,
                    color,
                    qc.pass_rate,
                    qc.total_defects,
                )
            )
        body_lines.append('</table>')
        body_lines.append(
            _('<p>Tổng: <b>%d phiếu QC có tỷ lệ đạt &lt; 90%%</b></p>') % len(high_fail)
        )
        body = '\n'.join(body_lines)

        self._send_notification(
            subject=_('🔍 %d Phiếu QC Tỷ Lệ Lỗi Cao (7 ngày)') % len(high_fail),
            body=body,
        )
        _logger.info("Garment Alert: Found %d high-fail QC inspections.", len(high_fail))
        return True

    # ------------------------------------------------------------------
    # 3) Upcoming Delivery Alerts (orders due within 3 days)
    # ------------------------------------------------------------------
    @api.model
    def _cron_check_upcoming_deliveries(self):
        """Alert about orders with delivery date within the next 3 days."""
        today = fields.Date.today()
        date_limit = today + timedelta(days=3)
        upcoming = self.env['garment.order'].search([
            ('delivery_date', '>=', today),
            ('delivery_date', '<=', date_limit),
            ('state', 'not in', ['done', 'cancelled', 'shipped']),
        ])
        if not upcoming:
            _logger.info("Garment Alert: No upcoming deliveries in 3 days.")
            return True

        body_lines = [
            _('<h3>📅 Đơn Hàng Sắp Đến Hạn Giao (3 ngày tới)</h3>'),
            '<table style="border-collapse:collapse;width:100%">',
            '<tr style="background:#2196f3;color:#fff">'
            '<th style="padding:8px;border:1px solid #ddd">Đơn Hàng</th>'
            '<th style="padding:8px;border:1px solid #ddd">Khách Hàng</th>'
            '<th style="padding:8px;border:1px solid #ddd">Ngày Giao</th>'
            '<th style="padding:8px;border:1px solid #ddd">Còn Lại</th>'
            '<th style="padding:8px;border:1px solid #ddd">Trạng Thái</th>'
            '</tr>',
        ]
        for order in upcoming:
            days_left = (order.delivery_date - today).days
            body_lines.append(
                '<tr>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '<td style="padding:6px;border:1px solid #ddd;font-weight:bold">%d ngày</td>'
                '<td style="padding:6px;border:1px solid #ddd">%s</td>'
                '</tr>' % (
                    order.name,
                    order.customer_id.name or '',
                    order.delivery_date,
                    days_left,
                    dict(order._fields['state'].selection).get(order.state, ''),
                )
            )
        body_lines.append('</table>')
        body = '\n'.join(body_lines)

        self._send_notification(
            subject=_('📅 %d Đơn Hàng Sắp Đến Hạn (3 ngày)') % len(upcoming),
            body=body,
        )
        _logger.info("Garment Alert: %d orders due within 3 days.", len(upcoming))
        return True

    # ------------------------------------------------------------------
    # Helper: send notification via chatter / Discuss
    # ------------------------------------------------------------------
    @api.model
    def _send_notification(self, subject, body):
        """Send notification to Garment Manager group users via Discuss."""
        # Try to find manager group
        manager_group = self.env.ref(
            'garment_base.group_garment_manager', raise_if_not_found=False
        )
        partner_ids = []
        if manager_group:
            partner_ids = manager_group.user_ids.mapped('partner_id').ids

        # Fallback: send to admin
        if not partner_ids:
            admin = self.env.ref('base.user_admin', raise_if_not_found=False)
            if admin:
                partner_ids = [admin.partner_id.id]

        if partner_ids:
            # Post as a note in Discuss (general channel or create one)
            channel = self.env['discuss.channel'].search(
                [('name', '=', 'Garment Alerts')], limit=1
            )
            if not channel:
                channel = self.env['discuss.channel'].create({
                    'name': 'Garment Alerts',
                    'channel_type': 'channel',
                    'description': 'Kênh thông báo tự động từ hệ thống Garment ERP',
                })
                # Add manager partners
                channel.add_members(partner_ids)

            channel.message_post(
                body=body,
                subject=subject,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
        return True
