from datetime import date

from odoo import models, fields, _
from odoo.exceptions import UserError


class AttendanceSummaryBatchWizard(models.TransientModel):
    """Tạo + tính Tổng Hợp Công tháng cho hàng loạt nhân viên."""
    _name = 'garment.attendance.summary.batch.wizard'
    _description = 'Tổng Hợp Công Hàng Loạt'

    month = fields.Selection([
        ('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
        ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
        ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng', required=True,
       default=lambda self: '%02d' % date.today().month)
    year = fields.Integer(
        string='Năm', required=True,
        default=lambda self: date.today().year,
    )
    department_ids = fields.Many2many(
        'hr.department', string='Phòng Ban',
        help='Để trống = toàn bộ nhân viên đang làm việc',
    )

    def action_generate(self):
        self.ensure_one()
        Summary = self.env['garment.attendance.summary']
        employees = self.env['hr.employee'].search(
            [('department_id', 'in', self.department_ids.ids)]
            if self.department_ids else [])
        if not employees:
            raise UserError(_('Không có nhân viên nào phù hợp.'))
        existing = Summary.search([
            ('month', '=', self.month),
            ('year', '=', self.year),
            ('employee_id', 'in', employees.ids),
        ])
        todo = employees - existing.employee_id
        new_summaries = Summary.create([{
            'employee_id': emp.id,
            'month': self.month,
            'year': self.year,
        } for emp in todo])
        all_summaries = existing | new_summaries
        all_summaries.action_calculate()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tổng Hợp Công %s/%d') % (self.month, self.year),
            'res_model': 'garment.attendance.summary',
            'view_mode': 'list,form',
            'domain': [('id', 'in', all_summaries.ids)],
        }
