from datetime import timedelta

from odoo import api, fields, models, tools


class MobileDashboard(models.AbstractModel):
    """Provide dashboard data for the mobile OWL component."""
    _name = 'garment.mobile.dashboard'
    _description = 'Mobile Dashboard Data Provider'

    @api.model
    def get_dashboard_data(self):
        """Return a dict with all KPI data for the mobile dashboard."""
        today = fields.Date.today()
        week_ago = today - timedelta(days=7)

        # --- Orders ---
        Order = self.env['garment.order']
        order_total = Order.search_count([('state', '!=', 'cancelled')])
        order_active = Order.search_count([
            ('state', 'in', [
                'material', 'cutting', 'sewing',
                'finishing', 'qc', 'packing',
            ]),
        ])
        order_done = Order.search_count([
            ('state', 'in', ['shipped', 'done']),
        ])
        order_late = Order.search_count([
            ('delivery_date', '<', today),
            ('state', 'not in', ['shipped', 'done', 'cancelled']),
        ])

        # --- Production ---
        Prod = self.env['garment.production.order']
        prod_active = Prod.search_count([('state', '=', 'in_progress')])
        prod_done = Prod.search_count([('state', '=', 'done')])
        prod_all = Prod.search([('state', '!=', 'cancelled')])
        planned_qty = sum(prod_all.mapped('planned_qty'))
        completed_qty = sum(prod_all.mapped('completed_qty'))
        completion_pct = (
            round(completed_qty / planned_qty * 100, 1)
            if planned_qty > 0 else 0
        )

        # --- QC (last 7 days) ---
        QC = self.env['garment.qc.inspection']
        qc_recent = QC.search([
            ('inspection_date', '>=', fields.Datetime.to_string(
                fields.Datetime.now() - timedelta(days=7)
            )),
            ('state', '=', 'done'),
            ('inspected_qty', '>', 0),
        ])
        qc_pass_count = len(qc_recent.filtered(lambda q: q.pass_rate >= 90))
        qc_total = len(qc_recent)
        qc_pass_rate = (
            round(qc_pass_count / qc_total * 100, 1) if qc_total else 100
        )

        # --- Deliveries ---
        Delivery = self.env['garment.delivery.order']
        delivery_pending = Delivery.search_count([
            ('state', 'in', ['draft', 'confirmed', 'packed']),
        ])
        delivery_done_count = Delivery.search_count([
            ('state', '=', 'done'),
        ])

        # --- Upcoming deliveries (3 days) ---
        upcoming_orders = Order.search([
            ('delivery_date', '>=', today),
            ('delivery_date', '<=', today + timedelta(days=3)),
            ('state', 'not in', ['done', 'cancelled', 'shipped']),
        ], limit=5, order='delivery_date asc')
        upcoming = [
            {
                'name': o.name,
                'customer': o.customer_id.name or '',
                'date': str(o.delivery_date),
                'days': (o.delivery_date - today).days,
            }
            for o in upcoming_orders
        ]

        # --- Late orders ---
        late_orders = Order.search([
            ('delivery_date', '<', today),
            ('state', 'not in', ['shipped', 'done', 'cancelled']),
        ], limit=5, order='delivery_date asc')
        late = [
            {
                'name': o.name,
                'customer': o.customer_id.name or '',
                'date': str(o.delivery_date),
                'days_late': (today - o.delivery_date).days,
            }
            for o in late_orders
        ]

        # --- Pending approvals ---
        pending_approvals = Order.search_count([
            ('approval_state', '=', 'pending'),
        ])

        return {
            'order': {
                'total': order_total,
                'active': order_active,
                'done': order_done,
                'late': order_late,
            },
            'production': {
                'active': prod_active,
                'done': prod_done,
                'planned_qty': planned_qty,
                'completed_qty': completed_qty,
                'completion_pct': completion_pct,
            },
            'quality': {
                'total': qc_total,
                'pass_count': qc_pass_count,
                'pass_rate': qc_pass_rate,
            },
            'delivery': {
                'pending': delivery_pending,
                'done': delivery_done_count,
            },
            'upcoming': upcoming,
            'late': late,
            'pending_approvals': pending_approvals,
        }
