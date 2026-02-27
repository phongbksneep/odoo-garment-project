# 🚀 Hướng Dẫn Nhanh — Hệ Thống Quản Lý Công Ty May

> **Phiên bản:** Odoo 19.0 | **Cập nhật:** Tháng 2/2026 | **24 module** | **216 tests passed**
>
> 📖 Xem [Hướng dẫn chi tiết đầy đủ](USER_GUIDE.md) để tra cứu từng trường dữ liệu.

---

## 1. Đăng Nhập & Giao Diện

1. Truy cập **http://localhost:8069**
2. Đăng nhập: `admin` / `admin`
3. Nhấn vào app **"Công Ty May"** — đây là app **duy nhất** chứa toàn bộ chức năng

![Đăng nhập](images/01_login.png)

![Trang chủ](images/02_home.png)

---

## 2. Cấu Trúc Menu

Toàn bộ chức năng nằm trong **8 nhóm menu** trên thanh ngang:

| # | Menu | Chức Năng Chính |
|---|------|----------------|
| 1 | **Đơn Hàng** | Đơn hàng, Style, Mẫu (Sample), Vải, Phụ liệu, Tính giá |
| 2 | **CRM** | Lead, Cơ hội kinh doanh, Buyer, Phản hồi/Khiếu nại |
| 3 | **Sản Xuất** | Lệnh SX, Cắt, Sản lượng ngày, Chuyền may, Hoàn thiện, Kế hoạch, Bảo trì, Giặt, Gia công |
| 4 | **Chất Lượng** | QC, Loại lỗi, Audits, CAP |
| 5 | **Kho & Giao Hàng** | Nhập NL, Phân bổ NL, Tem QR, Thùng hàng, Pallet, Packing, Nhập/Xuất kho, Giao hàng |
| 6 | **Kế Toán** | Hóa đơn bán/mua, Thanh toán |
| 7 | **Nhân Sự & Lương** | Chấm công, Nghỉ phép, Tay nghề, Lương khoán, Thưởng |
| 8 | **Báo Cáo** | Dashboard KPI, Tổng quan đơn hàng, Tiến độ SX, Cảnh báo, Hiệu suất chuyền |
| 9 | **Cấu Hình** | Bảng màu, Size, Ký hiệu giặt, Công thức giặt |

![Menu Đơn Hàng](images/80_menu_don_hang.png)

![Menu Sản Xuất](images/81_menu_san_xuat.png)

![Menu Chất Lượng](images/82_menu_chat_luong.png)

![Menu Kho & Giao Hàng](images/83_menu_kho.png)

![Menu Kế Toán](images/84_menu_ke_toan.png)

![Menu Nhân Sự & Lương](images/85_menu_nhan_su.png)

![Menu Báo Cáo](images/86_menu_bao_cao.png)

![Menu Cấu Hình](images/87_menu_cau_hinh.png)

---

## 3. Luồng Nghiệp Vụ Chính

### 3.1 Từ Đơn Hàng Đến Giao Hàng

```mermaid
flowchart LR
    CRM[🤝 CRM Lead] --> A[📋 Nhận Đơn Hàng]
    A --> B[✂️ Thiết Kế & Mẫu]
    B --> C[💰 Tính Giá Thành]
    C --> D[📅 Lập Kế Hoạch SX]
    D --> E[✂️ Cắt Vải]
    E --> F[🧵 May]
    F --> G[🧼 Giặt]
    G --> H[👔 Hoàn Thiện]
    H --> I[🔍 QC Kiểm Tra]
    I --> J[🏷️ In Tem/QR]
    J --> K[📦 Đóng Gói & Pallet]
    K --> L[🚚 Giao Hàng]
    L --> M[💵 Kế Toán]
    M --> FB[📝 Phản Hồi KH]

    style CRM fill:#E91E63,color:#fff
    style A fill:#4CAF50,color:#fff
    style F fill:#2196F3,color:#fff
    style I fill:#FF9800,color:#fff
    style L fill:#9C27B0,color:#fff
    style M fill:#F44336,color:#fff
    style FB fill:#E91E63,color:#fff
```

### 3.2 Sơ Đồ Liên Kết Module

```mermaid
graph TB
    BASE[🏭 garment_base\nĐơn Hàng, Style, Vải, Phụ Liệu]

    CRM[🤝 garment_crm\nLead, Phản Hồi, Buyer] --> BASE
    BASE --> SAMPLE[🎨 garment_sample\nQuản lý mẫu]
    BASE --> COSTING[💰 garment_costing\nTính giá thành]
    BASE --> PLANNING[📅 garment_planning\nKế hoạch SX]
    BASE --> PRODUCTION[🧵 garment_production\nLệnh SX, Chuyền May]
    BASE --> CUTTING[✂️ garment_cutting\nLệnh cắt]
    BASE --> ACCOUNTING[💵 garment_accounting\nHóa đơn, Thanh toán]
    BASE --> WAREHOUSE[📦 garment_warehouse\nPhiếu kho]
    BASE --> DELIVERY[🚚 garment_delivery\nGiao hàng]

    PRODUCTION --> QUALITY[🔍 garment_quality\nKiểm tra QC]
    PRODUCTION --> FINISHING[👔 garment_finishing\nHoàn thiện]
    PRODUCTION --> WASHING[🧼 garment_washing\nGiặt]
    PRODUCTION --> SUBCONTRACT[🤝 garment_subcontract\nGia công]
    PRODUCTION --> PACKING[📦 garment_packing\nĐóng gói]
    PRODUCTION --> DAILY[📊 Sản lượng ngày]

    PACKING --> LABEL[🏷️ garment_label\nIn Tem/QR, Pallet, Thùng]
    LABEL --> DELIVERY

    DAILY --> PAYROLL[💰 garment_payroll\nTính lương]
    HR[👥 garment_hr\nChấm công, Nghỉ phép] --> PAYROLL

    MAINTENANCE[🔧 garment_maintenance\nBảo trì máy] --> PRODUCTION
    COMPLIANCE[📋 garment_compliance\nTuân thủ] -.-> BASE
    REPORT[📊 garment_report\nBáo cáo] -.-> PRODUCTION
    REPORT -.-> QUALITY
    MATERIAL[📥 garment_material\nNhập NL] --> WAREHOUSE
    MATERIAL --> PRODUCTION
    DASHBOARD[📊 garment_dashboard\nDashboard] -.-> PRODUCTION
    DASHBOARD -.-> REPORT

    style BASE fill:#4CAF50,color:#fff
    style PRODUCTION fill:#2196F3,color:#fff
    style PAYROLL fill:#FF9800,color:#fff
    style ACCOUNTING fill:#F44336,color:#fff
    style DASHBOARD fill:#9C27B0,color:#fff
    style MATERIAL fill:#009688,color:#fff
    style CRM fill:#E91E63,color:#fff
    style LABEL fill:#FF5722,color:#fff
```

### 3.3 Luồng Chứng Từ

```mermaid
flowchart TB
    PO[📋 Đơn Hàng May] --> PROD[🏭 Lệnh Sản Xuất]
    PO --> CUT[✂️ Lệnh Cắt]
    PROD --> DO[📊 Sản Lượng Ngày]
    CUT --> PROD
    PROD --> QC[🔍 Phiếu QC]
    PROD --> FN[👔 Lệnh Hoàn Thiện]
    PROD --> WO[🧼 Lệnh Giặt]
    PROD --> SO[🤝 Đơn Gia Công]
    FN --> PL[📦 Packing List]
    QC --> PL
    PL --> DL[🚚 Phiếu Giao Hàng]
    DL --> INV[💵 Hóa Đơn]
    INV --> PAY[💳 Phiếu Thanh Toán]

    SM_IN[📥 Phiếu Nhập Kho] --> PO
    PO --> SM_OUT[📤 Phiếu Xuất Kho]

    DO --> WAGE[💰 Bảng Lương]
    ATT[🕐 Chấm Công] --> WAGE

    style PO fill:#4CAF50,color:#fff
    style PROD fill:#2196F3,color:#fff
    style INV fill:#F44336,color:#fff
    style WAGE fill:#FF9800,color:#fff
```

---

## 4. Vòng Đời Đơn Hàng

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đã_Xác_Nhận: Xác nhận
    Đã_Xác_Nhận --> Chuẩn_Bị_NL: Chuẩn bị
    Chuẩn_Bị_NL --> Đang_Cắt: Bắt đầu cắt
    Đang_Cắt --> Đang_May: Chuyển may
    Đang_May --> Hoàn_Thiện: Hoàn thiện
    Hoàn_Thiện --> Kiểm_QC: Kiểm tra
    Kiểm_QC --> Đóng_Gói: Đóng gói
    Đóng_Gói --> Đã_Giao: Giao hàng
    Đã_Giao --> Hoàn_Thành: Hoàn tất
    Nháp --> Đã_Hủy: Hủy
    Đã_Xác_Nhận --> Đã_Hủy: Hủy
```

---

## 5. Hướng Dẫn Theo Chức Năng

### 5.1 Đơn Hàng & Style

**Đường dẫn:** `Công Ty May → Đơn Hàng`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Tạo đơn hàng mới | Đơn Hàng May → **Tạo** → Chọn khách hàng, style → Thêm dòng chi tiết (màu, size, SL) → **Lưu** |
| Thêm mẫu may (Style) | Mẫu May / Style → **Tạo** → Điền tên, mã, loại SP → Upload tech pack → **Lưu** |
| Quản lý vải | Vải → **Tạo** → Tên, loại, khổ vải, giá → **Lưu** |
| Quản lý phụ liệu | Phụ Liệu → **Tạo** → Tên, loại, kích thước → **Lưu** |
| Tạo mẫu (Sample) | Quản Lý Mẫu → **Tạo** → Chọn style, loại mẫu (proto/fit/pp/top) → **Lưu** |
| Tính giá thành | Bảng Tính Giá Thành → **Tạo** → Chọn style → Thêm dòng chi phí (vải, PL, CM, ...) → **Lưu** |

![Đơn hàng](images/03_garment_orders.png)

![Chi tiết đơn hàng](images/50_order_detail.png)

#### Workflow mẫu may:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đang_Thiết_Kế: Thiết Kế
    Đang_Thiết_Kế --> Làm_Mẫu: Làm Mẫu
    Làm_Mẫu --> Đã_Duyệt: Duyệt
    Đã_Duyệt --> Đang_SX: Sản Xuất
    Đang_SX --> Ngừng_SX: Ngừng
```

#### Workflow phiếu mẫu (Sample):

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đang_Làm: Bắt đầu
    Đang_Làm --> Đã_Gửi: Gửi buyer
    Đã_Gửi --> Duyệt: Buyer duyệt
    Đã_Gửi --> Duyệt_Có_Sửa: Duyệt có chỉnh sửa
    Đã_Gửi --> Từ_Chối: Buyer từ chối
    Duyệt_Có_Sửa --> Đang_Làm: Làm lại (revision +1)
    Từ_Chối --> Đang_Làm: Làm lại (revision +1)
    Nháp --> Đã_Hủy: Hủy
```

---

### 5.2 Sản Xuất

**Đường dẫn:** `Công Ty May → Sản Xuất`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Tạo lệnh SX | Lệnh Sản Xuất → **Tạo** → Chọn đơn hàng, chuyền may → SL kế hoạch → **Xác nhận** |
| Nhập sản lượng ngày | Sản Lượng Ngày → **Tạo** → Chọn lệnh SX, ngày, ca → Nhập SL đạt, SL lỗi → **Lưu** |
| Tạo lệnh cắt | Lệnh Cắt → **Tạo** → Chọn đơn hàng, vải → Thêm lớp trải + bundle → **Xác nhận** |
| Lệnh hoàn thiện | Lệnh Hoàn Thiện → **Tạo** → Chọn lệnh SX → Nhập các task (cắt chỉ, ủi, gấp) → **Lưu** |
| Kế hoạch SX | Kế Hoạch SX → **Tạo** → Chọn đơn hàng → Phân chuyền (Line Loading) → **Xác nhận** |
| Quản lý chuyền | Chuyền May → **Tạo** → Tên, mã, loại, chuyền trưởng, CN → **Lưu** |
| Quản lý máy | Danh Sách Máy → **Tạo** → Loại, hãng, model, serial → Gắn chuyền → **Lưu** |
| Yêu cầu bảo trì | Yêu Cầu Bảo Trì → **Tạo** → Chọn máy, loại (định kỳ/sửa chữa/khẩn) → **Xác nhận** |

![Lệnh SX](images/07_production_orders.png)

![Chi tiết Lệnh SX](images/52_production_detail.png)

#### Workflow lệnh sản xuất:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Xác_Nhận: Xác nhận
    Xác_Nhận --> Đang_SX: Bắt đầu
    Đang_SX --> Hoàn_Thành: Hoàn thành
    Nháp --> Đã_Hủy: Hủy
```

---

### 5.3 Giặt & Gia Công

**Đường dẫn:** `Công Ty May → Sản Xuất → Lệnh Giặt / Đơn Gia Công`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Tạo lệnh giặt | Lệnh Giặt → **Tạo** → Chọn loại (nội bộ/gia công), lệnh SX, công thức giặt → Nhập SL → **Xác nhận** |
| Tạo đơn gia công | Đơn Gia Công → **Tạo** → Chọn loại (gửi/nhận), đối tác, công việc → Nhập chi tiết → **Xác nhận** |
| Thiết lập công thức giặt | Cấu Hình → Cấu Hình Giặt → Công Thức Giặt → **Tạo** → Loại giặt, nhiệt độ, hóa chất → **Lưu** |

![Lệnh Giặt](images/19_wash_orders.png)

![Chi tiết Giặt](images/58_wash_detail.png)

#### Workflow giặt:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Xác_Nhận: Xác nhận
    Xác_Nhận --> Đang_Giặt: Bắt đầu giặt
    Đang_Giặt --> Kiểm_Tra: Kiểm tra QC
    Kiểm_Tra --> Hoàn_Thành: Đạt
    Kiểm_Tra --> Đang_Giặt: Re-wash
    Hoàn_Thành --> Đã_Giao: Giao hàng
```

#### Workflow gia công:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Xác_Nhận: Xác nhận
    Xác_Nhận --> Đã_Gửi: Gửi hàng/NL
    Đã_Gửi --> Đang_GC: Đối tác xác nhận
    Đang_GC --> Nhận_1_Phần: Nhận một phần
    Đang_GC --> Đã_Nhận: Nhận đủ
    Nhận_1_Phần --> Đã_Nhận: Nhận nốt
    Đã_Nhận --> Kiểm_Tra: QC
    Kiểm_Tra --> Hoàn_Thành: Done
```

---

### 5.4 Chất Lượng & Tuân Thủ

**Đường dẫn:** `Công Ty May → Chất Lượng`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Tạo phiếu QC | Phiếu Kiểm Tra QC → **Tạo** → Chọn lệnh SX, loại QC (inline/endline/final/AQL) → Nhập SL kiểm, SL lỗi → **Lưu** |
| Tạo audit | Audits → **Tạo** → Loại (BSCI/WRAP/SEDEX...), auditor → Thêm finding + CAP → **Lưu** |

> ⚠️ Không thể đóng audit khi còn CAP chưa hoàn thành.

![QC Inspections](images/22_qc_inspections.png)

![Chi tiết QC](images/53_qc_detail.png)

---

### 5.5 Kho & Giao Hàng

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Tạo packing list | Packing List → **Tạo** → Chọn khách hàng, đơn hàng → Nhập thông tin vận chuyển (PO, cảng, ETD) → Thêm dòng carton (thùng, màu, size, SL) → **Bắt Đầu Đóng** → **Đã Đóng** → **Xuất Hàng** |
| Nhập kho | Nhập Kho → **Tạo** → Loại = Nhập, chọn kho → Thêm dòng hàng → **Xác nhận** |
| Xuất kho | Xuất Kho → **Tạo** → Loại = Xuất, chọn kho → Thêm dòng hàng → **Xác nhận** |
| Tạo phiếu giao hàng | Phiếu Giao Hàng → **Tạo** → Chọn khách, đơn hàng, phương tiện → Nhập thông tin container/B/L → **Xác nhận** |
| Thêm phương tiện | Phương Tiện → **Tạo** → Loại xe, biển số, tải trọng → **Lưu** |

![Phiếu Nhập Kho](images/25_warehouse_in.png)

![Phiếu Giao Hàng](images/27_delivery.png)

![Chi tiết Giao Hàng](images/62_delivery_detail.png)

#### Workflow giao hàng:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Xác_Nhận: Xác nhận
    Xác_Nhận --> Xếp_Hàng: Loading
    Xếp_Hàng --> Đang_Vận_Chuyển: Xuất phát
    Đang_Vận_Chuyển --> Đã_Giao: Giao xong
```

---

### 5.6 Kế Toán

**Đường dẫn:** `Công Ty May → Kế Toán`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Tạo hóa đơn bán | Hóa Đơn Bán → **Tạo** → Chọn khách, đơn hàng → Thêm dòng (mô tả, SL, giá) → Chọn thuế GTGT → **Xác nhận** |
| Tạo hóa đơn mua | Hóa Đơn Mua → **Tạo** → Chọn NCC, phân loại chi phí → Thêm dòng → **Xác nhận** |
| Thanh toán | Phiếu Thanh Toán → **Tạo** → Chọn HĐ liên quan, phương thức (tiền mặt/CK/L/C) → Nhập số tiền → **Xác nhận** |

> 💡 Thuế GTGT 0% cho hàng xuất khẩu, 10% cho nội địa.

![Hóa đơn bán](images/29_invoice_sale.png)

![Chi tiết hóa đơn](images/63_invoice_detail.png)

---

### 5.7 Nhân Sự & Lương

**Đường dẫn:** `Công Ty May → Nhân Sự & Lương`

| Thao tác | Cách thực hiện |
|----------|---------------|
| Chấm công | Chấm Công → **Tạo** → Chọn NV, ngày, trạng thái (đi làm/vắng/muộn) → Nhập giờ vào/ra → **Lưu** |
| Tổng hợp công tháng | Tổng Hợp Công Tháng → **Tạo** → Chọn NV, tháng/năm → Nhấn **"Tính Tổng"** |
| Tạo đơn nghỉ phép | Đơn Nghỉ Phép → **Tạo** → Chọn NV, loại nghỉ, từ ngày → đến ngày → **Gửi Duyệt** |
| Thiết lập đơn giá khoán | Đơn Giá Khoán → **Tạo** → Chọn style, công đoạn → Nhập đơn giá/SP → **Lưu** |
| Nhập sản lượng CN | Sản Lượng Công Nhân → **Tạo** → Chọn CN, lệnh SX, ngày → Nhập SL + giờ OT → **Lưu** |
| Tính lương tháng | Bảng Lương → **Tạo** → Chọn CN, tháng → Nhấn **"Tính Lương"** (tự pull chấm công + sản lượng) |
| Tạo phiếu thưởng | Phiếu Thưởng → **Tạo** → Chọn loại, tháng → Thêm dòng NV + số tiền → **Xác nhận** |

> 💡 Lương tự động tính: Lương cơ bản + Khoán sản phẩm + Tăng ca + Phụ cấp − BHXH (10.5%) − Thuế TNCN.

![Chấm công](images/32_attendance.png)

![Bảng lương](images/38_wage.png)

![Chi tiết lương](images/66_wage_detail.png)

---

### 5.8 Báo Cáo

**Đường dẫn:** `Công Ty May → Báo Cáo`

| Báo cáo | Nội dung |
|---------|---------|
| **Hiệu Suất Chuyền** | So sánh năng suất thực tế vs mục tiêu, theo chuyền và style |
| **Phân Tích Lỗi** | Tỷ lệ lỗi theo loại, theo chuyền, trend theo thời gian |
| **Báo Cáo Sản Xuất** | Wizard lọc theo khoảng ngày, đơn hàng, chuyền |

![Báo cáo hiệu suất](images/40_report_efficiency.png)

![Phân tích lỗi](images/41_report_defect.png)

---

### 5.9 Nhập Nguyên Liệu

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng → Nhập NL Mua Hàng / NL Khách Gửi (CMT)`

| Thao tác | Mô tả |
|----------|-------|
| **Nhập NL Mua Hàng** | Tạo phiếu nhập từ NCC, chọn loại = "Mua Hàng", điền NCC + chi tiết NL |
| **NL Khách Gửi (CMT)** | Khách gửi NL để gia công, chọn loại = "Khách Gửi", điền khách hàng |
| **Kiểm tra QC** | Xác nhận → Kiểm tra → QC Đạt → Nhập Kho |
| **Phân bổ NL** | Cấp phát NL cho đơn hàng/lệnh SX (menu Phân Bổ NL Cho SX) |

![Danh sách phiếu nhập NL](images/90_material_receipt_all.png)

![Form nhập NL](images/93_material_receipt_form_new.png)

![Phân bổ NL](images/94_material_allocation.png)

---

### 5.10 Dashboard — Bảng Điều Khiển

**Đường dẫn:** `Công Ty May → Báo Cáo → Dashboard`

| Báo cáo | Nội dung |
|---------|---------|
| **Tổng Quan KPI** | 17 chỉ số: đơn hàng, SX, QC, giao hàng, NL — biểu đồ tự động |
| **Tổng Quan Đơn Hàng** | Trạng thái, tiến độ %, ngày còn lại, trễ hạn — màu đỏ khi trễ |
| **Tiến Độ Sản Xuất** | % hoàn thành, SL lỗi, chuyền may, progressbar — xanh/vàng/đỏ |
| **Đơn Trễ Hạn** | Cảnh báo đơn quá ngày giao |
| **LSX Hoàn Thành Thấp** | LSX đang chạy nhưng < 50% |
| **LSX Lỗi Cao** | LSX có tỷ lệ lỗi > 5% |

![Dashboard KPI](images/96_dashboard_kpi_graph.png)

![Tổng quan đơn hàng](images/97_dashboard_order_overview.png)

![Tiến độ SX](images/98_dashboard_production_progress.png)

### 5.11 CRM — Quan Hệ Khách Hàng

| Chức Năng | Menu | Mô Tả |
|-----------|------|-------|
| Lead / Cơ Hội | CRM → Lead / Cơ Hội | Pipeline bán hàng: Lead → Đánh giá → Báo giá → Thương lượng → Chốt |
| Buyer / Khách Hàng | CRM → Buyer | Hồ sơ buyer ngành may, thống kê đơn hàng |
| Phản Hồi / Khiếu Nại | CRM → Phản Hồi | Theo dõi feedback, complaint, đánh giá hài lòng |

**Quick workflow CRM:**
1. Tạo Lead → Đánh giá → Gửi báo giá → Chốt thành công
2. Nhấn **📋 Tạo Đơn Hàng** → Tự động tạo đơn hàng may

![CRM Lead](images/105_crm_lead_form_new.png)

### 5.12 In Tem & Quản Lý Pallet

| Chức Năng | Menu | Mô Tả |
|-----------|------|-------|
| Tem QR Code | Kho → Tem / QR Code | In tem sản phẩm, thùng, pallet, vị trí kho |
| Thùng Hàng | Kho → Quản Lý Thùng | Đóng/tách/gộp thùng, tạo tem QR, xếp lên pallet |
| Pallet | Kho → Quản Lý Pallet | Tạo/đóng/tách/gộp pallet, theo dõi xuất hàng |

**Quick workflow:**
1. Đóng thùng hàng (nhập nội dung, SL, kích thước)
2. Tạo tem QR cho thùng (🏷 Tạo Tem QR)
3. Xếp thùng lên pallet → Đóng pallet → Xuất hàng

![Carton Box](images/116_carton_box_form_new.png)
![Pallet](images/114_pallet_form_new.png)

---

## 6. Phân Quyền

| Nhóm | Quyền |
|------|-------|
| **Garment User** | Xem tất cả, tạo/sửa đơn hàng & sản lượng |
| **Garment Manager** | Toàn quyền: tạo, sửa, xóa tất cả dữ liệu |

**Thiết lập:** Settings → Users → Chọn user → Tab Access Rights → Mục **Công Ty May** → Chọn User hoặc Manager.

---

## 7. FAQ

| Câu hỏi | Giải đáp |
|---------|---------|
| Đổi ngôn ngữ Tiếng Việt? | Settings → Translations → Load a Translation → Vietnamese |
| Mã tự động bị sai? | Settings → Technical → Sequences → Sửa Number Next |
| Import hàng loạt? | Trên danh sách → ⚙️ → Import records → Upload CSV/Excel |
| Hiệu suất chuyền = 0%? | Kiểm tra: chuyền có gắn CN không? Style có SAM không? Sản lượng ngày đã nhập chưa? |
| Tính lương không ra tiền khoán? | Kiểm tra Worker Output + Piece Rate đã nhập → Nhấn **"Tính Lương"** |
| Luồng nghiệp vụ chính? | Đơn hàng → Mẫu → Tính giá → Nhập NL → Kế hoạch → Cắt → May → Giặt → Hoàn thiện → QC → Đóng gói → Giao hàng → Kế toán |

---

> 📖 **Tài liệu đầy đủ:** [USER_GUIDE.md](USER_GUIDE.md) — bao gồm giải thích chi tiết từng trường dữ liệu của tất cả 24 module.
>
> 📞 **Hỗ trợ:** Liên hệ đội phát triển | 📚 [Odoo Docs](https://www.odoo.com/documentation/19.0/)
