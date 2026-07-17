import base64
import io
from datetime import date

from odoo import models, fields, _
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class BhxhReportWizard(models.TransientModel):
    """Bảng kê đóng BHXH/BHYT/BHTN tháng (số liệu lập mẫu D02-TS)."""
    _name = 'garment.bhxh.report.wizard'
    _description = 'Xuất Bảng Kê BHXH Tháng'

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
    file_data = fields.Binary(string='File Excel', readonly=True)
    file_name = fields.Char(string='Tên File', readonly=True)

    def action_export(self):
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_('Thư viện xlsxwriter chưa được cài đặt!'))
        wages = self.env['garment.wage.calculation'].search([
            ('month', '=', self.month),
            ('year', '=', self.year),
            ('state', '!=', 'draft'),
            ('apply_insurance', '=', True),
        ], order='department_id, employee_id')
        if not wages:
            raise UserError(_(
                'Không có dữ liệu lương (đã tính) có đóng BHXH '
                'cho tháng %s/%d!') % (self.month, self.year))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('BHXH')
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center',
            'valign': 'vcenter'})
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#1976D2', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True})
        number_fmt = workbook.add_format({
            'num_format': '#,##0', 'border': 1, 'align': 'right'})
        text_fmt = workbook.add_format({'border': 1, 'align': 'left'})
        total_fmt = workbook.add_format({
            'bold': True, 'num_format': '#,##0', 'border': 1,
            'align': 'right', 'bg_color': '#FFF9C4'})

        sheet.merge_range(
            'A1:L1',
            'BẢNG KÊ ĐÓNG BHXH - BHYT - BHTN THÁNG %s/%d (số liệu lập D02-TS)'
            % (self.month, self.year),
            title_fmt)
        sheet.set_row(0, 30)

        headers = [
            'STT', 'Họ Tên', 'Mã NV', 'Số Sổ BHXH', 'Mức Đóng',
            'BHXH NLĐ (8%)', 'BHYT NLĐ (1.5%)', 'BHTN NLĐ (1%)',
            'BHXH DN (17.5%)', 'BHYT DN (3%)', 'BHTN DN (1%)',
            'Tổng Cộng',
        ]
        widths = [5, 25, 12, 15, 14, 12, 12, 12, 12, 12, 12, 14]
        for col, (header, width) in enumerate(zip(headers, widths)):
            sheet.write(2, col, header, header_fmt)
            sheet.set_column(col, col, width)

        row = 3
        totals = [0.0] * 8
        for idx, wage in enumerate(wages, start=1):
            emp = wage.employee_id.sudo()
            amounts = [
                wage.insurance_base,
                wage.bhxh_employee, wage.bhyt_employee, wage.bhtn_employee,
                wage.bhxh_employer, wage.bhyt_employer, wage.bhtn_employer,
            ]
            line_total = sum(amounts[1:])
            sheet.write(row, 0, idx, text_fmt)
            sheet.write(row, 1, emp.name, text_fmt)
            sheet.write(row, 2, emp.employee_code or '', text_fmt)
            sheet.write(row, 3, emp.insurance_number or '', text_fmt)
            for col, val in enumerate(amounts, start=4):
                sheet.write(row, col, val, number_fmt)
            sheet.write(row, 11, line_total, number_fmt)
            for i, val in enumerate(amounts + [line_total]):
                totals[i] += val
            row += 1

        sheet.merge_range(row, 0, row, 3, 'TỔNG CỘNG', total_fmt)
        for col, val in enumerate(totals, start=4):
            sheet.write(row, col, val, total_fmt)

        workbook.close()
        self.write({
            'file_data': base64.b64encode(output.getvalue()),
            'file_name': 'BHXH_%s_%d.xlsx' % (self.month, self.year),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
