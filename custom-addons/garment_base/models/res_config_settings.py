from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    garment_working_minutes_per_day = fields.Integer(
        string='Số Phút Làm Việc / Ngày',
        config_parameter='garment_base.working_minutes_per_day',
        default=480,
        help='Số phút làm việc mỗi ngày (mặc định 480 = 8 giờ), dùng để tính hiệu suất chuyền',
    )
    garment_default_efficiency_target = fields.Float(
        string='Mục Tiêu Hiệu Suất (%)',
        config_parameter='garment_base.default_efficiency_target',
        default=80.0,
        help='Mục tiêu hiệu suất mặc định cho chuyền may (%)',
    )
    garment_default_aql_level = fields.Selection([
        ('I', 'AQL I — Kiểm Ít'),
        ('II', 'AQL II — Tiêu Chuẩn'),
        ('III', 'AQL III — Kiểm Nhiều'),
    ], string='Mức AQL Mặc Định',
        config_parameter='garment_base.default_aql_level',
        default='II',
        help='Mức AQL mặc định cho kiểm tra chất lượng',
    )
    garment_fabric_loss_warning_pct = fields.Float(
        string='Ngưỡng Cảnh Báo Hao Hụt Vải (%)',
        config_parameter='garment_base.fabric_loss_warning_pct',
        default=2.0,
        help='Tỷ lệ hao hụt vải (%) từ mức này trở lên sẽ hiển thị cảnh báo vàng',
    )
    garment_fabric_loss_critical_pct = fields.Float(
        string='Ngưỡng Nguy Hiểm Hao Hụt Vải (%)',
        config_parameter='garment_base.fabric_loss_critical_pct',
        default=5.0,
        help='Tỷ lệ hao hụt vải (%) từ mức này trở lên sẽ hiển thị cảnh báo đỏ',
    )
    garment_company_short_name = fields.Char(
        string='Tên Viết Tắt Công Ty',
        config_parameter='garment_base.company_short_name',
        help='Tên viết tắt hiển thị trên báo cáo, tem nhãn (VD: GMC)',
    )
