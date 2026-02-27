from odoo import models, fields, api, _


class GarmentProductionReport(models.TransientModel):
    """Wizard for generating production summary reports."""
    _name = 'garment.production.report'
    _description = 'Production Report Wizard'

    date_from = fields.Date(
        string='Từ Ngày',
        required=True,
        default=fields.Date.today,
    )
    date_to = fields.Date(
        string='Đến Ngày',
        required=True,
        default=fields.Date.today,
    )
    sewing_line_ids = fields.Many2many(
        'garment.sewing.line',
        string='Chuyền May',
        help='Bỏ trống để lấy tất cả chuyền',
    )
    style_ids = fields.Many2many(
        'garment.style',
        string='Mã Hàng',
        help='Bỏ trống để lấy tất cả mã hàng',
    )

    def action_generate_report(self):
        """Open efficiency analysis view filtered by wizard params."""
        self.ensure_one()
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.sewing_line_ids:
            domain.append(
                ('sewing_line_id', 'in', self.sewing_line_ids.ids)
            )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Báo Cáo Sản Xuất %s → %s') % (
                self.date_from, self.date_to,
            ),
            'res_model': 'garment.efficiency.analysis',
            'view_mode': 'list,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_group_line': 1,
            },
        }
