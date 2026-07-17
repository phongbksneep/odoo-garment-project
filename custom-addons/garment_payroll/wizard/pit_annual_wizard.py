import base64
import io
from datetime import date

from odoo import models, fields, _
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class PitAnnualWizard(models.TransientModel):
    """Tổng hợp thuế TNCN theo năm (số liệu phục vụ quyết toán)."""
    _name = 'garment.pit.annual.wizard'
    _description = 'Xuất Tổng Hợp Thuế TNCN Năm'

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
            ('year', '=', self.year),
            ('state', '!=', 'draft'),
        ])
        if not wages:
            raise UserError(_(
                'Không có dữ liệu lương (đã tính) cho năm %d!') % self.year)

        # Gộp theo nhân viên
        data = {}
        for wage in wages:
            emp = wage.employee_id
            row = data.setdefault(emp, {
                'months': 0, 'total_wage': 0.0, 'insurance': 0.0,
                'exempt': 0.0, 'personal': 0.0, 'dependent': 0.0,
                'taxable': 0.0, 'pit': 0.0,
            })
            row['months'] += 1
            row['total_wage'] += wage.total_wage
            row['insurance'] += wage.total_insurance
            row['exempt'] += (wage.tax_exempt_allowance
                              + wage.ot_exempt_amount)
            row['personal'] += wage.personal_deduction
            row['dependent'] += wage.dependent_deduction
            row['taxable'] += wage.taxable_income
            row['pit'] += wage.pit_amount

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('TNCN %d' % self.year)
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center',
            'valign': 'vcenter'})
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#7B1FA2', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True})
        number_fmt = workbook.add_format({
            'num_format': '#,##0', 'border': 1, 'align': 'right'})
        text_fmt = workbook.add_format({'border': 1, 'align': 'left'})
        total_fmt = workbook.add_format({
            'bold': True, 'num_format': '#,##0', 'border': 1,
            'align': 'right', 'bg_color': '#FFF9C4'})

        sheet.merge_range(
            'A1:K1',
            'TỔNG HỢP THUẾ TNCN NĂM %d (số liệu phục vụ quyết toán)'
            % self.year, title_fmt)
        sheet.set_row(0, 30)

        headers = [
            'STT', 'Họ Tên', 'Mã Số Thuế', 'Số Tháng',
            'Tổng Thu Nhập', 'BH Đã Trừ', 'Thu Nhập Miễn Thuế',
            'Giảm Trừ Bản Thân', 'Giảm Trừ Phụ Thuộc',
            'Thu Nhập Chịu Thuế', 'Thuế Đã Khấu Trừ',
        ]
        widths = [5, 25, 14, 8, 14, 12, 14, 14, 14, 14, 14]
        for col, (header, width) in enumerate(zip(headers, widths)):
            sheet.write(2, col, header, header_fmt)
            sheet.set_column(col, col, width)

        row = 3
        totals = [0.0] * 7
        for idx, (emp, vals) in enumerate(
                sorted(data.items(), key=lambda kv: kv[0].name), start=1):
            sheet.write(row, 0, idx, text_fmt)
            sheet.write(row, 1, emp.name, text_fmt)
            sheet.write(row, 2, emp.sudo().tax_code or '', text_fmt)
            sheet.write(row, 3, vals['months'], text_fmt)
            amounts = [vals['total_wage'], vals['insurance'],
                       vals['exempt'], vals['personal'],
                       vals['dependent'], vals['taxable'], vals['pit']]
            for col, val in enumerate(amounts, start=4):
                sheet.write(row, col, val, number_fmt)
            for i, val in enumerate(amounts):
                totals[i] += val
            row += 1

        sheet.merge_range(row, 0, row, 3, 'TỔNG CỘNG', total_fmt)
        for col, val in enumerate(totals, start=4):
            sheet.write(row, col, val, total_fmt)

        workbook.close()
        self.write({
            'file_data': base64.b64encode(output.getvalue()),
            'file_name': 'TNCN_%d.xlsx' % self.year,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
