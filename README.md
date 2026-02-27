# 🧵 Odoo 19 - Hệ Thống Quản Lý Công Ty May# 🧵 Odoo 19 - Hệ Thống Quản Lý Công Ty May# 🧵 Odoo 19 - Hệ Thống Quản Lý Công Ty May# 🧵 Odoo 19 - Hệ Thống Quản Lý Công Ty May# 🧵 Odoo 19 - Hệ Thống Quản Lý Công Ty May



Dự án ERP sử dụng **Odoo 19.0 Community Edition** được tùy chỉnh cho ngành **may mặc (Garment Manufacturing)**, bao gồm **22 module chuyên biệt** bao phủ toàn bộ quy trình từ nhận đơn hàng đến xuất hàng, bao gồm nhập nguyên liệu, hoàn thiện, chấm công, kế toán, kho, giặt, gia công, vận chuyển và dashboard tổng quan.



## 📋 Yêu cầuDự án ERP sử dụng **Odoo 19.0 Community Edition** được tùy chỉnh cho ngành **may mặc (Garment Manufacturing)**, bao gồm **20 module chuyên biệt** bao phủ toàn bộ quy trình từ nhận đơn hàng đến xuất hàng, bao gồm hoàn thiện, chấm công, kế toán, kho, giặt, gia công, vận chuyển.



- **Docker & Docker Compose** (Khuyến nghị)

- Hoặc: Python 3.10+, PostgreSQL 16+, Node.js 18+

## 📋 Yêu cầuDự án ERP sử dụng **Odoo 19.0 Community Edition** được tùy chỉnh cho ngành **may mặc (Garment Manufacturing)**, bao gồm 14 module chuyên biệt bao phủ toàn bộ quy trình từ nhận đơn hàng đến xuất hàng, bao gồm xưởng giặt và gia công.

## 🚀 Cài đặt & Khởi động



### Sử dụng Docker (Khuyến nghị)

- Python 3.10+

```bash

cd odoo-garment-project- PostgreSQL 16+

docker compose up -d

- Node.js 18+ (cho Odoo web assets)## 📋 Yêu cầuDự án ERP sử dụng **Odoo 19.0 Community Edition** được tùy chỉnh cho ngành **may mặc (Garment Manufacturing)**, bao gồm 12 module chuyên biệt bao phủ toàn bộ quy trình từ nhận đơn hàng đến xuất hàng.Dự án ERP sử dụng Odoo 19.0 được tùy chỉnh cho ngành may mặc (Garment Manufacturing).

# Truy cập: http://localhost:8069

# Đăng nhập: admin / admin (database: garment_db)- Hoặc **Docker & Docker Compose** (Khuyến nghị)

```



### Cài đặt thủ công trên macOS

## 🚀 Cài đặt & Khởi động

```bash

brew install postgresql@16- Python 3.10+

brew services start postgresql@16

createuser -s odoo### Sử dụng Docker (Khuyến nghị)

cd odoo-garment-project/odoo

pip install -r requirements.txt- PostgreSQL 16+

python odoo-bin -c ../odoo.conf

``````bash



## 📦 Custom Modules (22 Module)cd odoo-garment-project- Node.js 18+ (cho Odoo web assets)## 📋 Yêu cầu## 📋 Yêu cầu



### Pha 1 — Nền Tảng Cơ Sởdocker compose up -d



| Module | Mô tả | Tests |- Hoặc **Docker & Docker Compose** (Khuyến nghị)

|--------|--------|:-----:|

| `garment_base` | Module cơ sở: vải, phụ liệu, mẫu may, đơn hàng, ký hiệu giặt ủi | — |# Truy cập: http://localhost:8069

| `garment_production` | Sản xuất: chuyền may, lệnh SX, lệnh cắt, sản lượng, tiến độ | — |

| `garment_quality` | Chất lượng: QC inline/endline/final, AQL, phân loại lỗi | — |# Đăng nhập: admin / admin (database: garment_db)



### Pha 2 — Module Chuyên Sâu```



| Module | Mô tả | Tests |## 🚀 Cài đặt & Khởi động

|--------|--------|:-----:|

| `garment_costing` | Tính giá thành FOB/CM/CMT, BOM integration | 8 ✅ |### Cài đặt thủ công trên macOS

| `garment_sample` | Quản lý mẫu may: Proto, Fit, PP, TOP, revision | 12 ✅ |

| `garment_cutting` | Cắt nâng cao: marker, trải vải, bó hàng | 9 ✅ |- Python 3.10+- Python 3.10+

| `garment_packing` | Đóng gói: packing list, carton, shipping | 10 ✅ |

```bash

### Pha 3 — Báo Cáo & Phân Tích

brew install postgresql@16### Cách 1: Sử dụng Docker (Khuyến nghị)

| Module | Mô tả | Tests |

|--------|--------|:-----:|brew services start postgresql@16

| `garment_report` | Hiệu suất chuyền (SQL view), phân tích lỗi, wizard báo cáo | — |

createuser -s odoo- PostgreSQL 16+- PostgreSQL 15+

### Pha 4 — Tối Ưu & Nâng Cao

cd odoo-garment-project/odoo

| Module | Mô tả | Tests |

|--------|--------|:-----:|pip install -r requirements.txt```bash

| `garment_planning` | Kế hoạch SX: phân chuyền, auto-schedule | 8 ✅ |

| `garment_maintenance` | Bảo trì máy may: lịch định kỳ, sửa chữa, downtime | 11 ✅ |python odoo-bin -c ../odoo.conf

| `garment_payroll` | Lương khoán: piece rate, sản lượng, BHXH/BHYT, thưởng | 9 ✅ |

| `garment_compliance` | Tuân thủ: audit BSCI/WRAP/SA8000, CAP | 14 ✅ |```# Clone project- Node.js 18+ (cho Odoo web assets)- Node.js 18+ (cho Odoo web assets)



### Pha 5 — Xưởng Giặt & Gia Công



| Module | Mô tả | Tests |## 📦 Custom Modules (20 Module)cd odoo-garment-project

|--------|--------|:-----:|

| `garment_washing` | Xưởng giặt: hóa chất, công thức, đơn giặt | 24 ✅ |

| `garment_subcontract` | Gia công: gửi/nhận gia công, quản lý đối tác | 18 ✅ |

### Pha 1 — Nền Tảng Cơ Sở- Hoặc **Docker & Docker Compose** (Khuyến nghị)- Hoặc Docker & Docker Compose

### Pha 6 — Hoàn Thiện Hệ Thống



| Module | Mô tả | Tests |

|--------|--------|:-----:|| Module | Mô tả | Tests |# Khởi động

| `garment_finishing` | Tổ hoàn thiện: cắt chỉ, ủi, gấp, đóng tag, QC | 7 ✅ |

| `garment_hr` | Nhân sự: chấm công, phòng ban, tay nghề, nghỉ phép | 16 ✅ ||--------|--------|:-----:|

| `garment_accounting` | Kế toán VN: thuế GTGT, hóa đơn, công nợ, BHXH/BHYT | 9 ✅ |

| `garment_warehouse` | Kho: NPL, bán thành phẩm, thành phẩm, xuất/nhập/chuyển | 15 ✅ || `garment_base` | Module cơ sở: vải, phụ liệu, mẫu may, đơn hàng, ký hiệu giặt ủi | — |docker compose up -d

| `garment_delivery` | Giao hàng: phương tiện, tài xế, đơn giao hàng | 11 ✅ |

| `garment_production` | Sản xuất: chuyền may, lệnh SX, lệnh cắt, sản lượng, tiến độ | — |

### Pha 7 — Nhập NL & Dashboard

| `garment_quality` | Chất lượng: QC inline/endline/final, AQL, phân loại lỗi | — |

| Module | Mô tả | Tests |

|--------|--------|:-----:|

| `garment_material` | Nhập NL mua hàng, NL khách gửi (CMT), phân bổ NL cho SX | 16 ✅ |

| `garment_dashboard` | Dashboard KPI, tổng quan đơn hàng, tiến độ SX, cảnh báo | 10 ✅ |### Pha 2 — Module Chuyên Sâu# Truy cập: http://localhost:8069## 🚀 Cài đặt & Khởi động## 🚀 Cài đặt



### Module Phụ Trợ



| Module | Mô tả || Module | Mô tả | Tests |# Đăng nhập: admin / admin

|--------|--------|

| `garment_demo` | Dữ liệu mẫu cho toàn bộ hệ thống ||--------|--------|:-----:|



> **Tổng cộng: 139 post-tests ✅ — 0 failed, 0 errors — 17 module có tests**| `garment_costing` | Tính giá thành FOB/CM/CMT, BOM integration | 8 ✅ |```



## 🔧 Cấu hình sau cài đặt| `garment_sample` | Quản lý mẫu may: Proto, Fit, PP, TOP, revision | 12 ✅ |



1. Truy cập `http://localhost:8069`| `garment_cutting` | Cắt nâng cao: marker, trải vải, bó hàng | 9 ✅ |

2. Đăng nhập: `admin` / `admin` (database: `garment_db`)

3. Vào **Apps** → Tìm "Garment" → Cài đặt các module| `garment_packing` | Đóng gói: packing list, carton, shipping | 10 ✅ |

4. Vào **Settings** → Cài ngôn ngữ Tiếng Việt (nếu cần)

5. Cấu hình thông tin công ty### Cách 2: Cài đặt thủ công trên macOS### Cách 1: Sử dụng Docker (Khuyến nghị)### Cách 1: Sử dụng Docker (Khuyến nghị)



## 📁 Cấu trúc thư mục### Pha 3 — Báo Cáo & Phân Tích



```

odoo-garment-project/

├── odoo/                          # Odoo 19.0 source code| Module | Mô tả | Tests |

├── custom-addons/                 # 22 module tùy chỉnh

│   ├── garment_base/              # Vải, phụ liệu, style, đơn hàng|--------|--------|:-----:|```bash

│   ├── garment_production/        # Chuyền may, lệnh SX, sản lượng

│   ├── garment_quality/           # QC, loại lỗi, AQL| `garment_report` | Hiệu suất chuyền (SQL view), phân tích lỗi, wizard báo cáo | — |

│   ├── garment_costing/           # Tính giá thành

│   ├── garment_sample/            # Quản lý mẫu# 1. Cài PostgreSQL

│   ├── garment_cutting/           # Cắt nâng cao

│   ├── garment_packing/           # Đóng gói & xuất hàng### Pha 4 — Tối Ưu & Nâng Cao

│   ├── garment_report/            # Báo cáo, SQL views

│   ├── garment_planning/          # Kế hoạch SXbrew install postgresql@16```bash```bash

│   ├── garment_maintenance/       # Bảo trì máy

│   ├── garment_payroll/           # Lương khoán| Module | Mô tả | Tests |

│   ├── garment_compliance/        # Tuân thủ

│   ├── garment_washing/           # Xưởng giặt|--------|--------|:-----:|brew services start postgresql@16

│   ├── garment_subcontract/       # Gia công

│   ├── garment_finishing/         # Hoàn thiện| `garment_planning` | Kế hoạch SX: phân chuyền, auto-schedule | 8 ✅ |

│   ├── garment_hr/                # Nhân sự & chấm công

│   ├── garment_accounting/        # Kế toán VN| `garment_maintenance` | Bảo trì máy may: lịch định kỳ, sửa chữa, downtime | 11 ✅ |# Clone project# Clone project

│   ├── garment_warehouse/         # Quản lý kho

│   ├── garment_delivery/          # Giao hàng| `garment_payroll` | Lương khoán: piece rate, sản lượng, BHXH/BHYT, thưởng quý/năm | 9 ✅ |

│   ├── garment_material/          # Nhập nguyên liệu

│   ├── garment_dashboard/         # Dashboard tổng quan| `garment_compliance` | Tuân thủ: audit BSCI/WRAP/SA8000, CAP | 14 ✅ |# 2. Tạo user PostgreSQL

│   └── garment_demo/              # Dữ liệu mẫu

├── docker-compose.yml

├── odoo.conf

├── docs/### Pha 5 — Xưởng Giặt & Gia Côngcreateuser -s odoocd odoo-garment-projectcd odoo-garment-project

│   ├── USER_GUIDE.md              # Hướng dẫn sử dụng (1800+ dòng)

│   ├── QUICK_START.md             # Hướng dẫn nhanh

│   └── images/                    # 85 screenshots

├── PROJECT_PLAN.md| Module | Mô tả | Tests |

└── README.md

```|--------|--------|:-----:|



## 🔄 Quy trình Nghiệp Vụ Chính| `garment_washing` | Xưởng giặt: hóa chất, công thức, đơn giặt (nội bộ/ngoài/nhận) | 24 ✅ |# 3. Cài Python dependencies



```| `garment_subcontract` | Gia công: gửi/nhận gia công, quản lý đối tác | 18 ✅ |

Nhận PO Khách Hàng → Làm Mẫu (Sample) → Tính Giá (Costing)

    ↓cd odoo-garment-project/odoo

Xác Nhận Đơn Hàng → Lên Kế Hoạch SX (Planning)

    ↓### Pha 6 — Hoàn Thiện Hệ Thống

Nhập Nguyên Liệu (Mua / Khách Gửi CMT) → Kiểm Tra QC NL → Phân Bổ NL

    ↓pip install -r requirements.txt# Khởi động# Khởi động

Lên Sơ Đồ Cắt (Marker) → Trải Vải → Cắt → Đánh Số Bó

    ↓| Module | Mô tả | Tests |

Phân Chuyền May → Sản Xuất → QC Inline → QC Endline

    ↓                           ↓|--------|--------|:-----:|

    ↓                     Gửi Gia Công (nếu cần)

    ↓                           ↓| `garment_finishing` | Tổ hoàn thiện: cắt chỉ, ủi, gấp, đóng tag, QC | 7 ✅ |

Hoàn Thiện (Cắt Chỉ, Ủi) → Xưởng Giặt → QC Final → AQL Inspection

    ↓| `garment_hr` | Nhân sự: chấm công, phòng ban, tay nghề, nghỉ phép | 16 ✅ |# 4. Chạy Odoodocker compose up -ddocker-compose up -d

Đóng Gói (Packing List) → Xuất Hàng (Shipping) → Hoàn Thành

    ↓| `garment_accounting` | Kế toán VN: thuế GTGT, hóa đơn, công nợ, BHXH/BHYT/BHTN | 9 ✅ |

Dashboard: Theo dõi KPI, tiến độ, cảnh báo trễ hạn

```| `garment_warehouse` | Kho: NPL, bán thành phẩm, thành phẩm, xuất/nhập/chuyển | 15 ✅ |python odoo-bin -c ../odoo.conf



## 📊 Tính năng nổi bật| `garment_delivery` | Giao hàng: phương tiện, tài xế, đơn giao hàng | 11 ✅ |



| Tính năng | Chi tiết || `garment_demo` | Dữ liệu mẫu cho toàn bộ hệ thống | — |```

|-----------|----------|

| **Quản lý vải & phụ liệu** | Theo loại, thành phần, khổ vải, định lượng, nhà cung cấp |

| **Mẫu may / Style** | Tech pack, rập, SAM, ký hiệu giặt ủi, size & màu |

| **Đơn hàng may** | FOB/CIF, PO khách hàng, size-color matrix, tiến độ |> **Tổng cộng: 181 tests ✅ — 0 failed, 0 errors — 15 module có tests**

| **Nhập nguyên liệu** | Mua hàng, khách gửi CMT, QC NL, phân bổ cho SX |

| **Kế hoạch sản xuất** | Phân chuyền tự động, năng suất/ngày, ước tính kết thúc |

| **Sản xuất** | Chuyền may, lệnh SX, sản lượng ngày, hiệu suất |

| **Cắt nâng cao** | Marker, trải vải, bó hàng, hao hụt |## 🔧 Cấu hình sau cài đặt## 📦 Custom Modules (14 Module)# Truy cập: http://localhost:8069# Truy cập: http://localhost:8069

| **Kiểm tra chất lượng** | QC inline/endline/final, AQL, phân loại lỗi |

| **Tính giá thành** | FOB/CM/CMT, chi phí vải/phụ liệu/nhân công/profit |

| **Đóng gói** | Packing list, thùng carton, CBM, B/L |

| **Bảo trì máy** | 10 loại máy, lịch bảo trì, sửa chữa, downtime |1. Truy cập `http://localhost:8069`

| **Lương khoán** | Đơn giá, sản lượng cá nhân, OT, BHXH/BHYT |

| **Tuân thủ** | Audit BSCI/WRAP/SA8000/ISO, CAP, xếp hạng |2. Đăng nhập: `admin` / `admin` (database: `garment_db`)

| **Dashboard** | KPI tổng quan, tiến độ SX, đơn trễ hạn, tỷ lệ lỗi |

| **Xưởng giặt** | Hóa chất, công thức giặt, đơn giặt, QC giặt |3. Vào **Apps** → Tìm "Garment" → Cài đặt các module### Pha 1 — Nền Tảng Cơ Sở# Đăng nhập: admin / admin```

| **Gia công** | Gửi/nhận gia công, theo dõi tiến độ, đánh giá đối tác |

4. Vào **Settings** → Cài ngôn ngữ Tiếng Việt (nếu cần)

## 📖 Tài liệu

5. Cấu hình thông tin công ty

- 📖 [Hướng dẫn sử dụng chi tiết](./docs/USER_GUIDE.md) — 1800+ dòng, 85 screenshots

- 🚀 [Hướng dẫn nhanh](./docs/QUICK_START.md) — tóm tắt các thao tác chính

- 📋 [Kế hoạch triển khai](./PROJECT_PLAN.md)

- 📚 [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)### Thứ tự cài đặt (tự động xử lý dependencies):| Module | Mô tả | Tests | Trạng thái |```



## 📄 License1. `garment_base` (module cơ sở)



- Odoo Community: LGPL-3.02. `garment_production` → `garment_quality` → `garment_report`|--------|--------|:-----:|:---------:|

- Custom Modules: LGPL-3.0

3. `garment_costing`, `garment_sample`, `garment_cutting`, `garment_packing`

4. `garment_planning`, `garment_maintenance`, `garment_payroll`, `garment_compliance`| `garment_base` | Module cơ sở: vải, phụ liệu, mẫu may, đơn hàng, ký hiệu giặt ủi | — | ✅ |### Cách 2: Cài đặt thủ công trên macOS

5. `garment_washing`, `garment_subcontract`, `garment_finishing`

6. `garment_hr`, `garment_accounting`, `garment_warehouse`, `garment_delivery`| `garment_production` | Sản xuất: chuyền may, lệnh SX, lệnh cắt, sản lượng, tiến độ đơn hàng | — | ✅ |

7. `garment_demo` (dữ liệu mẫu - cài cuối cùng)

| `garment_quality` | Chất lượng: QC inline/endline/final, AQL, phân loại lỗi | — | ✅ |### Cách 2: Cài đặt thủ công trên macOS

## 🔄 Quy trình Nghiệp Vụ Chính



```

Nhận PO Khách Hàng → Làm Mẫu (Sample) → Tính Giá (Costing)### Pha 2 — Module Chuyên Sâu```bash

    ↓

Xác Nhận Đơn Hàng → Lên Kế Hoạch SX (Planning)

    ↓

Nhập Kho NPL (Warehouse) → Kiểm Vải → Xuất Kho Cắt| Module | Mô tả | Tests | Trạng thái |```bash# 1. Cài PostgreSQL

    ↓

Cắt (Marker → Trải Vải → Cắt → Bó Hàng)|--------|--------|:-----:|:---------:|

    ↓

Phân Chuyền May → Sản Xuất → QC Inline → QC Endline| `garment_costing` | Tính giá thành FOB/CM/CMT, BOM integration | 8 ✅ | ✅ |# 1. Cài PostgreSQLbrew install postgresql@16

    ↓                           ↓

    ↓                     Gửi Gia Công (nếu cần)| `garment_sample` | Quản lý mẫu may: Proto, Fit, PP, TOP, revision | 12 ✅ | ✅ |

    ↓                           ↓

Hoàn Thiện (Cắt Chỉ → Ủi → Gấp → Đóng Tag)| `garment_cutting` | Cắt nâng cao: marker, trải vải, bó hàng | 9 ✅ | ✅ |brew install postgresql@16brew services start postgresql@16

    ↓

Xưởng Giặt (nếu cần) → QC Final → AQL Inspection| `garment_packing` | Đóng gói: packing list, carton, shipping | 10 ✅ | ✅ |

    ↓

Đóng Gói (Packing List → Carton) → Nhập Kho Thành Phẩmbrew services start postgresql@16

    ↓

Giao Hàng (Xe Tải / Container) → Xuất Hóa Đơn → Hoàn Thành### Pha 3 — Báo Cáo & Phân Tích

```

# 2. Tạo user PostgreSQL

## 📊 Tính năng nổi bật

| Module | Mô tả | Tests | Trạng thái |

| Tính năng | Chi tiết |

|-----------|----------||--------|--------|:-----:|:---------:|# 2. Tạo user PostgreSQLcreateuser -s odoo

| **Quản lý vải & phụ liệu** | Theo loại, thành phần, khổ vải, định lượng, nhà cung cấp, giá |

| **Mẫu may / Style** | Tech pack, rập, hình ảnh, SAM, ký hiệu giặt ủi, size & màu || `garment_report` | Hiệu suất chuyền (SQL view), phân tích lỗi, wizard báo cáo | — | ✅ |

| **Đơn hàng may** | FOB/CIF, PO khách hàng, size-color matrix, tiến độ sản xuất |

| **Kế hoạch sản xuất** | Phân chuyền tự động, năng suất/ngày, ước tính ngày kết thúc |createuser -s odoo

| **Sản xuất** | Chuyền may, lệnh SX, sản lượng ngày theo ca, hiệu suất |

| **Cắt nâng cao** | Marker, trải vải (lớp), bó hàng, phát xuống chuyền, hao hụt |### Pha 4 — Tối Ưu & Nâng Cao

| **Hoàn thiện** | Cắt chỉ, ủi, gấp xếp, đóng tag/nhãn, QC hoàn thiện |

| **Kiểm tra chất lượng** | QC inline/endline/final, AQL, phân loại lỗi, tỷ lệ lỗi |# 3. Cài Python dependencies

| **Tính giá thành** | FOB/CM/CMT, chi phí vải/phụ liệu/nhân công/overhead/profit |

| **Quản lý mẫu** | 8 loại mẫu, workflow duyệt, comment khách hàng, revision || Module | Mô tả | Tests | Trạng thái |

| **Đóng gói** | Packing list, thùng carton, CBM, gross/net weight, B/L |

| **Bảo trì máy** | 10 loại máy, lịch bảo trì, sửa chữa, downtime tracking ||--------|--------|:-----:|:---------:|# 3. Cài Python dependenciescd odoo-garment-project/odoo

| **Nhân sự & chấm công** | Phòng ban/tổ, chấm công ngày, nghỉ phép, tay nghề |

| **Lương khoán** | Đơn giá SP, sản lượng cá nhân, OT, BHXH/BHYT, thưởng quý/năm || `garment_planning` | Kế hoạch SX: phân chuyền, auto-schedule | 8 ✅ | ✅ |

| **Kế toán VN** | Hóa đơn GTGT, thuế 10%, công nợ KH/NCC, mục kế toán may |

| **Quản lý kho** | Kho NPL/BTP/TP, phiếu nhập/xuất/chuyển kho || `garment_maintenance` | Bảo trì máy may: lịch định kỳ, sửa chữa, theo dõi downtime | 11 ✅ | ✅ |cd odoo-garment-project/odoopip install -r requirements.txt

| **Xưởng giặt** | Hóa chất, công thức giặt, đơn giặt nội bộ/ngoài, QC giặt |

| **Gia công** | Gửi/nhận gia công, theo dõi tiến độ, đánh giá đối tác || `garment_payroll` | Lương khoán: piece rate, sản lượng cá nhân, tính lương tháng | 9 ✅ | ✅ |

| **Giao hàng** | Phương tiện, tài xế, đơn giao hàng, tuyến đường |

| **Tuân thủ** | Audit BSCI/WRAP/SA8000/ISO, phát hiện, CAP, xếp hạng || `garment_compliance` | Tuân thủ: audit BSCI/WRAP/SA8000, CAP, tìm kiếm phát hiện | 14 ✅ | ✅ |pip install -r requirements.txt

| **Báo cáo** | Hiệu suất chuyền (pivot/graph), phân tích lỗi, wizard |

| **Dữ liệu mẫu** | Demo data đầy đủ cho tất cả module, sẵn sàng trải nghiệm |



## 📁 Cấu trúc thư mục### Pha 5 — Xưởng Giặt & Gia Công# 4. Chạy Odoo



```

odoo-garment-project/

├── odoo/                          # Odoo 19.0 source code| Module | Mô tả | Tests | Trạng thái |# 4. Chạy Odoopython odoo-bin -c ../odoo.conf

├── custom-addons/                 # 20 module tùy chỉnh

│   ├── garment_base/              # Vải, phụ liệu, style, đơn hàng, wash symbol|--------|--------|:-----:|:---------:|

│   ├── garment_production/        # Chuyền may, lệnh SX, cắt, sản lượng

│   ├── garment_quality/           # Loại lỗi, phiếu QC, AQL| `garment_washing` | Xưởng giặt: hóa chất, công thức giặt, đơn giặt (nội bộ/bên ngoài/nhận giặt) | 24 ✅ | ✅ |python odoo-bin -c ../odoo.conf```

│   ├── garment_costing/           # Phiếu giá thành, dòng chi phí

│   ├── garment_sample/            # Mẫu may, comment khách hàng| `garment_subcontract` | Gia công: gửi hàng đi gia công, nhận hàng gia công, quản lý đối tác gia công | 18 ✅ | ✅ |

│   ├── garment_cutting/           # Lệnh cắt, lớp vải, bó hàng

│   ├── garment_packing/           # Packing list, carton```

│   ├── garment_report/            # SQL views, wizard báo cáo

│   ├── garment_planning/          # Kế hoạch SX, phân chuyền> **Tổng cộng: 123 tests ✅ — 0 failed, 0 errors**

│   ├── garment_maintenance/       # Máy may, yêu cầu bảo trì

│   ├── garment_payroll/           # Đơn giá, sản lượng, tính lương, thưởng### Cách 3: Cài đặt trên Ubuntu/Debian

│   ├── garment_compliance/        # Audit, CAP, corrective action

│   ├── garment_washing/           # Hóa chất, công thức giặt, đơn giặt## 🔧 Cấu hình sau cài đặt

│   ├── garment_subcontract/       # Đơn gia công, đối tác

│   ├── garment_finishing/         # Lệnh hoàn thiện, công đoạn## 📦 Custom Modules (12 Module)

│   ├── garment_hr/                # Chấm công, phòng ban, nghỉ phép, tay nghề

│   ├── garment_accounting/        # Hóa đơn, thuế GTGT, mục kế toán1. Truy cập `http://localhost:8069`

│   ├── garment_warehouse/         # Phiếu kho, dòng chi tiết

│   ├── garment_delivery/          # Phương tiện, đơn giao hàng2. Đăng nhập: `admin` / `admin` (database: `garment_db`)```bash

│   └── garment_demo/              # Dữ liệu mẫu

├── docker-compose.yml3. Vào **Apps** → Tìm "Garment" → Cài đặt các module

├── odoo.conf

├── docs/USER_GUIDE.md4. Vào **Settings** → Cài ngôn ngữ Tiếng Việt (nếu cần)### Pha 1 — Nền Tảng Cơ Sở# 1. Cài đặt dependencies

├── PROJECT_PLAN.md

└── README.md5. Cấu hình thông tin công ty

```

sudo apt update

## 📖 Tài liệu

### Thứ tự cài đặt module (tự động xử lý dependencies):

- [Tài liệu hướng dẫn sử dụng](./docs/USER_GUIDE.md)

- [Kế hoạch triển khai](./PROJECT_PLAN.md)1. `garment_base` (cài trước — module cơ sở)| Module | Mô tả | Tests | Trạng thái |sudo apt install python3-pip python3-dev python3-venv \

- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)

2. `garment_production` → `garment_quality` → `garment_report`

## 📄 License

3. `garment_costing`, `garment_sample`, `garment_cutting`, `garment_packing`|--------|--------|:-----:|:---------:|    postgresql postgresql-client \

- Odoo Community: LGPL-3.0

- Custom Modules: LGPL-3.04. `garment_planning`, `garment_maintenance`, `garment_payroll`, `garment_compliance`


5. `garment_washing`, `garment_subcontract`| `garment_base` | Module cơ sở: vải, phụ liệu, mẫu may, đơn hàng, ký hiệu giặt ủi | — | ✅ |    libxml2-dev libxslt1-dev zlib1g-dev \



## 📁 Cấu trúc thư mục| `garment_production` | Sản xuất: chuyền may, lệnh SX, lệnh cắt, sản lượng, tiến độ đơn hàng | — | ✅ |    libsasl2-dev libldap2-dev \



```| `garment_quality` | Chất lượng: QC inline/endline/final, AQL, phân loại lỗi | — | ✅ |    build-essential libffi-dev

odoo-garment-project/

├── odoo/                          # Odoo 19.0 source code

│   ├── addons/                    # Odoo standard addons

│   └── odoo/                      # Odoo core### Pha 2 — Module Chuyên Sâu# 2. Tạo database user

├── custom-addons/                 # 14 module tùy chỉnh

│   ├── garment_base/              # ✅ Module cơ sởsudo -u postgres createuser -s odoo

│   │   └── models/                #    fabric, accessory, style, color, size, order, wash_symbol

│   ├── garment_production/        # ✅ Sản xuất| Module | Mô tả | Tests | Trạng thái |

│   │   └── models/                #    sewing_line, production_order, cutting_order, daily_output

│   ├── garment_quality/           # ✅ Chất lượng|--------|--------|:-----:|:---------:|# 3. Cài Python packages

│   │   └── models/                #    defect_type, qc_inspection

│   ├── garment_costing/           # ✅ Tính giá thành| `garment_costing` | Tính giá thành FOB/CM/CMT, BOM integration | 8 ✅ | ✅ |cd odoo-garment-project/odoo

│   │   └── models/                #    cost_sheet, cost_line

│   ├── garment_sample/            # ✅ Quản lý mẫu| `garment_sample` | Quản lý mẫu may: Proto, Fit, PP, TOP, revision | 12 ✅ | ✅ |pip3 install -r requirements.txt

│   │   └── models/                #    garment_sample (+ sample_comment)

│   ├── garment_cutting/           # ✅ Cắt nâng cao| `garment_cutting` | Cắt nâng cao: marker, trải vải, bó hàng | 9 ✅ | ✅ |

│   │   └── models/                #    cutting_order, cutting_layer, cutting_bundle

│   ├── garment_packing/           # ✅ Đóng gói & xuất hàng| `garment_packing` | Đóng gói: packing list, carton, shipping | 10 ✅ | ✅ |# 4. Chạy Odoo

│   │   └── models/                #    packing_list, carton_line

│   ├── garment_report/            # ✅ Báo cáopython3 odoo-bin -c ../odoo.conf

│   │   ├── models/                #    efficiency_analysis, defect_analysis (SQL views)

│   │   └── report/                #    production_report (wizard)### Pha 3 — Báo Cáo & Phân Tích```

│   ├── garment_planning/          # ✅ Kế hoạch sản xuất

│   │   └── models/                #    production_plan, line_loading

│   ├── garment_maintenance/       # ✅ Bảo trì máy

│   │   └── models/                #    machine, maintenance_request| Module | Mô tả | Tests | Trạng thái |## 📦 Custom Modules

│   ├── garment_payroll/           # ✅ Lương khoán

│   │   └── models/                #    piece_rate, worker_output, wage_calculation|--------|--------|:-----:|:---------:|

│   ├── garment_compliance/        # ✅ Tuân thủ

│   │   └── models/                #    compliance_audit, corrective_action| `garment_report` | Hiệu suất chuyền (SQL view), phân tích lỗi, wizard báo cáo | — | ✅ || Module | Mô tả | Trạng thái |

│   ├── garment_washing/           # ✅ Xưởng giặt

│   │   └── models/                #    wash_chemical, wash_recipe, wash_order|--------|--------|-----------|

│   └── garment_subcontract/       # ✅ Gia công

│       └── models/                #    subcontract_order, subcontract_partner (res.partner inherit)### Pha 4 — Tối Ưu & Nâng Cao| `garment_base` | Module cơ sở: vải, phụ liệu, mẫu may, đơn hàng | ✅ Sẵn sàng |

├── docker-compose.yml             # Docker setup

├── odoo.conf                      # Cấu hình Odoo| `garment_production` | Sản xuất: chuyền may, lệnh SX, lệnh cắt, sản lượng | ✅ Sẵn sàng |

├── docs/                          # Tài liệu hướng dẫn

├── PROJECT_PLAN.md                # Kế hoạch chi tiết| Module | Mô tả | Tests | Trạng thái || `garment_quality` | Chất lượng: QC inline/final, AQL, loại lỗi | ✅ Sẵn sàng |

└── README.md                      # File này

```|--------|--------|:-----:|:---------:|| `garment_costing` | Tính giá thành FOB/CM/CMT | 📋 Kế hoạch |



## 🔄 Quy trình Nghiệp Vụ Chính| `garment_planning` | Kế hoạch SX: phân chuyền, auto-schedule | 8 ✅ | ✅ || `garment_sample` | Quản lý mẫu may | 📋 Kế hoạch |



```| `garment_maintenance` | Bảo trì máy may: lịch định kỳ, sửa chữa, theo dõi downtime | 11 ✅ | ✅ || `garment_packing` | Đóng gói & xuất hàng | 📋 Kế hoạch |

Nhận PO Khách Hàng → Làm Mẫu (Sample) → Tính Giá (Costing)

    ↓| `garment_payroll` | Lương khoán: piece rate, sản lượng cá nhân, tính lương tháng | 9 ✅ | ✅ || `garment_report` | Báo cáo chuyên ngành | 📋 Kế hoạch |

Xác Nhận Đơn Hàng → Lên Kế Hoạch SX (Planning)

    ↓| `garment_compliance` | Tuân thủ: audit BSCI/WRAP/SA8000, CAP, tìm kiếm phát hiện | 14 ✅ | ✅ |

Đặt Mua NPL → Nhận NPL → Kiểm Vải (QC Fabric)

    ↓## 🔧 Cấu hình sau cài đặt

Lên Sơ Đồ Cắt (Marker) → Trải Vải → Cắt → Đánh Số Bó

    ↓> **Tổng cộng: 65 tests ✅ — 0 failed, 0 errors**

Phân Chuyền May → Sản Xuất → QC Inline → QC Endline

    ↓                           ↓1. Truy cập `http://localhost:8069`

    ↓                     Gửi Gia Công (nếu cần)

    ↓                           ↓## 🔧 Cấu hình sau cài đặt2. Tạo database mới: `garment_db`

Hoàn Thiện (Cắt Chỉ, Ủi) → Xưởng Giặt → QC Final → AQL Inspection

    ↓3. Đăng nhập: admin / admin

Đóng Gói (Packing List) → Xuất Hàng (Shipping) → Hoàn Thành

```1. Truy cập `http://localhost:8069`4. Vào **Apps** → Cài đặt các module:



## 📊 Tính năng nổi bật2. Đăng nhập: `admin` / `admin` (database: `garment_db`)   - Sales, Purchase, Inventory, Manufacturing, HR



| Tính năng | Chi tiết |3. Vào **Apps** → Tìm "Garment" → Cài đặt các module   - Garment Base, Garment Production, Garment Quality

|-----------|----------|

| **Quản lý vải & phụ liệu** | Theo loại, thành phần, khổ vải, định lượng, nhà cung cấp, giá |4. Vào **Settings** → Cài ngôn ngữ Tiếng Việt (nếu cần)5. Vào **Settings** → Cài ngôn ngữ Tiếng Việt

| **Mẫu may / Style** | Tech pack, rập, hình ảnh, SAM, ký hiệu giặt ủi, size & màu |

| **Đơn hàng may** | FOB/CIF, PO khách hàng, size-color matrix, tiến độ sản xuất |5. Cấu hình thông tin công ty6. Cấu hình thông tin công ty

| **Kế hoạch sản xuất** | Phân chuyền tự động, năng suất/ngày, ước tính ngày kết thúc |

| **Sản xuất** | Chuyền may, lệnh SX, sản lượng ngày theo ca, hiệu suất |

| **Cắt nâng cao** | Marker, trải vải (lớp), bó hàng, phát xuống chuyền, hao hụt |

| **Kiểm tra chất lượng** | QC inline/endline/final, AQL, phân loại lỗi, tỷ lệ lỗi |### Thứ tự cài đặt module (tự động xử lý dependencies):## 📁 Cấu trúc thư mục

| **Tính giá thành** | FOB/CM/CMT, chi phí vải/phụ liệu/nhân công/overhead/profit |

| **Quản lý mẫu** | 8 loại mẫu, workflow duyệt, comment khách hàng, revision |1. `garment_base` (cài trước — module cơ sở)

| **Đóng gói** | Packing list, thùng carton, CBM, gross/net weight, B/L |

| **Bảo trì máy** | 10 loại máy, lịch bảo trì, sửa chữa, downtime tracking |2. `garment_production` → `garment_quality` → `garment_report````

| **Lương khoán** | Đơn giá sản phẩm, sản lượng cá nhân, OT, tổng lương tháng |

| **Tuân thủ** | Audit BSCI/WRAP/SA8000/ISO, phát hiện, CAP, xếp hạng |3. `garment_costing`, `garment_sample`, `garment_cutting`, `garment_packing`odoo-garment-project/

| **Báo cáo** | Hiệu suất chuyền (pivot/graph), phân tích lỗi, wizard |

| **Tiến độ đơn hàng** | Theo dõi % hoàn thành, cảnh báo đúng hạn giao hàng |4. `garment_planning`, `garment_maintenance`, `garment_payroll`, `garment_compliance`├── odoo/                  # Odoo 19.0 source code

| **Xưởng giặt** | Hóa chất, công thức giặt, đơn giặt nội bộ/bên ngoài, QC giặt |

| **Gia công** | Gửi/nhận gia công, theo dõi tiến độ, đánh giá đối tác |├── custom-addons/         # Module tùy chỉnh



## 📖 Tài liệu## 📁 Cấu trúc thư mục│   ├── garment_base/



- [Tài liệu hướng dẫn sử dụng](./docs/USER_GUIDE.md)│   ├── garment_production/

- [Kế hoạch triển khai](./PROJECT_PLAN.md)

- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)```│   └── garment_quality/



## 📄 Licenseodoo-garment-project/├── docker-compose.yml



- Odoo Community: LGPL-3.0├── odoo/                          # Odoo 19.0 source code├── odoo.conf

- Custom Modules: LGPL-3.0

│   ├── addons/                    # Odoo standard addons├── PROJECT_PLAN.md        # Kế hoạch chi tiết

│   └── odoo/                      # Odoo core└── README.md              # File này

├── custom-addons/                 # 12 module tùy chỉnh```

│   ├── garment_base/              # ✅ Module cơ sở

│   │   └── models/                #    fabric, accessory, style, color, size, order, wash_symbol## 📖 Tài liệu tham khảo

│   ├── garment_production/        # ✅ Sản xuất

│   │   └── models/                #    sewing_line, production_order, cutting_order, daily_output- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)

│   ├── garment_quality/           # ✅ Chất lượng- [Odoo Developer Tutorial](https://www.odoo.com/documentation/19.0/developer.html)

│   │   └── models/                #    defect_type, qc_inspection- [PROJECT_PLAN.md](./PROJECT_PLAN.md) - Kế hoạch triển khai chi tiết

│   ├── garment_costing/           # ✅ Tính giá thành

│   │   └── models/                #    cost_sheet, cost_line## 📄 License

│   ├── garment_sample/            # ✅ Quản lý mẫu

│   │   └── models/                #    garment_sample (+ sample_comment)Odoo Community: LGPL-3.0

│   ├── garment_cutting/           # ✅ Cắt nâng caoCustom Modules: LGPL-3.0

│   │   └── models/                #    cutting_order, cutting_layer, cutting_bundle
│   ├── garment_packing/           # ✅ Đóng gói & xuất hàng
│   │   └── models/                #    packing_list, carton_line
│   ├── garment_report/            # ✅ Báo cáo
│   │   ├── models/                #    efficiency_analysis, defect_analysis (SQL views)
│   │   └── report/                #    production_report (wizard)
│   ├── garment_planning/          # ✅ Kế hoạch sản xuất
│   │   └── models/                #    production_plan, line_loading
│   ├── garment_maintenance/       # ✅ Bảo trì máy
│   │   └── models/                #    machine, maintenance_request
│   ├── garment_payroll/           # ✅ Lương khoán
│   │   └── models/                #    piece_rate, worker_output, wage_calculation
│   └── garment_compliance/        # ✅ Tuân thủ
│       └── models/                #    compliance_audit, corrective_action
├── docker-compose.yml             # Docker setup
├── odoo.conf                      # Cấu hình Odoo
├── docs/                          # Tài liệu hướng dẫn
├── PROJECT_PLAN.md                # Kế hoạch chi tiết
└── README.md                      # File này
```

## 🔄 Quy trình Nghiệp Vụ Chính

```
Nhận PO Khách Hàng → Làm Mẫu (Sample) → Tính Giá (Costing)
    ↓
Xác Nhận Đơn Hàng → Lên Kế Hoạch SX (Planning)
    ↓
Đặt Mua NPL → Nhận NPL → Kiểm Vải (QC Fabric)
    ↓
Lên Sơ Đồ Cắt (Marker) → Trải Vải → Cắt → Đánh Số Bó
    ↓
Phân Chuyền May → Sản Xuất → QC Inline → QC Endline
    ↓
Hoàn Thiện (Cắt Chỉ, Ủi) → QC Final → AQL Inspection
    ↓
Đóng Gói (Packing List) → Xuất Hàng (Shipping) → Hoàn Thành
```

## 📊 Tính năng nổi bật

| Tính năng | Chi tiết |
|-----------|----------|
| **Quản lý vải & phụ liệu** | Theo loại, thành phần, khổ vải, định lượng, nhà cung cấp, giá |
| **Mẫu may / Style** | Tech pack, rập, hình ảnh, SAM, ký hiệu giặt ủi, size & màu |
| **Đơn hàng may** | FOB/CIF, PO khách hàng, size-color matrix, tiến độ sản xuất |
| **Kế hoạch sản xuất** | Phân chuyền tự động, năng suất/ngày, ước tính ngày kết thúc |
| **Sản xuất** | Chuyền may, lệnh SX, sản lượng ngày theo ca, hiệu suất |
| **Cắt nâng cao** | Marker, trải vải (lớp), bó hàng, phát xuống chuyền, hao hụt |
| **Kiểm tra chất lượng** | QC inline/endline/final, AQL, phân loại lỗi, tỷ lệ lỗi |
| **Tính giá thành** | FOB/CM/CMT, chi phí vải/phụ liệu/nhân công/overhead/profit |
| **Quản lý mẫu** | 8 loại mẫu, workflow duyệt, comment khách hàng, revision |
| **Đóng gói** | Packing list, thùng carton, CBM, gross/net weight, B/L |
| **Bảo trì máy** | 10 loại máy, lịch bảo trì, sửa chữa, downtime tracking |
| **Lương khoán** | Đơn giá sản phẩm, sản lượng cá nhân, OT, tổng lương tháng |
| **Tuân thủ** | Audit BSCI/WRAP/SA8000/ISO, phát hiện, CAP, xếp hạng |
| **Báo cáo** | Hiệu suất chuyền (pivot/graph), phân tích lỗi, wizard |
| **Tiến độ đơn hàng** | Theo dõi % hoàn thành, cảnh báo đúng hạn giao hàng |

## 📖 Tài liệu

- [Tài liệu hướng dẫn sử dụng](./docs/USER_GUIDE.md)
- [Kế hoạch triển khai](./PROJECT_PLAN.md)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)

## 📄 License

- Odoo Community: LGPL-3.0
- Custom Modules: LGPL-3.0
