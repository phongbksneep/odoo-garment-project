from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # --- Bảo hiểm & mức nhà nước ---
    payroll_luong_co_so = fields.Float(
        string='Lương Cơ Sở (VNĐ)',
        config_parameter='garment_payroll.luong_co_so',
        default=2340000,
        help='Dùng tính trần đóng BHXH/BHYT (20 lần lương cơ sở).',
    )
    payroll_luong_toi_thieu_vung = fields.Float(
        string='Lương Tối Thiểu Vùng (VNĐ)',
        config_parameter='garment_payroll.luong_toi_thieu_vung',
        default=4960000,
        help='Theo vùng của doanh nghiệp (vùng 1: 4,96tr; vùng 2: 4,41tr; '
             'vùng 3: 3,86tr; vùng 4: 3,45tr). Dùng tính trần BHTN.',
    )

    # --- Thuế TNCN ---
    payroll_pit_enabled = fields.Boolean(
        string='Khấu Trừ Thuế TNCN',
        config_parameter='garment_payroll.pit_enabled',
        default=True,
        help='Tắt nếu doanh nghiệp không khấu trừ thuế TNCN tại nguồn.',
    )
    payroll_personal_deduction = fields.Float(
        string='Giảm Trừ Bản Thân (VNĐ/tháng)',
        config_parameter='garment_payroll.personal_deduction',
        default=15500000,
    )
    payroll_dependent_deduction = fields.Float(
        string='Giảm Trừ Người Phụ Thuộc (VNĐ/người/tháng)',
        config_parameter='garment_payroll.dependent_deduction',
        default=6200000,
    )
    payroll_lunch_cap = fields.Float(
        string='Trần Miễn Thuế Ăn Trưa (VNĐ/tháng)',
        config_parameter='garment_payroll.lunch_allowance_cap',
        default=730000,
    )

    # --- Hệ số tăng ca (mặc định theo Điều 98 BLLĐ 2019) ---
    payroll_ot_mult_weekday = fields.Float(
        string='Hệ Số TC Ngày Thường',
        config_parameter='garment_payroll.ot_mult_weekday',
        default=1.5,
        help='Luật định tối thiểu 150%. Giảm xuống là lựa chọn của '
             'doanh nghiệp, không phải khuyến nghị.',
    )
    payroll_ot_mult_weekend = fields.Float(
        string='Hệ Số TC Ngày Nghỉ Tuần',
        config_parameter='garment_payroll.ot_mult_weekend',
        default=2.0,
    )
    payroll_ot_mult_holiday = fields.Float(
        string='Hệ Số TC Ngày Lễ',
        config_parameter='garment_payroll.ot_mult_holiday',
        default=3.0,
    )

    # --- Phép năm ---
    payroll_leave_base_days = fields.Float(
        string='Số Ngày Phép Năm Cơ Bản',
        config_parameter='garment_hr.annual_leave_base_days',
        default=12,
    )
    payroll_leave_seniority_bonus = fields.Boolean(
        string='Cộng Phép Thâm Niên (+1 ngày/5 năm)',
        config_parameter='garment_hr.leave_seniority_bonus',
        default=True,
    )
