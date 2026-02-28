/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Garment Mobile Dashboard — OWL Component
 *
 * Touch-friendly, mobile-optimized dashboard showing:
 * - KPI cards (orders, production, quality, delivery, approvals)
 * - Production progress bar
 * - Late orders alert list
 * - Upcoming deliveries list
 * - Quick-action buttons for common tasks
 *
 * Design notes (lưu ý cho mobile):
 * - Touch targets >= 44px (Apple HIG)
 * - Card-based layout, 2-column grid on phone
 * - Minimal text, large numbers
 * - Pull-to-refresh style refresh button
 */
export class GarmentMobileDashboard extends Component {
    static template = "garment_mobile.MobileDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            data: {
                order: { total: 0, active: 0, done: 0, late: 0 },
                production: {
                    active: 0,
                    done: 0,
                    planned_qty: 0,
                    completed_qty: 0,
                    completion_pct: 0,
                },
                quality: { total: 0, pass_count: 0, pass_rate: 100 },
                delivery: { pending: 0, done: 0 },
                upcoming: [],
                late: [],
                pending_approvals: 0,
            },
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "garment.mobile.dashboard",
                "get_dashboard_data",
                [],
            );
            this.state.data = data;
        } catch (e) {
            console.error("Mobile dashboard load error:", e);
        }
        this.state.loading = false;
    }

    async onRefresh() {
        await this.loadData();
    }

    /**
     * Open an Odoo action by its XML id.
     */
    openAction(actionXmlId) {
        this.action.doAction(actionXmlId);
    }

    /**
     * Open the main garment dashboard (list/pivot view).
     */
    openDashboard() {
        this.action.doAction("garment_dashboard.action_dashboard_kpi");
    }

    /**
     * Navigate to a specific order by name.
     */
    async openOrder(orderName) {
        const ids = await this.orm.call(
            "garment.order",
            "search",
            [[["name", "=", orderName]]],
        );
        if (ids && ids.length) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "garment.order",
                res_id: ids[0],
                views: [[false, "form"]],
                target: "current",
            });
        }
    }
}

// Register as a client action so Odoo can display it
registry.category("actions").add("garment_mobile_dashboard", GarmentMobileDashboard);
