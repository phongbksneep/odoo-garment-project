# 🏭 KẾ HOẠCH TRIỂN KHAI ODOO 19 CHO CÔNG TY MAY

## 📋 Tổng Quan Dự Án

| Thông tin | Chi tiết |
|-----------|----------|
| **Nền tảng** | Odoo 19.0 Community Edition |
| **Ngành** | Sản xuất May mặc (Garment Manufacturing) |
| **Ngôn ngữ** | Tiếng Việt (vi_VN) |
| **Thời gian dự kiến** | 6 tháng (Pha 1-4) |

---

## 🎯 PHA 1: NỀN TẢNG CƠ SỞ (Tháng 1-2)

### 1.1 Cài đặt & Cấu hình hệ thống
- [x] Clone Odoo 19.0 source code
- [x] Tạo cấu trúc project
- [x] Docker compose cho môi trường dev
- [ ] Cài đặt PostgreSQL 16
- [ ] Cấu hình Odoo server
- [ ] Cài đặt ngôn ngữ Tiếng Việt
- [ ] Cấu hình email server
- [ ] Thiết lập backup tự động

### 1.2 Module Odoo tiêu chuẩn cần cài
| Module | Mục đích | Ưu tiên |
|--------|----------|---------|
| **Contacts (res.partner)** | Quản lý khách hàng, nhà cung cấp | ⭐⭐⭐ |
| **Sales (sale_management)** | Quản lý đơn hàng bán | ⭐⭐⭐ |
| **Purchase** | Quản lý mua hàng NPL | ⭐⭐⭐ |
| **Inventory (stock)** | Quản lý kho vải, phụ liệu, thành phẩm | ⭐⭐⭐ |
| **Manufacturing (mrp)** | Quản lý sản xuất | ⭐⭐⭐ |
| **Accounting** | Kế toán, tài chính | ⭐⭐⭐ |
| **HR (hr)** | Quản lý nhân sự | ⭐⭐⭐ |
| **HR Attendance** | Chấm công | ⭐⭐ |
| **HR Payroll** | Tính lương | ⭐⭐ |
| **Project** | Quản lý dự án | ⭐⭐ |
| **Quality** | Quản lý chất lượng | ⭐⭐ |
| **Maintenance** | Bảo trì máy móc | ⭐ |

### 1.3 Module Custom đã tạo
- [x] **garment_base** - Module cơ sở ngành may
  - Quản lý Vải (Fabric)
  - Quản lý Phụ Liệu (Accessories)
  - Quản lý Mẫu May / Style
  - Bảng Màu (Color)
  - Bảng Size
  - Đơn Hàng May (Garment Order)

- [x] **garment_production** - Module sản xuất
  - Chuyền May (Sewing Line)
  - Lệnh Sản Xuất (Production Order)
  - Lệnh Cắt (Cutting Order)
  - Sản Lượng Hàng Ngày (Daily Output)

- [x] **garment_quality** - Module chất lượng
  - Loại Lỗi (Defect Types)
  - Phiếu Kiểm Tra QC (QC Inspection)
  - QC Inline / Final / AQL

---

## 🔧 PHA 2: PHÁT TRIỂN MODULE CHUYÊN SÂU (Tháng 2-3)

### 2.1 Module `garment_costing` - Tính Giá Thành
- [ ] Bảng định mức nguyên phụ liệu (BOM Garment)
- [ ] Tính giá FOB / CM / CMT / CMPT
- [ ] Chi phí nguyên liệu (Fabric Cost)
- [ ] Chi phí phụ liệu (Trim Cost)
- [ ] Chi phí nhân công (Labor Cost - dựa trên SAM)
- [ ] Chi phí sản xuất chung (Overhead)
- [ ] Chi phí đóng gói (Packing Cost)
- [ ] Báo cáo so sánh giá dự toán vs thực tế

### 2.2 Module `garment_sample` - Quản Lý Mẫu
- [ ] Yêu cầu làm mẫu (Sample Request)
- [ ] Loại mẫu: Proto, Fit, Size Set, PP, TOP, Shipment
- [ ] Theo dõi trạng thái mẫu
- [ ] Nhận xét / Comment từ khách hàng
- [ ] Lịch sử gửi mẫu

### 2.3 Module `garment_cutting` - Mở Rộng Quản Lý Cắt
- [ ] Sơ đồ cắt (Marker/Layout)
- [ ] Hiệu suất vải (Fabric Utilization)
- [ ] Đánh số bó (Bundle Numbering)
- [ ] Theo dõi tồn vải trên bàn cắt
- [ ] Báo cáo hao hụt vải

### 2.4 Module `garment_packing` - Đóng Gói & Xuất Hàng
- [ ] Packing List
- [ ] Carton Box Management
- [ ] Assortment (phân bổ size/màu vào thùng)
- [ ] Shipping Instruction
- [ ] Bill of Lading
- [ ] Commercial Invoice
- [ ] Certificate of Origin

---

## 📊 PHA 3: BÁO CÁO & TÍCH HỢP (Tháng 3-4)

### 3.1 Module `garment_report` - Báo Cáo Chuyên Ngành
- [ ] **Báo cáo sản xuất:**
  - Báo cáo năng suất chuyền (Line Efficiency)
  - Báo cáo sản lượng theo ngày/tuần/tháng
  - Biểu đồ tiến độ đơn hàng
  - So sánh SAM chuẩn vs thực tế
  
- [ ] **Báo cáo chất lượng:**
  - Tỷ lệ lỗi theo chuyền/mã hàng
  - Pareto chart - Top lỗi phổ biến
  - Báo cáo QC theo AQL
  - DHU (Defects per Hundred Units)
  
- [ ] **Báo cáo tồn kho:**
  - Tồn kho vải theo loại/màu
  - Tồn kho phụ liệu
  - Cảnh báo tồn kho tối thiểu
  - Báo cáo xuất nhập tồn NPL
  
- [ ] **Báo cáo tài chính:**
  - Giá thành sản xuất theo đơn hàng
  - Lợi nhuận theo khách hàng / mã hàng
  - Chi phí nguyên liệu / đơn hàng

### 3.2 Dashboard
- [ ] Dashboard Giám đốc sản xuất
- [ ] Dashboard Chuyền trưởng
- [ ] Dashboard QC Manager
- [ ] Dashboard Quản lý kho

### 3.3 Tích hợp
- [ ] Tích hợp máy chấm công (HR Attendance)
- [ ] Tích hợp barcode / QR code cho tracking
- [ ] Export Excel / PDF cho các báo cáo
- [ ] API cho mobile app (nếu cần)

---

## 🏗️ PHA 4: TỐI ƯU & NÂNG CAO (Tháng 4-6)

### 4.1 Module `garment_planning` - Kế Hoạch Sản Xuất
- [ ] Lịch sản xuất tổng (Master Production Schedule)
- [ ] Phân chuyền tự động
- [ ] Cân bằng chuyền (Line Balancing)
- [ ] Gantt chart tiến độ
- [ ] Cảnh báo trễ deadline

### 4.2 Module `garment_maintenance` - Bảo Trì
- [ ] Quản lý máy may (theo loại: 1 kim, 2 kim, vắt sổ, ...)
- [ ] Lịch bảo trì định kỳ
- [ ] Yêu cầu sửa chữa
- [ ] Quản lý phụ tùng thay thế
- [ ] Thống kê thời gian máy hỏng

### 4.3 Module `garment_hr` - Nhân Sự Ngành May
- [ ] Quản lý tay nghề công nhân
- [ ] Đánh giá kỹ năng theo công đoạn
- [ ] Tính lương sản phẩm (Piece Rate)
- [ ] Tính lương theo năng suất
- [ ] Quản lý ca làm việc
- [ ] Overtime / Tăng ca

### 4.4 Module `garment_compliance` - Tuân Thủ
- [ ] Audit xã hội (Social Audit)
- [ ] Quản lý chứng chỉ (BSCI, WRAP, SA8000, ...)
- [ ] Hệ thống 5S
- [ ] An toàn lao động
- [ ] Quản lý hóa chất

---

## 📐 CẤU TRÚC THƯ MỤC DỰ ÁN

```
odoo-garment-project/
├── odoo/                          # Odoo 19.0 source (clone từ GitHub)
│   ├── addons/                    # Odoo standard addons
│   └── odoo/                      # Odoo core
├── custom-addons/                 # Custom modules cho công ty may
│   ├── garment_base/              # ✅ Module cơ sở
│   │   ├── models/
│   │   │   ├── fabric.py          # Quản lý vải
│   │   │   ├── accessory.py       # Quản lý phụ liệu
│   │   │   ├── garment_style.py   # Mẫu may / Style
│   │   │   ├── garment_color.py   # Bảng màu
│   │   │   ├── garment_size.py    # Bảng size
│   │   │   └── garment_order.py   # Đơn hàng may
│   │   ├── views/
│   │   ├── security/
│   │   ├── data/
│   │   └── static/
│   ├── garment_production/        # ✅ Module sản xuất
│   │   ├── models/
│   │   │   ├── sewing_line.py     # Chuyền may
│   │   │   ├── production_order.py # Lệnh sản xuất
│   │   │   ├── cutting_order.py   # Lệnh cắt
│   │   │   └── daily_output.py    # Sản lượng ngày
│   │   ├── views/
│   │   ├── security/
│   │   └── data/
│   ├── garment_quality/           # ✅ Module chất lượng
│   │   ├── models/
│   │   │   ├── defect_type.py     # Loại lỗi
│   │   │   └── qc_inspection.py   # Phiếu kiểm tra QC
│   │   ├── views/
│   │   ├── security/
│   │   └── data/
│   ├── garment_costing/           # 📋 Tính giá thành (Pha 2)
│   ├── garment_sample/            # 📋 Quản lý mẫu (Pha 2)
│   ├── garment_packing/           # 📋 Đóng gói & xuất hàng (Pha 2)
│   ├── garment_report/            # 📋 Báo cáo (Pha 3)
│   ├── garment_planning/          # 📋 Kế hoạch SX (Pha 4)
│   ├── garment_maintenance/       # 📋 Bảo trì (Pha 4)
│   ├── garment_hr/                # 📋 Nhân sự ngành may (Pha 4)
│   └── garment_compliance/        # 📋 Tuân thủ (Pha 4)
├── docker-compose.yml             # ✅ Docker setup
├── odoo.conf                      # ✅ Cấu hình Odoo
├── PROJECT_PLAN.md                # ✅ File này
├── README.md                      # ✅ Hướng dẫn cài đặt
└── logs/                          # Log files
```

---

## 🔄 QUY TRÌNH NGHIỆP VỤ CHÍNH

### Quy trình Đơn Hàng May (Order Flow)
```
Nhận PO Khách Hàng → Xác Nhận Đơn Hàng → Lên Kế Hoạch SX
    ↓
Đặt Mua NPL → Nhận NPL vào Kho → Kiểm Vải (QC Fabric)
    ↓
Lên Sơ Đồ Cắt → Cắt Vải → Đánh Số Bó
    ↓
Phân Chuyền → May → QC Inline → QC Endline
    ↓
Hoàn Thiện (Cắt Chỉ, Ủi) → QC Final → AQL Inspection
    ↓
Đóng Gói → Xuất Hàng → Hoàn Thành
```

### Quy trình Sản Xuất (Production Flow)
```
Lệnh Sản Xuất (PO) ──→ Lệnh Cắt (CO) ──→ Giao Bán Thành Phẩm
                                                    ↓
                                            Chuyền May ──→ Sản Lượng Ngày
                                                    ↓
                                            Hoàn Thiện ──→ QC ──→ Đóng Gói
```

### Quy trình Kiểm Tra Chất Lượng (QC Flow)
```
QC Vải đầu vào → QC Inline (trên chuyền) → QC Endline (cuối chuyền)
    ↓                                               ↓
Kiểm NPL                                   QC Final (kiểm cuối)
                                                    ↓
                                            AQL Inspection → ĐẠT → Đóng gói
                                                           → KHÔNG ĐẠT → Sửa lại
```

---

## 📈 CHỈ SỐ KPI THEO DÕI

| KPI | Mô tả | Mục tiêu |
|-----|--------|----------|
| **Line Efficiency** | Hiệu suất chuyền may | ≥ 65% |
| **DHU** | Defects per Hundred Units | ≤ 5% |
| **On-Time Delivery** | Giao hàng đúng hạn | ≥ 95% |
| **Fabric Utilization** | Hiệu suất sử dụng vải | ≥ 85% |
| **AQL Pass Rate** | Tỷ lệ đạt AQL | ≥ 98% |
| **Rework Rate** | Tỷ lệ sửa lại | ≤ 3% |
| **Absenteeism** | Tỷ lệ vắng mặt | ≤ 5% |
| **Machine Downtime** | Thời gian máy hỏng | ≤ 3% |
| **Order Fulfillment** | Tỷ lệ hoàn thành đơn | ≥ 98% |

---

## 💡 GHI CHÚ QUAN TRỌNG

### Thuật ngữ ngành may
| Tiếng Việt | Tiếng Anh | Giải thích |
|-----------|-----------|------------|
| NPL | Raw Material | Nguyên Phụ Liệu |
| Định mức | Consumption | Lượng NPL cần cho 1 sản phẩm |
| SAM | Standard Allowed Minutes | Thời gian chuẩn cho phép |
| FOB | Free On Board | Giá giao tại cảng |
| CM | Cut & Make | Giá gia công cắt may |
| CMT | Cut, Make & Trim | Giá gia công cắt may + phụ liệu |
| AQL | Acceptable Quality Level | Mức chất lượng chấp nhận |
| DHU | Defects per Hundred Units | Số lỗi trên 100 sản phẩm |
| BTP | Semi-finished Product | Bán thành phẩm |
| Rập | Pattern | Mẫu giấy cắt vải |
| Sơ đồ | Marker | Bản vẽ xếp rập trên vải |

### Yêu cầu hệ thống
- **Server:** Ubuntu 22.04+ / macOS
- **Python:** 3.10+
- **PostgreSQL:** 15+
- **RAM:** 4GB+ (khuyến nghị 8GB)
- **Storage:** 50GB+ SSD

---

## 📞 Liên hệ & Hỗ trợ
- **Tài liệu Odoo:** https://www.odoo.com/documentation/19.0/
- **Odoo Forum:** https://www.odoo.com/forum/help-1
- **GitHub Odoo:** https://github.com/odoo/odoo (branch 19.0)
