# 🧵 Odoo 19 - Hệ Thống Quản Lý Công Ty May

Dự án ERP sử dụng **Odoo 19.0 Community Edition** được tùy chỉnh cho ngành **may mặc (Garment Manufacturing)**, bao gồm **25 module chuyên biệt** bao phủ toàn bộ quy trình từ nhận đơn hàng đến xuất hàng, bao gồm CRM khách hàng, nhập nguyên liệu, sản xuất, kiểm kê kho, quản lý nhân viên, phân quyền 4 cấp, hoàn thiện, chấm công, kế toán, kho, giặt, gia công, in tem/QR code, đóng tách pallet/thùng, vận chuyển và dashboard tổng quan.

## 📋 Yêu cầu

- **Docker & Docker Compose** (Khuyến nghị)
- Hoặc: Python 3.10+, PostgreSQL 16+, Node.js 18+

## 🚀 Cài đặt & Khởi động

### Sử dụng Docker (Khuyến nghị)

```bash
cd odoo-garment-project
docker compose up -d
# Truy cập: http://localhost:8069
# Đăng nhập: admin / admin (database: garment_db)
```

### Cài đặt thủ công trên macOS

```bash
brew install postgresql@16
brew services start postgresql@16
createuser -s odoo
cd odoo-garment-project/odoo
pip install -r requirements.txt
python odoo-bin -c ../odoo.conf
```

## 📦 Custom Modules (25 Module) — 214 Tests ✅

### Pha 1 — Nền Tảng Cơ Sở

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_base` | Module cơ sở: vải, phụ liệu, mẫu may, đơn hàng, ký hiệu giặt ủi, phân quyền 4 cấp | — |
| `garment_production` | Sản xuất: chuyền may, lệnh SX, lệnh cắt, sản lượng, tiến độ | — |
| `garment_quality` | Chất lượng: QC inline/endline/final, AQL, phân loại lỗi | — |

### Pha 2 — Module Chuyên Sâu

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_costing` | Tính giá thành FOB/CM/CMT, BOM integration | 8 ✅ |
| `garment_sample` | Quản lý mẫu may: Proto, Fit, PP, TOP, revision | 12 ✅ |
| `garment_cutting` | Cắt nâng cao: marker, trải vải, bó hàng | 9 ✅ |
| `garment_packing` | Đóng gói: packing list, carton, shipping | 10 ✅ |

### Pha 3 — Báo Cáo & Phân Tích

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_report` | Hiệu suất chuyền (SQL view), phân tích lỗi, wizard báo cáo | — |

### Pha 4 — Tối Ưu & Nâng Cao

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_planning` | Kế hoạch SX: phân chuyền, auto-schedule | 8 ✅ |
| `garment_maintenance` | Bảo trì máy may: lịch định kỳ, sửa chữa, downtime | 11 ✅ |
| `garment_payroll` | Lương khoán: piece rate, sản lượng, BHXH/BHYT, thưởng | 9 ✅ |
| `garment_compliance` | Tuân thủ: audit BSCI/WRAP/SA8000, CAP | 14 ✅ |

### Pha 5 — Xưởng Giặt & Gia Công

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_washing` | Xưởng giặt: hóa chất, công thức, đơn giặt | 24 ✅ |
| `garment_subcontract` | Gia công: gửi/nhận gia công, quản lý đối tác | 18 ✅ |

### Pha 6 — Hoàn Thiện Hệ Thống

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_finishing` | Tổ hoàn thiện: cắt chỉ, ủi, gấp, đóng tag, QC | 7 ✅ |
| `garment_hr` | Nhân sự: quản lý nhân viên may, chấm công, phòng ban, kỹ năng, nghỉ phép | 29 ✅ |
| `garment_accounting` | Kế toán VN: thuế GTGT, hóa đơn, công nợ, BHXH/BHYT | 9 ✅ |
| `garment_warehouse` | Kho: NPL, bán thành phẩm, thành phẩm, xuất/nhập/chuyển | 15 ✅ |
| `garment_delivery` | Giao hàng: phương tiện, tài xế, đơn giao hàng | 11 ✅ |

### Pha 7 — Nhập NL & Dashboard

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_material` | Nhập NL mua hàng, NL khách gửi (CMT), phân bổ NL cho SX | 16 ✅ |
| `garment_dashboard` | Dashboard KPI, tổng quan đơn hàng, tiến độ SX, cảnh báo | 12 ✅ |

### Pha 8 — CRM, Tem/Pallet & Kiểm Kê Kho

| Module | Mô tả | Tests |
|--------|--------|:-----:|
| `garment_crm` | CRM: lead/opportunity, phản hồi khách hàng, hồ sơ buyer | 30 ✅ |
| `garment_label` | In tem QR code, quản lý pallet, đóng tách thùng/pallet | 39 ✅ |
| `garment_inventory` | Kiểm kê kho: phiên kiểm kê, quét QR, điều chỉnh tự động | 21 ✅ |

### Module Phụ Trợ

| Module | Mô tả |
|--------|--------|
| `garment_demo` | Dữ liệu mẫu cho toàn bộ hệ thống |

> **Tổng cộng: 214 tests ✅ — 0 failed, 0 errors — 25 module**

## 🔐 Phân Quyền 4 Cấp

| Cấp | Nhóm | Quyền |
|-----|------|-------|
| 1 | **Nhân Viên (User)** | Xem tất cả, tạo/sửa dữ liệu liên quan |
| 2 | **Tổ Trưởng (Team Leader)** | + Quản lý nhóm/tổ, duyệt sản lượng |
| 3 | **Trưởng Phòng (Dept Manager)** | + Quản lý phòng ban, duyệt nghỉ phép |
| 4 | **Quản Lý (Manager)** | Toàn quyền: tạo, sửa, xóa tất cả |

## 🔧 Cấu hình sau cài đặt

1. Truy cập `http://localhost:8069`
2. Đăng nhập: `admin` / `admin` (database: `garment_db`)
3. Vào **Apps** → Tìm "Garment" → Cài đặt các module
4. Vào **Settings** → Cài ngôn ngữ Tiếng Việt (nếu cần)
5. Cấu hình thông tin công ty

## 📁 Cấu trúc thư mục

```
odoo-garment-project/
├── odoo/                          # Odoo 19.0 source code
├── custom-addons/                 # 25 module tùy chỉnh
│   ├── garment_base/              # Vải, phụ liệu, style, đơn hàng
│   ├── garment_production/        # Chuyền may, lệnh SX, sản lượng
│   ├── garment_quality/           # QC, loại lỗi, AQL
│   ├── garment_costing/           # Tính giá thành
│   ├── garment_sample/            # Quản lý mẫu
│   ├── garment_cutting/           # Cắt nâng cao
│   ├── garment_packing/           # Đóng gói & xuất hàng
│   ├── garment_report/            # Báo cáo, SQL views
│   ├── garment_planning/          # Kế hoạch SX
│   ├── garment_maintenance/       # Bảo trì máy
│   ├── garment_payroll/           # Lương khoán
│   ├── garment_compliance/        # Tuân thủ
│   ├── garment_washing/           # Xưởng giặt
│   ├── garment_subcontract/       # Gia công
│   ├── garment_finishing/         # Hoàn thiện
│   ├── garment_hr/                # Nhân sự, nhân viên may, chấm công
│   ├── garment_accounting/        # Kế toán VN
│   ├── garment_warehouse/         # Quản lý kho
│   ├── garment_delivery/          # Giao hàng
│   ├── garment_material/          # Nhập nguyên liệu
│   ├── garment_dashboard/         # Dashboard tổng quan
│   ├── garment_crm/               # CRM khách hàng
│   ├── garment_label/             # In tem & quản lý pallet
│   ├── garment_inventory/         # Kiểm kê kho
│   └── garment_demo/              # Dữ liệu mẫu
├── docker-compose.yml
├── odoo.conf
├── docs/
│   ├── USER_GUIDE.md              # Hướng dẫn sử dụng (~2100 dòng)
│   ├── QUICK_START.md             # Hướng dẫn nhanh
│   └── images/                    # 113 screenshots
├── PROJECT_PLAN.md
└── README.md
```

## 🧪 Chạy Tests

```bash
# Test tất cả module
docker exec garment_odoo odoo -d garment_db --test-enable \
  --test-tags garment_base,garment_production,garment_quality,garment_costing,garment_sample,garment_cutting,garment_packing,garment_planning,garment_maintenance,garment_payroll,garment_compliance,garment_report,garment_washing,garment_subcontract,garment_finishing,garment_hr,garment_accounting,garment_warehouse,garment_delivery,garment_crm,garment_label,garment_inventory,garment_dashboard \
  -u garment_base --stop-after-init --no-http

# Test một module cụ thể
docker exec garment_odoo odoo -d garment_db --test-enable \
  --test-tags garment_crm -u garment_crm --stop-after-init --no-http
```

## 📖 Tài Liệu

| Tài liệu | Mô tả |
|-----------|-------|
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Hướng dẫn sử dụng chi tiết (~2100 dòng), 28 chương |
| [QUICK_START.md](docs/QUICK_START.md) | Hướng dẫn nhanh, tóm tắt chức năng |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | Kế hoạch dự án |

## 📸 Screenshots

Hệ thống có **113 screenshots** trong thư mục `docs/images/`, bao gồm:

- Quản lý đơn hàng, style, vải, phụ liệu
- Sản xuất, cắt, chuyền may, sản lượng
- Chất lượng QC, compliance
- Kho, nhập NL, giao hàng
- CRM: lead, buyer, phản hồi
- In tem QR, thùng hàng, pallet
- Kiểm kê kho, phiên kiểm kê
- Nhân viên may, kỹ năng, phân quyền
- Dashboard, báo cáo, kế toán

## 📄 License

Dự án sử dụng **LGPL-3** license, phù hợp với Odoo Community Edition.

---

> 📞 **Hỗ trợ:** Liên hệ đội phát triển
> 📚 **Odoo Docs:** https://www.odoo.com/documentation/19.0/