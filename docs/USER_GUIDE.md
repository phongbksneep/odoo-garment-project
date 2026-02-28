# 📖 Tài Liệu Hướng Dẫn Sử Dụng - Hệ Thống Quản Lý Công Ty May

> **Phiên bản:** Odoo 19.0 | **Ngày cập nhật:** Tháng 2/2026
> **Đối tượng:** Quản lý, trưởng phòng, nhân viên sử dụng hệ thống ERP
> **Tổng số module:** 27 module chuyên biệt | **291 test cases** — 0 failures

---

## 📑 Mục Lục

1. [Giới thiệu & Đăng nhập](#1-giới-thiệu--đăng-nhập)
2. [Sơ Đồ Tổng Quan & Luồng Nghiệp Vụ](#2-sơ-đồ-tổng-quan--luồng-nghiệp-vụ)
3. [Module Garment Base — Quản lý cơ sở](#3-module-garment-base--quản-lý-cơ-sở)
4. [Module Garment Production — Sản xuất](#4-module-garment-production--sản-xuất)
5. [Module Garment Quality — Chất lượng](#5-module-garment-quality--chất-lượng)
6. [Module Garment Costing — Tính giá thành](#6-module-garment-costing--tính-giá-thành)
7. [Module Garment Sample — Quản lý mẫu](#7-module-garment-sample--quản-lý-mẫu)
8. [Module Garment Cutting — Cắt nâng cao](#8-module-garment-cutting--cắt-nâng-cao)
9. [Module Garment Packing — Đóng gói & xuất hàng](#9-module-garment-packing--đóng-gói--xuất-hàng)
10. [Module Garment Planning — Kế hoạch sản xuất](#10-module-garment-planning--kế-hoạch-sản-xuất)
11. [Module Garment Maintenance — Bảo trì máy](#11-module-garment-maintenance--bảo-trì-máy)
12. [Module Garment Payroll — Lương khoán](#12-module-garment-payroll--lương-khoán)
13. [Module Garment Compliance — Tuân thủ](#13-module-garment-compliance--tuân-thủ)
14. [Module Garment Report — Báo cáo](#14-module-garment-report--báo-cáo)
15. [Module Garment Washing — Xưởng Giặt](#15-module-garment-washing--xưởng-giặt)
16. [Module Garment Subcontract — Gia Công](#16-module-garment-subcontract--gia-công)
17. [Module Garment Finishing — Hoàn Thiện](#17-module-garment-finishing--hoàn-thiện)
18. [Module Garment HR — Nhân Sự & Chấm Công](#18-module-garment-hr--nhân-sự--chấm-công)
19. [Module Garment Accounting — Kế Toán VN](#19-module-garment-accounting--kế-toán-vn)
20. [Module Garment Warehouse — Quản Lý Kho](#20-module-garment-warehouse--quản-lý-kho)
21. [Module Garment Delivery — Giao Hàng](#21-module-garment-delivery--giao-hàng)
22. [Module Garment Material — Nhập Nguyên Liệu](#22-module-garment-material--nhập-nguyên-liệu)
23. [Module Garment Dashboard — Bảng Điều Khiển](#23-module-garment-dashboard--bảng-điều-khiển)
24. [Module Garment CRM — Quan Hệ Khách Hàng](#24-module-garment-crm--quan-hệ-khách-hàng)
25. [Module Garment Label — In Tem & Quản Lý Pallet](#25-module-garment-label--in-tem--quản-lý-pallet)
26. [Module Garment Inventory — Kiểm Kê Kho](#26-module-garment-inventory--kiểm-kê-kho)
27. [Module Garment Print — In Ấn, Xuất Excel & Cảnh Báo Tự Động](#27-module-garment-print--in-ấn-xuất-excel--cảnh-báo-tự-động)
28. [Quản Lý Nhân Viên & Phân Quyền](#28-quản-lý-nhân-viên--phân-quyền)
29. [Module Garment Mobile — Responsive & Phê Duyệt](#29-module-garment-mobile--responsive--phê-duyệt)
30. [🔐 Nhật Ký Kiểm Soát (Audit Log)](#30-🔐-nhật-ký-kiểm-soát-audit-log)
31. [FAQ — Câu hỏi thường gặp](#31-faq--câu-hỏi-thường-gặp)

---

## 1. Giới thiệu & Đăng nhập

### 1.1 Tổng quan hệ thống

Hệ thống ERP Công Ty May được xây dựng trên nền tảng **Odoo 19.0**, bao gồm **27 module chuyên biệt** quản lý toàn bộ quy trình từ nhận đơn hàng đến xuất hàng, bao gồm nhập nguyên liệu, CRM quan hệ khách hàng, in tem QR code, quản lý pallet/thùng hàng, kiểm kê kho, quản lý nhân viên, phân quyền 4 cấp, hoàn thiện, chấm công, kế toán, kho, giặt, gia công, giao hàng, in ấn PDF, xuất Excel, cảnh báo tự động, dashboard tổng quan, mobile-responsive UI và luồng phê duyệt đơn hàng.

### 1.2 Đăng nhập

1. Mở trình duyệt → Truy cập **http://localhost:8069**
2. Nhập tài khoản:
   - **Email:** `admin`
   - **Password:** `admin`
3. Nhấn **Log in**

![Trang đăng nhập Odoo](images/01_login.png)
*Hình 1: Trang đăng nhập hệ thống*

> 💡 **Mẹo:** Bookmark trang đăng nhập để truy cập nhanh hơn.

### 1.3 Giao diện chính

Sau khi đăng nhập, bạn sẽ thấy:

- **App Launcher (Home):** Chỉ có **1 ứng dụng duy nhất** — **"Công Ty May"** chứa toàn bộ chức năng
- **Thanh menu ngang:** Các nhóm chức năng chính bên trong app (Đơn Hàng, Sản Xuất, Chất Lượng, ...)
- **Sidebar trái:** Menu phụ của nhóm đang chọn
- **Vùng nội dung chính:** Hiển thị danh sách / form / biểu đồ

![Giao diện chính sau đăng nhập](images/02_home.png)
*Hình 2: Giao diện chính sau khi đăng nhập — chỉ hiển thị app "Công Ty May"*

### 1.4 Truy cập module Công Ty May

Nhấn vào **"Công Ty May"** trên màn hình Home. Toàn bộ chức năng được tổ chức trong **9 nhóm menu** trên thanh ngang:

| # | Menu Nhóm | Chức Năng |
|---|-----------|-----------|
| 1 | **Đơn Hàng** | Đơn hàng may, Mẫu may/Style, Vải, Phụ liệu, Quản lý mẫu, Bảng tính giá thành |
| 2 | **CRM** | Lead / Cơ hội, Buyer / Khách hàng, Phản hồi / Khiếu nại |
| 3 | **Sản Xuất** | Lệnh SX, Lệnh cắt, Lệnh cắt nâng cao, Sản lượng ngày, Chuyền may, Lệnh hoàn thiện, Kế hoạch SX, Line loading, Danh sách máy, Yêu cầu bảo trì, Lệnh giặt, Đơn gia công |
| 4 | **Chất Lượng** | Phiếu kiểm tra QC, Loại lỗi, Audits, CAP (Khắc phục) |
| 5 | **Kho & Giao Hàng** | Nhập NL Mua Hàng, NL Khách Gửi (CMT), Phân bổ NL, Kiểm kê kho, Tem/QR Code, Thùng hàng, Pallet, Packing list, Nhập kho, Xuất kho, Phiếu giao hàng, Phương tiện |
| 6 | **Kế Toán** | Hóa đơn bán, Hóa đơn mua, Phiếu thanh toán, Tất cả hóa đơn |
| 7 | **Nhân Sự & Lương** | Nhân viên may, Tổ trưởng, Chấm công, Tổng hợp công tháng, Kỹ năng, Đơn nghỉ phép, Đơn giá khoán, Sản lượng CN, Bảng lương, Phiếu thưởng |
| 8 | **Báo Cáo** | Dashboard KPI, Tổng quan đơn hàng, Tiến độ SX, Đơn trễ hạn, Hiệu suất chuyền, Phân tích lỗi, Báo cáo sản xuất |
| 9 | **Cấu Hình** | Bảng màu, Bảng size, Ký hiệu giặt, Công thức giặt, Hóa chất |

![Đơn Hàng menu](images/80_menu_don_hang.png)
*Hình 2b: Menu "Đơn Hàng" — tất cả chức năng đặt hàng trong một nhóm*

![Sản Xuất menu](images/81_menu_san_xuat.png)
*Hình 2c: Menu "Sản Xuất" — bao gồm cả Giặt, Gia Công, Bảo Trì, Kế Hoạch*

![Kho & Giao Hàng menu](images/83_menu_kho.png)
*Hình 2d: Menu "Kho & Giao Hàng" — Packing, Kho và Giao Hàng gộp chung*

![Cấu Hình menu](images/87_menu_cau_hinh.png)
*Hình 2e: Menu "Cấu Hình" — Bảng màu, Bảng size, Ký hiệu giặt, Công thức, Hóa chất*

---

## 2. Sơ Đồ Tổng Quan & Luồng Nghiệp Vụ

### 2.1 Luồng Nghiệp Vụ Chính — Từ Đơn Hàng Đến Giao Hàng

```mermaid
flowchart LR
    CRM[🤝 CRM Lead\ngarment_crm] --> A[📋 Nhận Đơn Hàng\ngarment_base]
    A --> B[✂️ Thiết Kế & Mẫu\ngarment_sample]
    B --> C[💰 Tính Giá Thành\ngarment_costing]
    C --> D[📅 Lập Kế Hoạch SX\ngarment_planning]
    D --> D2[📥 Nhập Nguyên Liệu\ngarment_material]
    D2 --> E[✂️ Cắt Vải\ngarment_cutting]
    E --> F[🧵 May\ngarment_production]
    F --> G[🧼 Giặt\ngarment_washing]
    G --> H[👔 Hoàn Thiện\ngarment_finishing]
    H --> I[🔍 QC Kiểm Tra\ngarment_quality]
    I --> J[🏷️ In Tem / QR\ngarment_label]
    J --> K[📦 Đóng Gói\ngarment_packing]
    K --> L[🚚 Giao Hàng\ngarment_delivery]
    L --> M[💵 Kế Toán / Thu Tiền\ngarment_accounting]

    style CRM fill:#E91E63,color:#fff
    style A fill:#4CAF50,color:#fff
    style D2 fill:#009688,color:#fff
    style F fill:#2196F3,color:#fff
    style I fill:#FF9800,color:#fff
    style L fill:#9C27B0,color:#fff
    style M fill:#F44336,color:#fff
```

### 2.2 Sơ Đồ Liên Kết Giữa Các Module

```mermaid
graph TB
    BASE[🏭 garment_base\nĐơn Hàng, Mẫu May, Vải, Phụ Liệu]

    CRM[🤝 garment_crm\nLead, Phản Hồi, Buyer] --> BASE
    BASE --> SAMPLE[🎨 garment_sample\nQuản lý mẫu]
    BASE --> COSTING[💰 garment_costing\nTính giá thành]
    BASE --> PLANNING[📅 garment_planning\nKế hoạch SX]
    BASE --> PRODUCTION[🧵 garment_production\nLệnh SX, Chuyền May]
    BASE --> CUTTING[✂️ garment_cutting\nLệnh cắt chi tiết]
    BASE --> ACCOUNTING[💵 garment_accounting\nHóa đơn, Thanh toán]
    BASE --> WAREHOUSE[📦 garment_warehouse\nPhiếu kho]
    BASE --> DELIVERY[🚚 garment_delivery\nGiao hàng]

    PRODUCTION --> QUALITY[🔍 garment_quality\nKiểm tra QC]
    PRODUCTION --> FINISHING[👔 garment_finishing\nHoàn thiện]
    PRODUCTION --> WASHING[🧼 garment_washing\nGiặt]
    PRODUCTION --> SUBCONTRACT[🤝 garment_subcontract\nGia công]
    PRODUCTION --> PACKING[📦 garment_packing\nĐóng gói]
    PRODUCTION --> DAILY[📊 Sản lượng hàng ngày]

    PACKING --> LABEL[🏷️ garment_label\nIn Tem/QR, Pallet, Thùng]
    LABEL --> DELIVERY

    DAILY --> PAYROLL[💰 garment_payroll\nTính lương]
    HR[👥 garment_hr\nNhân viên, Chấm công, Nghỉ phép] --> PAYROLL

    MAINTENANCE[🔧 garment_maintenance\nBảo trì máy] --> PRODUCTION
    COMPLIANCE[📋 garment_compliance\nTuân thủ] -.-> BASE
    REPORT[📊 garment_report\nBáo cáo] -.-> PRODUCTION
    REPORT -.-> QUALITY
    MATERIAL[📥 garment_material\nNhập NL, Phân bổ] --> WAREHOUSE
    MATERIAL --> PRODUCTION
    INVENTORY[📋 garment_inventory\nKiểm kê kho] --> WAREHOUSE
    DASHBOARD[📊 garment_dashboard\nDashboard KPI] -.-> PRODUCTION
    DASHBOARD -.-> REPORT

    style BASE fill:#4CAF50,color:#fff
    style PRODUCTION fill:#2196F3,color:#fff
    style PAYROLL fill:#FF9800,color:#fff
    style ACCOUNTING fill:#F44336,color:#fff
    style MATERIAL fill:#009688,color:#fff
    style CRM fill:#E91E63,color:#fff
    style LABEL fill:#FF5722,color:#fff
    style DASHBOARD fill:#9C27B0,color:#fff
```

### 2.3 Luồng Chứng Từ — Document Flow

```mermaid
flowchart TB
    PO[📋 Đơn Hàng May\nGarment Order] --> PROD[🏭 Lệnh Sản Xuất\nProduction Order]
    PO --> CUT[✂️ Lệnh Cắt\nCutting Order]
    PROD --> DO[📊 Sản Lượng Ngày\nDaily Output]
    CUT --> PROD
    PROD --> QC[🔍 Phiếu QC\nQC Inspection]
    PROD --> FN[👔 Lệnh Hoàn Thiện\nFinishing Order]
    PROD --> WO[🧼 Lệnh Giặt\nWash Order]
    PROD --> SO[🤝 Đơn Gia Công\nSubcontract Order]
    FN --> PL[📦 Packing List]
    QC --> PL
    PL --> DL[🚚 Phiếu Giao Hàng\nDelivery Order]
    DL --> INV[💵 Hóa Đơn\nInvoice]
    INV --> PAY[💳 Phiếu Thanh Toán\nPayment]

    MR[📥 Phiếu Nhập NL\nMaterial Receipt] --> PO
    MR --> MA[📤 Phân Bổ NL\nMaterial Allocation]
    MA --> PROD

    SM_IN[📥 Phiếu Nhập Kho] --> PO
    PO --> SM_OUT[📤 Phiếu Xuất Kho]

    DO --> WAGE[💰 Bảng Lương\nWage Calculation]
    ATT[🕐 Chấm Công\nAttendance] --> WAGE

    style PO fill:#4CAF50,color:#fff
    style PROD fill:#2196F3,color:#fff
    style INV fill:#F44336,color:#fff
    style WAGE fill:#FF9800,color:#fff
    style MR fill:#009688,color:#fff
```

### 2.4 Trạng Thái Đơn Hàng (Order Lifecycle)

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

## 3. Module Garment Base — Quản lý Cơ Sở

Module nền tảng quản lý tất cả dữ liệu chung của công ty may.

### 3.1 Quản lý Vải (Fabric)

**Đường dẫn:** `Công Ty May → Đơn Hàng → Vải`

#### Thêm mới loại vải:

1. Nhấn **"Tạo"** (nút xanh góc trái)
2. Điền thông tin vải
3. Tab **Nhà Cung Cấp:** Thêm nhà cung cấp vải
4. Tab **Màu Có Sẵn:** Chọn màu vải có sẵn
5. Nhấn **"Lưu"**

![Danh sách Vải](images/05_fabrics.png)
*Hình 2e: Danh sách quản lý vải*

#### Bảng giải thích trường — Vải (garment.fabric):

| Trường | Kiểu | Ý Nghĩa | Ví dụ |
|--------|------|---------|-------|
| **Tên Vải** | Char | Tên gọi đầy đủ của loại vải | `Cotton Oxford 100%` |
| **Mã Vải** | Char | Mã nội bộ duy nhất để quản lý | `FAB-001` |
| **Loại Vải** | Selection | Phân loại: Cotton, Polyester, Silk, Denim, Linen, Blend, Knit, Nylon, Rayon, Spandex, Khác | `cotton` |
| **Thành Phần** | Char | Tỷ lệ sợi | `60% Cotton 40% Polyester` |
| **Khổ Vải (cm)** | Float | Chiều rộng cuộn vải, ảnh hưởng đến sơ đồ cắt | `150` |
| **Định Lượng (g/m²)** | Float | Trọng lượng/m², quyết định loại kim may | `140` |
| **Giá / Mét** | Float | Đơn giá nhập vải từ nhà cung cấp | `45000` |
| **Đặt Hàng Tối Thiểu** | Float | MOQ (Minimum Order Quantity) từ NCC | `500` |
| **Thời Gian Giao (ngày)** | Integer | Lead time, ảnh hưởng kế hoạch SX | `14` |
| **Độ Co Rút (%)** | Float | % co rút sau giặt, cần tính thêm khi cắt | `3.0` |

---

### 3.2 Quản lý Phụ Liệu (Accessories)

**Đường dẫn:** `Công Ty May → Đơn Hàng → Phụ Liệu`

![Danh sách Phụ Liệu](images/06_accessories.png)
*Hình 2f: Danh sách quản lý phụ liệu*

#### Bảng giải thích trường — Phụ Liệu (garment.accessory):

| Trường | Kiểu | Ý Nghĩa | Ví dụ |
|--------|------|---------|-------|
| **Tên Phụ Liệu** | Char | Tên phụ liệu (bắt buộc) | `Nút nhựa 4 lỗ 15mm` |
| **Mã Phụ Liệu** | Char | Mã nội bộ duy nhất (bắt buộc) | `ACC-001` |
| **Loại Phụ Liệu** | Selection | button (Nút/Cúc), zipper (Khóa Kéo), thread (Chỉ May), label (Nhãn Mác), elastic (Thun/Dây Chun), lace (Ren/Đăng Ten), ribbon (Ruy Băng), hook (Móc/Khuy), padding (Mex/Lót), packaging (Bao Bì/Đóng Gói), hanger (Móc Treo), tag (Thẻ Bài), other (Khác) | `button` |
| **Đơn Vị Tính** | Many2one → uom.uom | Đơn vị tính từ danh mục UoM (bắt buộc) | `Cái` |
| **Màu Có Sẵn** | Many2many → garment.color | Danh sách màu sắc có sẵn cho phụ liệu | `Trắng, Đen, Đỏ` |
| **Kích Thước** | Char | Kích thước chi tiết | `15mm` |
| **Chất Liệu** | Char | Vật liệu phụ liệu | `Nhựa ABS` |
| **Nhà Cung Cấp** | Many2many → res.partner | Danh sách nhà cung cấp phụ liệu | `Công ty ABC, Công ty XYZ` |
| **Sản Phẩm Liên Kết** | Many2one → product.product | Liên kết sản phẩm Odoo để quản lý tồn kho | `[ACC-001] Nút nhựa 4 lỗ` |
| **Giá** | Float | Đơn giá mua | `500` |

---

### 3.3 Quản lý Mẫu May / Style

**Đường dẫn:** `Công Ty May → Đơn Hàng → Mẫu May / Style`

![Danh sách Mã Hàng / Style](images/04_styles.png)
*Hình 3: Danh sách mã hàng (Style) trong hệ thống*

![Chi tiết Mẫu May](images/51_style_detail.png)
*Hình 4: Màn hình chi tiết mẫu may — form view đầy đủ*

#### Bảng giải thích trường — Mẫu May (garment.style):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Tên Mẫu** | Char | ✅ | Tên gọi mẫu may | `Áo Polo nam cổ đứng` |
| **Mã Mẫu (Style No.)** | Char | ✅ | Mã duy nhất do khách/nội bộ đặt | `STY-2026-001` |
| **Loại Sản Phẩm** | Selection | ✅ | Phân loại sản phẩm: shirt (Áo Sơ Mi), tshirt (Áo Thun), polo (Polo), jacket (Jacket), blazer (Vest), pants (Quần Tây), jeans (Jeans), shorts (Short), skirt (Chân Váy), dress (Đầm), suit (Bộ Vest), uniform (Đồng Phục), sportswear (Thể Thao), underwear (Đồ Lót), sleepwear (Đồ Ngủ), childwear (Trẻ Em), other (Khác) | `polo` |
| **Mùa** | Selection | | ss (Xuân Hè), aw (Thu Đông), all (Quanh Năm) | `ss` |
| **Giới Tính** | Selection | | male / female / unisex / kids | `unisex` |
| **Khách Hàng** | Many2one | | Buyer đặt hàng mẫu này | `H&M Vietnam` |
| **Độ Khó** | Selection | | easy / medium / hard / very_hard — ảnh hưởng đến SAM | `medium` |
| **Định Mức Vải (m/sp)** | Float | | Số mét vải cần cho 1 sản phẩm | `1.85` |
| **Thời Gian May (phút/sp)** | Float | | Thời gian may trung bình 1 SP | `18` |
| **SAM** | Float | | Standard Allowed Minutes — thời gian chuẩn cho phép (phút) | `15.5` |
| **Vải Sử Dụng** | Many2many | | Gắn các loại vải cho mẫu này | `Cotton Oxford, Lót Polyester` |
| **Phụ Liệu Sử Dụng** | Many2many | | Gắn phụ liệu cần thiết | `Nút nhựa, Khóa kéo, Nhãn` |
| **Bảng Size** | Many2many | | Size sản xuất cho mẫu này | `S, M, L, XL, XXL` |
| **Bảng Màu** | Many2many | | Màu sản xuất cho mẫu này | `Trắng, Đen, Navy` |
| **Hướng Dẫn Giặt Ủi** | Text | | Wash care instruction | `Giặt máy 30°C, không tẩy` |
| **Ký Hiệu Giặt** | Many2many | | Ký hiệu giặt ISO trên nhãn | `W30, DNB, MI` |
| **Tech Pack** | Binary | | File PDF/JPG tài liệu kỹ thuật | Upload file |
| **File Rập / Pattern** | Binary | | File rập cắt | Upload file |
| **Hình Mặt Trước / Sau** | Binary | | Hình ảnh sản phẩm | Upload ảnh |
| **Trạng Thái** | Selection | | draft → design → sample → approved → production → discontinued | `approved` |

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

---

### 3.4 Quản lý Đơn Hàng

**Đường dẫn:** `Công Ty May → Đơn Hàng → Đơn Hàng May`

![Danh sách Đơn Hàng May](images/03_garment_orders.png)
*Hình 5: Danh sách đơn hàng may*

![Chi tiết Đơn Hàng](images/50_order_detail.png)
*Hình 6: Màn hình chi tiết đơn hàng — form view với đầy đủ thông tin*

#### Bảng giải thích trường — Đơn Hàng (garment.order):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Đơn Hàng** | Char | ✅ | Mã tự động (GO-2026-XXXXX) | `GO-2026-00001` |
| **Khách Hàng** | Many2one | ✅ | Buyer đặt hàng (có rank customer) | `H&M Vietnam` |
| **PO Khách Hàng** | Char | | Mã PO từ phía khách hàng | `PO-HM-2026-458` |
| **Mẫu May** | Many2one | ✅ | Style sản xuất | `Áo Polo nam cổ đứng` |
| **Ngày Đặt Hàng** | Date | | Ngày ký hợp đồng / nhận PO | `2026-01-15` |
| **Ngày Giao Hàng** | Date | | Deadline giao hàng | `2026-03-30` |
| **Đơn Giá FOB** | Float | | Giá FOB cho 1 sản phẩm | `8.50` (USD) |
| **Tiền Tệ** | Many2one | | Loại tiền (mặc định = tiền công ty) | `USD` |
| **Phương Thức Thanh Toán** | Selection | | tt (T/T Chuyển Khoản), lc (L/C Thư Tín Dụng), dp (D/P), da (D/A) | `tt` |
| **Điều Kiện Giao Hàng** | Selection | | fob (FOB), cif (CIF), exw (EXW), cfr (CFR) | `fob` |
| **Cảng Đến** | Char | | Cảng đích cho hàng xuất khẩu | `Hamburg, Germany` |
| **Shipping Mark** | Text | | Ký hiệu đóng gói trên thùng hàng | `H&M / PO-458 / ...` |
| **Tổng Số Lượng** | Integer | 🔄 | Tự tính từ tổng các dòng chi tiết | `10,000` |
| **Tổng Tiền** | Float | 🔄 | Tự tính = Tổng SL × Đơn giá | `85,000` |
| **Đúng Hạn** | Boolean | 🔄 | Tự tính từ ngày giao so với hôm nay | ✅/❌ |
| **Số Ngày Còn Lại** | Integer | 🔄 | Tự tính số ngày đến deadline | `45` |
| **Trạng Thái** | Selection | | 11 trạng thái: draft, confirmed, material, cutting, sewing, finishing, qc, packing, shipped, done, cancelled | `confirmed` |

> 🔄 = Trường tự động tính, không cần nhập tay.

#### Chi tiết đơn hàng (Order Line):

| Trường | Ý Nghĩa |
|--------|---------|
| **Màu** | Màu sản phẩm trong đơn |
| **Size** | Size sản phẩm |
| **Số Lượng** | Số lượng đặt cho combo màu-size |
| **Đơn Giá** | Lấy từ đơn giá FOB của đơn hàng |
| **Thành Tiền** | Tự tính = Số lượng × Đơn giá |

---

## 4. Module Garment Production — Sản Xuất

Module quản lý sản xuất: chuyền may, lệnh sản xuất, sản lượng hàng ngày.

![Sản Xuất menu](images/81_menu_san_xuat.png)
*Hình 7b: Menu Sản Xuất — bao gồm cả Giặt, Gia Công, Bảo Trì, Kế Hoạch SX*

### 4.1 Chuyền May (Sewing Line)

**Đường dẫn:** `Công Ty May → Sản Xuất → Chuyền May`

![Danh sách Chuyền May](images/10_sewing_lines.png)
*Hình 7: Danh sách chuyền may*

![Chi tiết Chuyền May](images/72_sewing_detail.png)
*Hình 8: Form view chi tiết chuyền may*

#### Bảng giải thích trường — Chuyền May (garment.sewing.line):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Tên Chuyền** | Char | ✅ | Tên gọi chuyền | `Chuyền May 1` |
| **Mã Chuyền** | Char | ✅ | Mã duy nhất | `LINE-01` |
| **Loại Chuyền** | Selection | ✅ | sewing (May), cutting (Bàn Cắt), finishing (Hoàn Thiện), ironing (Ủi), packing (Đóng Gói) | `sewing` |
| **Chuyền Trưởng** | Many2one | | Người quản lý chuyền | `Nguyễn Văn A` |
| **Công Nhân** | Many2many | | Danh sách CN trong chuyền | 35 người |
| **Số Công Nhân** | Integer | 🔄 | Tự tính từ danh sách CN | `35` |
| **Số Máy** | Integer | | Tổng số máy trong chuyền | `40` |
| **Năng Suất / Ngày (sp)** | Integer | | Capacity dự kiến | `800` |
| **Hiệu Suất (%)** | Float | | Hiệu suất trung bình | `80.0` |
| **Vị Trí / Nhà Xưởng** | Char | | Vị trí vật lý | `Nhà xưởng A - Tầng 2` |
| **Trạng Thái** | Selection | | active / maintenance / inactive | `active` |

---

### 4.2 Lệnh Sản Xuất (Production Order)

**Đường dẫn:** `Công Ty May → Sản Xuất → Lệnh Sản Xuất`

![Danh sách Lệnh SX](images/07_production_orders.png)
*Hình 9: Danh sách lệnh sản xuất*

![Chi tiết Lệnh SX](images/52_production_detail.png)
*Hình 10: Form view chi tiết lệnh sản xuất — hiển thị tiến độ, sản lượng*

#### Bảng giải thích trường — Lệnh Sản Xuất (garment.production.order):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Lệnh SX** | Char | ✅ | Mã tự động (PO-2026-XXXXX) | `PO-2026-00001` |
| **Đơn Hàng May** | Many2one | ✅ | Liên kết đến đơn hàng gốc | `GO-2026-00001` |
| **Mẫu May** | Many2one | 🔄 | Lấy từ đơn hàng may (related) | `Áo Polo nam` |
| **Khách Hàng** | Many2one | 🔄 | Lấy từ đơn hàng (related) | `H&M Vietnam` |
| **Chuyền May** | Many2one | | Phân chuyền may thực hiện | `Chuyền May 1` |
| **SL Kế Hoạch** | Integer | ✅ | Số lượng cần sản xuất | `5,000` |
| **SL Hoàn Thành** | Integer | 🔄 | Tự tính từ sản lượng ngày | `3,200` |
| **SL Lỗi** | Integer | 🔄 | Tự tính từ sản lượng ngày | `45` |
| **Tỷ Lệ Hoàn Thành (%)** | Float | 🔄 | = SL Hoàn Thành / SL Kế Hoạch × 100 | `64.0%` |
| **Ngày Bắt Đầu** | Date | | Tự set khi chuyển trạng thái | `2026-02-01` |
| **Ngày Kết Thúc Dự Kiến** | Date | | Deadline cho lệnh SX | `2026-02-28` |
| **Ngày Kết Thúc Thực Tế** | Date | | Tự set khi hoàn thành | `2026-02-26` |
| **SAM** | Float | 🔄 | Lấy từ mẫu may (related) | `15.5` |
| **Trạng Thái** | Selection | | draft → confirmed → in_progress → done / cancelled | `in_progress` |

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

### 4.3 Sản Lượng Hàng Ngày (Daily Output)

**Đường dẫn:** `Công Ty May → Sản Xuất → Sản Lượng Hàng Ngày`

![Sản Lượng Hàng Ngày](images/09_daily_output.png)
*Hình 11: Danh sách sản lượng hàng ngày*

![Chi tiết Sản Lượng](images/71_output_detail.png)
*Hình 12: Form view chi tiết sản lượng hàng ngày*

#### Bảng giải thích trường — Sản Lượng (garment.daily.output):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Lệnh Sản Xuất** | Many2one | ✅ | Liên kết đến lệnh SX | `PO-2026-00001` |
| **Chuyền May** | Many2one | 🔄 | Lấy từ lệnh SX (related) | `Chuyền May 1` |
| **Ngày** | Date | ✅ | Ngày nhập sản lượng | `2026-02-15` |
| **Ca Làm Việc** | Selection | ✅ | morning (Ca Sáng), afternoon (Ca Chiều), night (Ca Tối), overtime (Tăng Ca) | `morning` |
| **Mục Tiêu (sp)** | Integer | | SL mục tiêu trong ca | `200` |
| **Sản Lượng Đạt (sp)** | Integer | ✅ | SL thực tế hoàn thành | `185` |
| **Số Lượng Lỗi (sp)** | Integer | | SL lỗi phát hiện | `8` |
| **Sửa Lại (sp)** | Integer | | SL sửa chữa (rework) | `5` |
| **Số CN Làm Việc** | Integer | | Số công nhân trong ca | `35` |
| **Giờ Làm Việc** | Float | | Giờ làm việc thực tế | `8.0` |
| **Hiệu Suất (%)** | Float | 🔄 | = SL Đạt / Mục Tiêu × 100 | `92.5%` |
| **Tỷ Lệ Lỗi (%)** | Float | 🔄 | = Lỗi / (Đạt + Lỗi) × 100 | `4.1%` |

---

## 5. Module Garment Quality — Chất Lượng

Module quản lý kiểm tra chất lượng (QC) trong sản xuất.

### 5.1 Phiếu Kiểm Tra QC (QC Inspection)

**Đường dẫn:** `Công Ty May → Chất Lượng → Phiếu Kiểm Tra QC`

![Chất Lượng menu](images/82_menu_chat_luong.png)
*Hình 12b: Menu Chất Lượng — QC, Audits và CAP gộp chung*

![Danh sách QC](images/22_qc_inspections.png)
*Hình 13: Danh sách phiếu kiểm tra QC*

![Chi tiết QC](images/53_qc_detail.png)
*Hình 14: Form view chi tiết phiếu QC — kết quả kiểm tra*

#### Bảng giải thích trường — QC Inspection (garment.qc.inspection):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã Phiếu** | Char | ✅ | Mã tự động (QC-XXXXX) | `QC-2026-00001` |
| **Lệnh Sản Xuất** | Many2one | ✅ | Lệnh SX được kiểm tra | `PO-2026-00001` |
| **Loại QC** | Selection | ✅ | inline (Kiểm Tra Chuyền), endline (Kiểm Cuối Chuyền), final (Kiểm Cuối Cùng), aql (Kiểm AQL), fabric (Kiểm Vải), washing (Kiểm Sau Giặt) | `final` |
| **Mức AQL** | Selection | | 1.0 / 1.5 / 2.5 / 4.0 / 6.5 | `2.5` |
| **Ngày Kiểm Tra** | Date | ✅ | Ngày thực hiện | `2026-02-20` |
| **QC Inspector** | Many2one | | Nhân viên QC thực hiện | `Lê Thị QC` |
| **SL Kiểm Tra** | Integer | ✅ | Số lượng mẫu kiểm | `200` |
| **SL Đạt** | Integer | | SL đạt yêu cầu | `190` |
| **SL Lỗi** | Integer | | SL phát hiện lỗi | `10` |
| **Tỷ Lệ Lỗi (%)** | Float | 🔄 | Tự tính | `5.0%` |
| **Kết Quả** | Selection | | pass (Đạt), fail (Không Đạt), conditional (Đạt Có Điều Kiện) | `pass` |
| **Chi Tiết Lỗi** | One2many | | Danh sách lỗi phát hiện | Bảng lỗi |
| **Trạng Thái** | Selection | | draft → in_progress → done / cancelled | `done` |

---

## 6. Module Garment Costing — Tính Giá Thành

**Đường dẫn:** `Công Ty May → Đơn Hàng → Bảng Tính Giá Thành`

![Danh sách Bảng Tính Giá](images/12_costing.png)
*Hình 15: Danh sách bảng tính giá thành*

![Chi tiết Bảng Tính Giá](images/56_costing_detail.png)
*Hình 16: Form view bảng tính giá thành — breakdown chi phí*

### 6.1 Bảng Tính Giá Thành (Cost Sheet)

#### Bảng giải thích trường — Cost Sheet (garment.cost.sheet):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã** | Char | ✅ | Mã tự động (CS-XXXXX) | `CS-2026-00001` |
| **Mẫu May** | Many2one | ✅ | Style được tính giá | `Áo Polo nam` |
| **Khách Hàng** | Many2one | ✅ | Buyer yêu cầu | `H&M Vietnam` |
| **Đơn Hàng** | Many2one | | Đơn hàng may liên kết | `GO-2026-00001` |
| **Ngày** | Date | ✅ | Ngày lập bảng giá | `2026-01-15` |
| **Tiền Tệ** | Many2one | ✅ | Loại tiền tính giá | `USD` |
| **Loại Tính Giá** | Selection | ✅ | fob (FOB), cm (CM — Cut & Make), cmt (CMT — Cut, Make & Trim) | `fob` |
| **SL Đặt Hàng** | Integer | ✅ | Số lượng đơn hàng | `10,000` |
| **Chi Phí Vải** | One2many | | Dòng chi phí vải (từ Cost Line, cost_type=fabric) | Bảng chi tiết |
| **Chi Phí PL** | One2many | | Dòng chi phí phụ liệu (cost_type=accessory) | Bảng chi tiết |
| **Chi Phí Đóng Gói** | One2many | | Dòng chi phí đóng gói (cost_type=packing) | Bảng chi tiết |
| **Chi Phí Khác** | One2many | | Dòng chi phí khác (cost_type=other) | Bảng chi tiết |
| **Tổng NVL/SP** | Monetary | 🔄 | = Vải + PL + Đóng Gói + Khác (per pc) | `3.50` |
| **SMV** | Float | | Standard Minute Value — thời gian may 1 SP (phút) | `12.5` |
| **Hiệu Suất Mục Tiêu (%)** | Float | | Target efficiency | `60.0` |
| **Đơn Giá CM/Phút** | Monetary | | Giá gia công mỗi phút | `0.05` |
| **Chi Phí CM/SP** | Monetary | 🔄 | = SMV ÷ (Efficiency/100) × CM Rate | `1.04` |
| **Chi Phí Giặt/SP** | Monetary | | Washing cost per piece | `0.30` |
| **Chi Phí Thêu/SP** | Monetary | | Embroidery cost per piece | `0.20` |
| **Chi Phí In/SP** | Monetary | | Printing cost per piece | `0.00` |
| **Chi Phí Test/SP** | Monetary | | Testing cost per piece | `0.10` |
| **Tổng Gia Công/SP** | Monetary | 🔄 | = Giặt + Thêu + In + Test | `0.60` |
| **Hoa Hồng (%)** | Float | | Commission % (chỉ cho FOB) | `3.0` |
| **Freight/SP** | Monetary | | Inland freight per piece | `0.15` |
| **Overhead (%)** | Float | | Overhead % | `5.0` |
| **Lợi Nhuận (%)** | Float | | Profit margin % | `5.0` |
| **Giá Thành/SP** | Monetary | 🔄 | Cost price per piece (tuỳ loại FOB/CM/CMT) | `5.29` |
| **Giá Bán/SP** | Monetary | 🔄 | Selling price per piece (gồm overhead + profit) | `6.80` |
| **Tổng Giá Trị Đơn Hàng** | Monetary | 🔄 | = Giá Bán × SL Đặt Hàng | `68,000` |
| **Revision** | Integer | | Số lần sửa đổi bảng giá | `0` |
| **Trạng Thái** | Selection | | draft → confirmed → approved → revised → cancelled | `approved` |

> 💡 **Công thức tính giá:**
> - **FOB:** Cost = NVL + CM + Gia Công + Overhead + Freight → Selling = Cost + Commission + Profit
> - **CM:** Cost = CM only → Selling = CM + Overhead + Profit
> - **CMT:** Cost = PL + CM + Gia Công → Selling = Cost + Overhead + Profit

### 6.2 Chi Tiết Chi Phí (Cost Line — garment.cost.line):

| Trường | Ý Nghĩa |
|--------|---------|
| **Loại Chi Phí** | fabric (Vải) / accessory (Phụ Liệu) / packing (Đóng Gói) / other (Khác) |
| **Sản Phẩm** | Sản phẩm liên kết (tuỳ chọn) |
| **Mô Tả** | Mô tả chi tiết (VD: Vải Cotton Oxford 150cm) |
| **ĐVT** | Đơn vị tính (từ danh mục UoM) |
| **Định Mức/SP** | Lượng tiêu hao cho 1 sản phẩm |
| **Đơn Giá** | Giá mua |
| **Hao Hụt (%)** | Phần trăm hao hụt nguyên liệu |
| **Thành Tiền/SP** | 🔄 = Định Mức × (1 + Hao Hụt%) × Đơn Giá |
| **Nhà Cung Cấp** | NCC cung cấp nguyên liệu |

---

## 7. Module Garment Sample — Quản Lý Mẫu

**Đường dẫn:** `Công Ty May → Đơn Hàng → Quản Lý Mẫu`

![Danh sách Mẫu](images/11_samples.png)
*Hình 17: Danh sách quản lý mẫu*

![Chi tiết Mẫu](images/55_sample_detail.png)
*Hình 18: Form view chi tiết phiếu mẫu*

### 7.1 Phiếu Mẫu (Sample)

#### Bảng giải thích trường — Mẫu (garment.sample):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã Mẫu** | Char | ✅ | Mã tự động (SM-XXXXX) | `SM-2026-00001` |
| **Mẫu May (Style)** | Many2one | ✅ | Mẫu may liên quan | `Áo Polo nam` |
| **Khách Hàng** | Many2one | ✅ | Buyer yêu cầu mẫu | `H&M Vietnam` |
| **Loại Mẫu** | Selection | ✅ | proto (Mẫu Prototype), fit (Mẫu Fit), size_set (Mẫu Size Set), salesman (Mẫu Salesman), pp (Mẫu PP), top (Mẫu TOP), shipment (Mẫu Shipment), ad_hoc (Mẫu Ad-hoc) | `pp` |
| **Số Lượng** | Integer | ✅ | Số SP mẫu cần làm | `6` |
| **Sizes** | Many2many | | Các size mẫu | `S, M, L` |
| **Màu** | Many2many | | Các màu mẫu | `Navy, White` |
| **Ngày Yêu Cầu** | Date | | Ngày yêu cầu làm mẫu | `2026-01-10` |
| **Hạn Giao Mẫu** | Date | ✅ | Deadline giao mẫu cho buyer | `2026-01-25` |
| **Ngày Gửi Mẫu** | Date | | Ngày thực tế gửi mẫu | `2026-01-23` |
| **Ngày Duyệt** | Date | | Ngày buyer duyệt | `2026-01-28` |
| **Người Phụ Trách** | Many2one | | User chịu trách nhiệm | `Admin` |
| **Thông Tin Vải** | Text | | Thông tin vải sử dụng | `Cotton Oxford 150cm` |
| **Ghi Chú NVL** | Text | | Ghi chú nguyên vật liệu | |
| **Ảnh Mặt Trước** | Binary | | Ảnh mẫu mặt trước | 📷 |
| **Ảnh Mặt Sau** | Binary | | Ảnh mẫu mặt sau | 📷 |
| **Ảnh Chi Tiết** | Binary | | Ảnh chi tiết mẫu | 📷 |
| **Comments** | One2many | | Phản hồi từ buyer (model garment.sample.comment) | Bảng comment |
| **Revision** | Integer | | Số lần chỉnh sửa | `0` |
| **Courier / Tracking** | Char | | Thông tin vận chuyển mẫu | `DHL 1234567890` |
| **Trạng Thái** | Selection | | draft → in_progress → submitted → approved / approved_with_comments / rejected / cancelled | `approved` |

#### Bảng giải thích — Comment Mẫu (garment.sample.comment):

| Trường | Kiểu | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|---------|-----------------|
| **Ngày** | Datetime | Ngày comment | `2026-01-28 10:00` |
| **Người Viết** | Many2one | User tạo comment | `Admin` |
| **Loại** | Selection | buyer (Buyer Comment), internal (Internal), correction (Cần Chỉnh Sửa) | `buyer` |
| **Nội Dung** | Text | Nội dung phản hồi | `Adjust collar width` |
| **Ảnh Đính Kèm** | Binary | Ảnh minh hoạ | 📷 |
| **Revision** | Integer | Revision của mẫu lúc comment | `1` |

#### Workflow mẫu:

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
    Đang_Làm --> Đã_Hủy: Hủy
    Đã_Gửi --> Đã_Hủy: Hủy
```

> 💡 Trạng thái **Duyệt Có Chỉnh Sửa** (`approved_with_comments`): Buyer đồng ý nhưng yêu cầu sửa nhỏ trước khi sản xuất. Có thể "Làm lại" để tạo revision mới.

---

## 8. Module Garment Cutting — Cắt Nâng Cao

**Đường dẫn:** `Công Ty May → Sản Xuất → Lệnh Cắt`

![Lệnh Cắt](images/08_cutting_orders.png)
*Hình 19: Danh sách lệnh cắt*

![Lệnh Cắt Nâng Cao](images/13_cutting_advanced.png)
*Hình 19b: Danh sách lệnh cắt nâng cao (module garment_cutting)*

![Chi tiết Lệnh Cắt](images/57_cutting_detail.png)
*Hình 19c: Form view chi tiết lệnh cắt nâng cao*

### 8.1 Lệnh Cắt (Cutting Order)

#### Bảng giải thích trường — Lệnh Cắt Nâng Cao (garment.cutting.order.adv):

| Trường | Kiểu | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|---------|-----------------|
| **Số Lệnh Cắt** | Char | Mã tự động | `CO-2026-00001` |
| **Lệnh Sản Xuất** | Many2one | Liên kết lệnh SX (bắt buộc) | `PO-2026-00001` |
| **Đơn Hàng May** | Many2one | Tự lấy từ lệnh SX (related) | `GO-2026-00001` |
| **Mẫu May** | Many2one | Tự lấy từ lệnh SX (related) | `Áo Polo nam` |
| **Ngày Cắt** | Date | Ngày thực hiện cắt (bắt buộc) | `2026-02-01` |
| **Chiều Dài Sơ Đồ (m)** | Float | Marker Length — chiều dài sơ đồ cắt | `12.50` |
| **Chiều Rộng Sơ Đồ (cm)** | Float | Marker Width | `150` |
| **Hiệu Suất Sơ Đồ (%)** | Float | Marker Efficiency — tỷ lệ sử dụng vải (0–100%) | `85.5` |
| **Vải** | Many2one | Vải sử dụng | `Cotton Oxford` |
| **Màu Vải** | Char | Màu sắc lô vải cắt | `Trắng` |
| **Lớp Trải** | One2many | Chi tiết các lớp trải vải | Bảng lớp |
| **Tổng Lớp Trải** | Integer | Tự tính từ số lớp (computed) | `80` |
| **Tổng Vải Sử Dụng (m)** | Float | Tự tính = tổng length các lớp (computed) | `1,000` |
| **Bundle** | One2many | Chi tiết các bó cắt | Bảng bundle |
| **Tổng Bundle** | Integer | Tự tính (computed) | `25` |
| **Tổng SP Cắt** | Integer | Tự tính từ bundle quantity (computed) | `4,980` |
| **SP Lỗi** | Integer | Số SP lỗi khi cắt | `5` |
| **Hao Hụt (kg)** | Float | Trọng lượng vải thừa | `2.5` |
| **Thợ Cắt** | Many2one → hr.employee | Người thực hiện cắt | `Nguyễn Văn Cắt` |
| **Bàn Cắt** | Char | Số bàn cắt | `Bàn 3` |
| **Trạng Thái** | Selection | draft → spreading → cutting → numbering → done / cancelled | `done` |

### 8.2 Lớp Trải Vải (Cutting Layer — garment.cutting.layer):

| Trường | Kiểu | Ý Nghĩa | Ví dụ |
|--------|------|---------|-------|
| **Số Thứ Tự** | Integer | Sequence — số thứ tự lớp trải | `10` |
| **Số Cuộn Vải** | Char | Roll No. — mã cuộn vải sử dụng | `ROLL-001` |
| **Lô Vải** | Many2one → stock.lot | Lot vải trong kho Odoo | `LOT-2026-001` |
| **Chiều Dài (m)** | Float | Chiều dài vải trải trong lớp (bắt buộc) | `12.50` |
| **Shade / Lô Màu** | Char | Số lô màu của cuộn vải | `Shade A` |
| **Lỗi Phát Hiện** | Integer | Số lỗi vải phát hiện trong lớp | `2` |
| **Điểm Nối** | Integer | Số điểm nối (splice) trong lớp | `1` |
| **Ghi Chú** | Char | Ghi chú thêm | `Vải tốt` |

### 8.3 Bó Hàng (Bundle — garment.cutting.bundle):

| Trường | Kiểu | Ý Nghĩa | Ví dụ |
|--------|------|---------|-------|
| **Số Bundle** | Char | Mã bó hàng (unique trong lệnh cắt, bắt buộc) | `B-001` |
| **Size** | Many2one → garment.size | Size cắt (bắt buộc) | `M` |
| **Màu** | Many2one → garment.color | Màu sắc | `Trắng` |
| **Số Lượng (SP)** | Integer | Số sản phẩm trong bó (bắt buộc) | `40` |
| **Từ Lớp** | Integer | Lớp trải bắt đầu | `1` |
| **Đến Lớp** | Integer | Lớp trải kết thúc | `40` |
| **Đã Phát Chuyền** | Boolean | Đã phát xuống chuyền may chưa | ✅/❌ |
| **Ngày Phát** | Date | Ngày phát cho chuyền may | `2026-02-02` |
| **Chuyền May** | Many2one → garment.sewing.line | Chuyền may nhận bó hàng | `Chuyền 1` |
| **Ghi Chú** | Char | Ghi chú | `Bó đầu tiên` |

#### Workflow lệnh cắt:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đang_Trải_Vải: Bắt đầu trải
    Đang_Trải_Vải --> Đang_Cắt: Bắt đầu cắt
    Đang_Cắt --> Đánh_Số_Bó_Hàng: Đánh số / Bó
    Đánh_Số_Bó_Hàng --> Hoàn_Thành: Hoàn thành
    Nháp --> Đã_Hủy: Hủy
    Đang_Trải_Vải --> Đã_Hủy: Hủy
    Đang_Cắt --> Đã_Hủy: Hủy
    Đánh_Số_Bó_Hàng --> Đã_Hủy: Hủy
```

> 💡 **Quy trình cắt:** Nháp → Trải vải (thêm lớp trải) → Cắt → Đánh số / Bó hàng (tạo bundle) → Hoàn thành. Không thể hoàn thành nếu chưa có bundle.

---

## 9. Module Garment Packing — Đóng Gói & Xuất Hàng

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng → Packing List`

![Packing List](images/24_packing.png)
*Hình 20: Danh sách packing list*

![Chi tiết Packing](images/60_packing_detail.png)
*Hình 21: Form view chi tiết packing list*

### 9.1 Packing List

#### Bảng giải thích trường — Packing List (garment.packing.list):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã** | Char | ✅ | Mã tự động (PL-XXXXX) | `PL-2026-00001` |
| **Đơn Hàng May** | Many2one | | Đơn hàng đóng gói | `GO-2026-00001` |
| **Khách Hàng** | Many2one | ✅ | Buyer | `H&M Vietnam` |
| **Mẫu May** | Many2one | | Style sản phẩm | `Áo Polo nam` |
| **Ngày Đóng Gói** | Date | | Ngày đóng gói | `2026-02-28` |
| **PO Number** | Char | | Số PO từ buyer | `PO-2026-ABC` |
| **Cảng Đến** | Char | | Destination port | `Hamburg` |
| **Phương Thức Vận Chuyển** | Selection | | sea (Đường Biển), air (Đường Hàng Không), courier (Chuyển Phát) | `sea` |
| **ETD** | Date | | Ngày xuất hàng dự kiến | `2026-03-05` |
| **ETA** | Date | | Ngày đến dự kiến | `2026-03-25` |
| **Tàu / Chuyến Bay** | Char | | Tên tàu hoặc chuyến bay | `MAERSK SEALAND` |
| **Số B/L** | Char | | Số vận đơn (Bill of Lading) | `BL-12345` |
| **Số Container** | Char | | Số container | `MSKU1234567` |
| **Loại Đóng Gói** | Selection | | solid (Solid Pack), ratio (Ratio Pack), assorted (Assorted Pack) | `ratio` |
| **Dòng Carton** | One2many | | Chi tiết từng thùng | Bảng carton |
| **Tổng Thùng** | Integer | 🔄 | Tổng số thùng carton | `250` |
| **Tổng SL** | Integer | 🔄 | Tổng SP trong tất cả thùng | `10,000` |
| **Tổng Trọng Lượng Gross (kg)** | Float | 🔄 | Gross weight | `3,500` |
| **Tổng Trọng Lượng Net (kg)** | Float | 🔄 | Net weight | `2,800` |
| **Tổng CBM (m³)** | Float | 🔄 | Tổng thể tích | `65.5` |
| **Trạng Thái** | Selection | | draft → packing → packed → shipped → delivered / cancelled | `packed` |

#### Workflow Packing List:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đang_Đóng_Gói: Bắt đầu đóng
    Đang_Đóng_Gói --> Đã_Đóng: Hoàn thành đóng gói
    Đã_Đóng --> Đã_Xuất: Xuất hàng
    Đã_Xuất --> Đã_Giao: Giao xong
    Nháp --> Đã_Hủy: Hủy
    Đang_Đóng_Gói --> Đã_Hủy: Hủy
    Đã_Đóng --> Đã_Hủy: Hủy
```

### 9.2 Chi Tiết Carton (Carton Line — garment.carton.line):

| Trường | Ý Nghĩa |
|--------|---------|
| **Từ Thùng** | Số thùng bắt đầu (VD: 1) |
| **Đến Thùng** | Số thùng kết thúc (VD: 50) |
| **Số Thùng** | 🔄 = Đến - Từ + 1 |
| **Size** | Size SP trong thùng |
| **Màu** | Màu SP trong thùng |
| **SL / Thùng** | Số SP trong mỗi thùng |
| **Tổng SL** | 🔄 = Số Thùng × SL/Thùng |
| **Dài (cm)** | Kích thước thùng — chiều dài |
| **Rộng (cm)** | Kích thước thùng — chiều rộng |
| **Cao (cm)** | Kích thước thùng — chiều cao |
| **Gross Weight (kg)** | Trọng lượng gross 1 thùng |
| **Net Weight (kg)** | Trọng lượng net 1 thùng |
| **CBM / Thùng** | 🔄 = Dài × Rộng × Cao ÷ 1,000,000 |
| **Tổng Gross** | 🔄 = Số Thùng × Gross Weight |
| **Tổng Net** | 🔄 = Số Thùng × Net Weight |
| **Tổng CBM** | 🔄 = Số Thùng × CBM/Thùng |
| **Barcode** | Mã vạch thùng carton |

### 9.3 Shipping Instruction — Chỉ Thị Giao Hàng (SI)

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng → Shipping Instruction (SI)`

Shipping Instruction là chứng từ gửi cho hãng tàu/hãng hàng không, hướng dẫn cách vận chuyển lô hàng. Mỗi SI gắn với một Packing List cụ thể.

#### Bảng giải thích trường — Shipping Instruction (garment.shipping.instruction):

| Trường | Kiểu | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|---------|-----------------|
| **Số SI** | Char | Mã tự động SI/YYYY/XXXXX | `SI/2026/00001` |
| **Packing List** | Many2one | Packing list liên kết | `PKL/2026/00001` |
| **Đơn Hàng** | Many2one | Đơn hàng (auto) | `GO-2026-00001` |
| **Buyer** | Many2one | Khách hàng (auto) | `H&M Vietnam` |
| **Ngày Tạo SI** | Date | Ngày lập | `2026-03-01` |
| **Shipper** | Char | Tên người gửi | `Garment Co. Ltd` |
| **Địa Chỉ Shipper** | Text | Địa chỉ shipper | `KCN Tân Bình, HCMC` |
| **Consignee** | Char | Tên người nhận | `H&M Sweden AB` |
| **Địa Chỉ Consignee** | Text | Địa chỉ consignee | `Stockholm, Sweden` |
| **Notify Party** | Text | Bên thông báo | `Same as consignee` |
| **Cảng Xếp Hàng** | Char | Port of loading | `Cat Lai, HCMC` |
| **Cảng Dỡ Hàng** | Char | Port of discharge (auto) | `Hamburg` |
| **Phương Thức** | Selection | Đường biển/hàng không (auto) | `sea` |
| **Tàu / Chuyến Bay** | Char | Tên phương tiện (auto) | `MAERSK SEALAND` |
| **ETD / ETA** | Date | Ngày xuất / đến (auto) | `2026-03-05` |
| **Mô Tả Hàng Hóa** | Text | Nội dung hàng hóa | `100% Cotton T-Shirts` |
| **Tổng Thùng / SL / Trọng Lượng / CBM** | Computed | Auto từ packing list | |
| **Điều Khoản Thanh Toán** | Selection | T/T, L/C, D/A, D/P | `lc` |
| **Incoterm** | Selection | FOB, CIF, CFR, EXW, DAP, DDP | `fob` |
| **Số L/C** | Char | Số thư tín dụng (nếu L/C) | `LC-2026-001` |
| **Chứng Từ Yêu Cầu** | Boolean × 6 | Invoice, PL, B/L, C/O, Fumigation, Inspection | ✅ / ❌ |
| **Trạng Thái** | Selection | draft → confirmed → sent → done / cancelled | `confirmed` |

#### Workflow SI:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đã_Xác_Nhận: Xác nhận
    Đã_Xác_Nhận --> Đã_Gửi_Hãng_Tàu: Gửi SI
    Đã_Gửi_Hãng_Tàu --> Hoàn_Thành: Done
    Nháp --> Đã_Hủy: Hủy
    Đã_Xác_Nhận --> Đã_Hủy: Hủy
    Đã_Gửi_Hãng_Tàu --> Đã_Hủy: Hủy
    Đã_Hủy --> Nháp: Đặt lại
```

### 9.4 Certificate of Origin — Chứng Nhận Xuất Xứ (C/O)

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng → Certificate of Origin (C/O)`

Chứng nhận xuất xứ (C/O) là chứng từ xác nhận nguồn gốc xuất xứ hàng hóa, cần thiết để hưởng ưu đãi thuế quan theo các hiệp định thương mại tự do (FTA).

#### Bảng giải thích trường — Certificate of Origin (garment.certificate.origin):

| Trường | Kiểu | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|---------|-----------------|
| **Số C/O** | Char | Mã tự động CO/YYYY/XXXXX | `CO/2026/00001` |
| **Packing List** | Many2one | Packing list liên kết | `PKL/2026/00001` |
| **Đơn Hàng** | Many2one | Đơn hàng (auto) | `GO-2026-00001` |
| **Buyer** | Many2one | Khách hàng (auto) | `H&M Vietnam` |
| **Ngày Cấp** | Date | Ngày cấp C/O | `2026-03-02` |
| **Loại C/O** | Selection | Form A, B, D, E, AK, AJ, AI, AANZ, VC, VK, EUR.1, CPTPP, RCEP, Non-Preferential | `form_d` |
| **Nước Xuất Xứ** | Char | Country of origin | `Vietnam` |
| **Nước Đến** | Char | Destination country | `Korea` |
| **Người Xuất Khẩu** | Char | Exporter name | `Garment Co. Ltd` |
| **Người Nhập Khẩu** | Char | Importer name | `Samsung SDS` |
| **Cơ Quan Cấp** | Char | Issuing authority | `VCCI` |
| **Số Tham Chiếu** | Char | Số tham chiếu VCCI | `REF-2026-001` |
| **Số Invoice / Ngày** | Char + Date | Invoice liên quan | `INV-2026-100` |
| **Cảng Xếp / Dỡ Hàng** | Char | Port of loading/discharge | `Cat Lai / Busan` |
| **Trạng Thái** | Selection | draft → applied → approved → issued / cancelled | `applied` |

#### Chi Tiết Hàng Hóa (C/O Line — garment.certificate.origin.line):

| Trường | Ý Nghĩa |
|--------|---------|
| **Mô Tả Hàng Hóa** | Tên / mô tả sản phẩm |
| **Mã HS** | Harmonized System code |
| **Số Lượng** | Số lượng hàng |
| **Đơn Vị** | Đơn vị tính (PCS, KG...) |
| **Trọng Lượng (kg)** | Trọng lượng hàng |
| **Trị Giá FOB (USD)** | Giá trị FOB |
| **Tiêu Chí Xuất Xứ** | WO (Wholly Obtained), PE, RVC, CTC, SP |

#### Workflow C/O:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Đã_Nộp_Hồ_Sơ: Nộp hồ sơ
    Đã_Nộp_Hồ_Sơ --> Đã_Duyệt: Duyệt
    Đã_Duyệt --> Đã_Cấp: Cấp C/O
    Nháp --> Đã_Hủy: Hủy
    Đã_Nộp_Hồ_Sơ --> Đã_Hủy: Hủy
    Đã_Duyệt --> Đã_Hủy: Hủy
    Đã_Hủy --> Nháp: Đặt lại
```

> 💡 **Mẹo:** Từ Packing List, nhấn nút thống kê **SI** hoặc **C/O** ở góc trên để nhanh chóng tạo hoặc xem các chứng từ liên quan.

---

## 10. Module Garment Planning — Kế Hoạch Sản Xuất

**Đường dẫn:** `Công Ty May → Sản Xuất → Kế Hoạch Sản Xuất`

![Kế Hoạch SX](images/15_planning.png)
*Hình 22: Danh sách kế hoạch sản xuất*

![Line Loading](images/16_line_loading.png)
*Hình 22b: Danh sách Line Loading — phân chuyền sản xuất*

![Chi tiết Kế Hoạch](images/73_plan_detail.png)
*Hình 23: Form view chi tiết kế hoạch sản xuất — phân chuyền*

### 10.1 Kế Hoạch Sản Xuất (Production Plan)

#### Bảng giải thích trường — Kế Hoạch (garment.production.plan):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã** | Char | ✅ | Mã tự động (PP-XXXXX) | `PP-2026-00001` |
| **Đơn Hàng** | Many2one | | Đơn hàng cần lập kế hoạch | `GO-2026-00001` |
| **Mẫu May** | Many2one | ✅ | Style sản xuất | `Áo Polo nam` |
| **Khách Hàng** | Many2one | | Buyer | `H&M Vietnam` |
| **Tổng SL Đặt Hàng** | Integer | ✅ | Tổng số lượng cần sản xuất | `10,000` |
| **SMV** | Float | ✅ | Standard Minute Value | `12.5` |
| **Ưu Tiên** | Selection | | 0 (Thấp), 1 (Bình Thường), 2 (Cao), 3 (Khẩn Cấp) | `1` |
| **Ngày Bắt Đầu** | Date | ✅ | Ngày bắt đầu SX | `2026-02-01` |
| **Ngày Kết Thúc** | Date | ✅ | Ngày kết thúc SX | `2026-02-28` |
| **Ngày Xuất Hàng** | Date | | Ship date deadline | `2026-03-05` |
| **Phân Chuyền** | One2many | | Phân bổ cho các chuyền | Bảng loading |
| **Tổng SL Kế Hoạch** | Integer | 🔄 | Tổng SL đã phân bổ | `9,500` |
| **SL Còn Lại** | Integer | 🔄 | = Tổng Đặt Hàng - Kế Hoạch | `500` |
| **Tổng Ngày Cần** | Float | 🔄 | = Tổng SL ÷ Tổng Năng Suất | `18.5` |
| **Trạng Thái** | Selection | | draft → confirmed → in_progress → done / cancelled | `confirmed` |

### 10.2 Phân Chuyền (Line Loading):

| Trường | Ý Nghĩa |
|--------|---------|
| **Chuyền May** | Chuyền được phân công |
| **SL Phân Bổ** | Số SP phân cho chuyền |
| **Ngày Bắt Đầu** | Ngày chuyền bắt đầu may |
| **Ngày Kết Thúc** | Ngày dự kiến hoàn thành |
| **SL Hoàn Thành** | Tự tính từ sản lượng ngày |
| **Tiến Độ (%)** | Tự tính = Hoàn Thành / Phân Bổ × 100 |

### 10.3 🧮 Capacity Planning Nâng Cao

**Đường dẫn:** `Công Ty May → Sản Xuất → 🧮 Capacity Planning`

Capacity Planning nâng cao cho phép **tính toán công suất chuyền tự động** dựa trên SAM (Standard Allowed Minutes), số lượng công nhân, và hiệu suất mục tiêu. Hỗ trợ lập kế hoạch trước khi tạo kế hoạch sản xuất chính thức.

#### Công thức tính:

```
Năng suất / ngày = (Số CN × Phút khả dụng × Hiệu suất%) / SAM
Phút khả dụng   = Phút làm việc - Phút nghỉ + Phút tăng ca
Số ngày cần     = ceil(Tổng SL ÷ Tổng năng suất/ngày)
```

#### Luồng sử dụng:

```mermaid
graph LR
    A[Nháp] --> B[Thêm Chuyền + Cấu hình]
    B --> C[🔄 Tính Toán]
    C --> D{Đạt tiến độ?}
    D -- Có --> E[✅ Duyệt]
    D -- Không --> F[Điều chỉnh CN/Ca/Hiệu suất]
    F --> C
    E --> G[📋 Tạo Kế Hoạch SX]
```

#### Bảng giải thích trường — Capacity Planning (garment.capacity.planning):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã Kế Hoạch** | Char | ✅ | Mã tự động (CAP/yyyy/xxxxx) | `CAP/2026/00001` |
| **Đơn Hàng May** | Many2one | | Liên kết đơn hàng | `GO-2026-00001` |
| **Mã Hàng** | Many2one | ✅ | Style sản xuất (tự load SAM) | `Áo Polo nam` |
| **SAM (Phút)** | Float | ✅ | Thời gian tiêu chuẩn may 1 SP | `10.0` |
| **Tổng SL Đặt Hàng** | Integer | ✅ | Số lượng cần sản xuất | `10,000` |
| **Phút Làm Việc / Ngày** | Integer | ✅ | Giờ làm chính (mặc định 480 = 8h) | `480` |
| **Phút Nghỉ / Ngày** | Integer | | Thời gian nghỉ giải lao | `60` |
| **Phút Tăng Ca / Ngày** | Integer | | Thời gian OT | `120` |
| **Phút Khả Dụng / Ngày** | Integer | 🔄 | = Làm việc - Nghỉ + Tăng ca | `540` |
| **Ngày Xuất Hàng** | Date | | Ship date deadline | `2026-03-15` |
| **Số Ngày Có Thể SX** | Integer | 🔄 | = Ship date - Hôm nay | `30` |
| **Tổng Năng Suất / Ngày** | Integer | 🔄 | Tổng output tất cả chuyền | `1,974` |
| **Tổng Năng Suất / Giờ** | Float | 🔄 | Tổng output / giờ | `294.0` |
| **Tổng Số CN** | Integer | 🔄 | Tổng CN tất cả chuyền | `70` |
| **Số Ngày Cần** | Float | 🔄 | = ceil(Tổng SL ÷ Năng suất/ngày) | `6.0` |
| **Đạt Tiến Độ?** | Boolean | 🔄 | Ngày cần ≤ Ngày có thể? | `✅` |
| **Tỷ Lệ Sử Dụng (%)** | Float | 🔄 | % tải công suất | `70.5` |
| **SP / CN / Ngày** | Float | 🔄 | Năng suất bình quân | `28.2` |
| **Chuyền Thắt Cổ Chai** | Many2one | 🔄 | Chuyền có NS/CN thấp nhất | `Chuyền May A` |
| **Trạng Thái** | Selection | | Nháp → Đã Tính Toán → Đã Duyệt / Đã Hủy | `simulated` |

#### Phân Bổ Chuyền (garment.capacity.line):

| Trường | Ý Nghĩa |
|--------|---------|
| **Chuyền May** | Chuyền được phân bổ |
| **Số CN** | Tự lấy từ chuyền, có thể sửa |
| **Hiệu Suất Mục Tiêu (%)** | % hiệu suất kỳ vọng (mặc định 65%) |
| **Năng Suất / Ngày** | 🔄 Tự tính = (CN × Phút KD × Hiệu suất) ÷ SAM |
| **Năng Suất / Giờ** | 🔄 Tự tính |
| **SP / CN / Ngày** | 🔄 Tự tính |
| **Ngày Cần (riêng)** | 🔄 Nếu chỉ dùng chuyền này |
| **Tỷ Trọng (%)** | 🔄 % đóng góp so với tổng |

#### Hành động chính:

| Nút | Mô tả |
|-----|-------|
| **🔄 Tính Toán Công Suất** | Kích hoạt tính toán tự động cho tất cả chuyền |
| **✅ Duyệt** | Duyệt kế hoạch (cần tính toán trước) |
| **📋 Tạo Kế Hoạch SX** | Tạo Production Plan + Line Loading từ kết quả |
| **❌ Hủy** / **🔄 Về Nháp** | Quản lý trạng thái |

> 💡 **Mẹo:** Sử dụng Capacity Planning để **mô phỏng** trước nhiều kịch bản (tăng ca, thêm CN, đổi hiệu suất) rồi chọn phương án tối ưu nhất trước khi tạo kế hoạch SX thực tế.

### 10.4 ⏰ Cảnh Báo Hạn Giao Hàng Tự Động (Deadline Auto-Alert)

Hệ thống tự động kiểm tra hạn giao hàng (ship_date) của các kế hoạch sản xuất **mỗi ngày** và tạo cảnh báo (Activity) cho người phụ trách:

**Điều kiện cảnh báo:**
- Kế hoạch **quá hạn** (ship_date < hôm nay) → Activity: "⚠️ QUÁ HẠN X ngày!"
- Kế hoạch **sắp đến hạn** (ship_date trong vòng 3 ngày) → Activity: "⏰ Còn X ngày đến hạn giao"

**Đặc điểm:**
- Chỉ cảnh báo kế hoạch đang hoạt động (không cảnh báo đã hoàn thành hoặc đã hủy)
- Không tạo cảnh báo trùng lặp trong cùng ngày
- Activity hiển thị trên chatter của kế hoạch và trong mục "Hoạt động" của người dùng
- Cron job chạy tự động hàng ngày, không cần cấu hình thêm

**Quản trị:**

| Mục | Chi Tiết |
|-----|----------|
| **Tên Cron** | Garment: Cảnh Báo Hạn Giao Hàng |
| **Tần Suất** | Mỗi ngày 1 lần |
| **Đường dẫn quản lý** | Settings → Technical → Automation → Scheduled Actions |
| **Ngưỡng cảnh báo** | 3 ngày trước ship_date |

---

## 11. Module Garment Maintenance — Bảo Trì Máy

**Đường dẫn:** `Công Ty May → Sản Xuất`

### 11.1 Quản Lý Máy Móc (Machine)

**Đường dẫn:** `Công Ty May → Sản Xuất → Danh Sách Máy`

![Danh sách Máy](images/17_machines.png)
*Hình 24: Danh sách máy móc*

![Chi tiết Máy](images/70_machine_detail.png)
*Hình 25: Form view chi tiết máy — thông số, bảo trì*

#### Bảng giải thích trường — Máy Móc (garment.machine):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã Máy** | Char | ✅ | Mã nội bộ | `M-001` |
| **Loại Máy** | Selection | ✅ | lockstitch (1 Kim), overlock (Vắt Sổ), flatlock (Bằng), bartack (Bọ), buttonhole (Khuy), button_attach (Đính Cúc), zigzag, cutting (Cắt), pressing (Ủi/Ép), other | `lockstitch` |
| **Hãng** | Char | | Thương hiệu | `Juki` |
| **Model** | Char | | Model máy | `DDL-8700` |
| **Số Serial** | Char | | Số serial (duy nhất) | `JK-2023-12345` |
| **Ngày Mua** | Date | | Ngày mua máy | `2023-01-15` |
| **Hết Bảo Hành** | Date | | Ngày hết bảo hành | `2025-01-15` |
| **Chuyền May** | Many2one | | Đang ở chuyền nào | `Chuyền May 1` |
| **Thợ Phụ Trách** | Many2one | | CN phụ trách máy | `Trần Văn B` |
| **Trạng Thái** | Selection | | active / maintenance / broken / retired | `active` |
| **Chu Kỳ Bảo Trì (ngày)** | Integer | | Interval bảo trì định kỳ | `30` |
| **Bảo Trì Gần Nhất** | Date | | Ngày bảo trì cuối | `2026-01-20` |
| **Bảo Trì Tiếp** | Date | 🔄 | Tự tính = Gần nhất + Chu kỳ | `2026-02-19` |
| **Lịch Sử Bảo Trì** | One2many | | Danh sách yêu cầu bảo trì | Bảng |

### 11.2 Yêu Cầu Bảo Trì (Maintenance Request)

![Danh sách Yêu Cầu Bảo Trì](images/18_maintenance.png)
*Hình 25b: Danh sách yêu cầu bảo trì*

![Chi tiết Bảo Trì](images/69_maint_req_detail.png)
*Hình 26: Form view chi tiết yêu cầu bảo trì*

#### Bảng giải thích trường — Yêu Cầu Bảo Trì (garment.maintenance.request):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã** | Char | ✅ | Mã tự động (MR-XXXXX) | `MR-2026-00001` |
| **Máy** | Many2one | ✅ | Máy cần bảo trì | `M-001 (Juki DDL-8700)` |
| **Loại** | Selection | ✅ | preventive (Bảo Trì Định Kỳ), corrective (Sửa Chữa), breakdown (Hư Hỏng Khẩn) | `corrective` |
| **Ưu Tiên** | Selection | | 0 (Thấp), 1 (Bình Thường), 2 (Cao), 3 (Khẩn Cấp) | `1` |
| **Ngày Yêu Cầu** | Datetime | | Thời điểm yêu cầu | `2026-02-15 08:30` |
| **Ngày Dự Kiến** | Date | | Ngày dự kiến xử lý | `2026-02-16` |
| **Ngày Hoàn Thành** | Datetime | | Tự set khi hoàn thành | `2026-02-16 14:00` |
| **Kỹ Thuật Viên** | Many2one | | Thợ sửa | `Nguyễn Văn Kỹ Thuật` |
| **Mô Tả Sự Cố** | Text | | Mô tả chi tiết sự cố | `Máy bị kẹt chỉ` |
| **Xử Lý** | Text | | Mô tả cách xử lý | `Thay bộ cần chỉ` |
| **Phụ Tùng Sử Dụng** | Text | | Liệt kê phụ tùng | `Bộ cần chỉ Juki` |
| **Chi Phí** | Float | | Chi phí sửa chữa | `500,000` |
| **Thời Gian Dừng (giờ)** | Float | | Tổng giờ máy dừng | `5.5` |
| **Trạng Thái** | Selection | | draft → confirmed → in_progress → done / cancelled | `done` |

> ⚡ Khi xác nhận yêu cầu **breakdown**, máy tự động chuyển trạng thái **"Hư Hỏng"**. Khi hoàn thành, máy chuyển lại **"Đang Hoạt Động"**.

---

## 12. Module Garment Payroll — Lương Khoán

**Đường dẫn:** `Công Ty May → Nhân Sự & Lương`

### 12.1 Bảng Lương (Wage Calculation)

![Bảng Lương](images/38_wage.png)
*Hình 27: Danh sách bảng lương tháng*

![Đơn Giá Khoán](images/36_piece_rate.png)
*Hình 27b: Danh sách đơn giá khoán theo mã hàng*

![Sản Lượng Công Nhân](images/37_worker_output.png)
*Hình 27c: Danh sách sản lượng công nhân hàng ngày*

![Chi tiết Bảng Lương](images/66_wage_detail.png)
*Hình 28: Form view chi tiết bảng lương — tổng hợp thu nhập*

#### Bảng giải thích trường — Bảng Lương (garment.wage.calculation):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã** | Char | ✅ | Mã tự động | `WG-2026-00001` |
| **Công Nhân** | Many2one | ✅ | Nhân viên tính lương | `Nguyễn Thị May` |
| **Phòng Ban** | Many2one | 🔄 | Lấy từ nhân viên | `Chuyền May 1` |
| **Tháng** | Selection | ✅ | 01 → 12 | `02` (Tháng 2) |
| **Năm** | Integer | ✅ | Năm tính lương | `2026` |
| ---- | ---- | ---- | **LƯƠNG CƠ BẢN** | ---- |
| **Lương Cơ Bản (VNĐ)** | Float | | Mức lương hợp đồng | `5,000,000` |
| **Ngày Công (tiêu chuẩn)** | Integer | | Số ngày công tháng | `26` |
| **Ngày Thực Tế** | Integer | | Số ngày đi làm thực tế | `24` |
| **Lương Ngày Công** | Float | 🔄 | = Lương CB / Ngày CĐ × Ngày TT | `4,615,385` |
| ---- | ---- | ---- | **LƯƠNG KHOÁN** | ---- |
| **Tổng SL Sản Phẩm** | Integer | 🔄 | Tự tính từ Worker Output | `2,500` |
| **Tiền Khoán (VNĐ)** | Float | 🔄 | Tự tính từ Piece Rate × SL | `2,000,000` |
| ---- | ---- | ---- | **TĂNG CA** | ---- |
| **Tổng Giờ Tăng Ca** | Float | 🔄 | Tự tính từ Worker Output | `20.5` |
| **Đơn Giá OT (VNĐ/h)** | Float | | Đơn giá 1 giờ tăng ca | `35,000` |
| **Tiền Tăng Ca** | Float | 🔄 | = Giờ TC × Đơn giá | `717,500` |
| ---- | ---- | ---- | **PHỤ CẤP** | ---- |
| **PC Chuyên Cần** | Float | | Thưởng đi đủ công | `300,000` |
| **PC Ăn Trưa** | Float | | Hỗ trợ cơm trưa | `600,000` |
| **PC Xăng Xe** | Float | | Hỗ trợ đi lại | `300,000` |
| **PC Điện Thoại** | Float | | Phụ cấp liên lạc | `100,000` |
| **PC Khác** | Float | | Phụ cấp thêm | `0` |
| **Tổng Phụ Cấp** | Float | 🔄 | Tổng 5 khoản PC trên | `1,300,000` |
| ---- | ---- | ---- | **BẢO HIỂM XÃ HỘI** | ---- |
| **Mức Đóng BHXH** | Float | | Mức lương đóng BHXH | `5,000,000` |
| **BHXH (8%)** | Float | 🔄 | = Mức đóng × 8% | `400,000` |
| **BHYT (1.5%)** | Float | 🔄 | = Mức đóng × 1.5% | `75,000` |
| **BHTN (1%)** | Float | 🔄 | = Mức đóng × 1% | `50,000` |
| **Tổng BH (10.5%)** | Float | 🔄 | = BHXH + BHYT + BHTN | `525,000` |
| ---- | ---- | ---- | **THUẾ TNCN** | ---- |
| **Giảm Trừ Bản Thân** | Float | | 11 triệu/tháng (luật VN) | `11,000,000` |
| **Số Người Phụ Thuộc** | Integer | | Số NPT đăng ký | `1` |
| **Giảm Trừ PT** | Float | 🔄 | = NPT × 4.4 triệu | `4,400,000` |
| **Thu Nhập Chịu Thuế** | Float | 🔄 | = Tổng TN - BH - GT | `0` |
| **Thuế TNCN** | Float | 🔄 | Tính theo biểu lũy tiến 7 bậc | `0` |
| ---- | ---- | ---- | **TỔNG KẾT** | ---- |
| **Thưởng Tháng** | Float | | Tiền thưởng thêm | `200,000` |
| **Khấu Trừ Khác** | Float | | Các khoản trừ khác | `0` |
| **Tổng Thu Nhập** | Float | 🔄 | Gross = CB + Khoán + OT + PC + Thưởng | `8,632,885` |
| **Thực Lĩnh** | Float | 🔄 | Net = Gross - BH - Thuế - KT | `8,107,885` |
| **Trạng Thái** | Selection | | draft → calculated → confirmed → paid | `paid` |

> 💡 Nhấn nút **"Tính Lương"** để tự động pull dữ liệu từ Chấm Công và Worker Output.

### 12.2 Phiếu Thưởng (Bonus)

![Danh sách Thưởng](images/39_bonus.png)
*Hình 29: Danh sách phiếu thưởng*

![Chi tiết Thưởng](images/67_bonus_detail.png)
*Hình 30: Form view chi tiết phiếu thưởng — danh sách nhân viên*

#### Bảng giải thích trường — Phiếu Thưởng (garment.bonus):

| Trường | Kiểu | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|---------|-----------------|
| **Mã** | Char | Mã tự động (BN-XXXXX) | `BN-2026-00001` |
| **Tháng / Năm** | Selection + Integer | Kỳ thưởng | `02 / 2026` |
| **Loại Thưởng** | Selection | monthly (Hàng Tháng), quarterly (Quý), yearly (Cuối Năm), special (Đặc Biệt), productivity (Năng Suất), quality (Chất Lượng), attendance (Chuyên Cần) | `monthly` |
| **Tổng Tiền Thưởng** | Float | 🔄 Tổng từ các dòng | `5,000,000` |
| **Chi Tiết (Bonus Line)** | One2many | Danh sách NV được thưởng | Bảng |
| **Trạng Thái** | Selection | draft → confirmed / cancelled | `confirmed` |

**Bonus Line:**

| Trường | Ý Nghĩa |
|--------|---------|
| **Nhân Viên** | CN được thưởng |
| **Xếp Loại** | a (Xuất Sắc), b (Giỏi), c (Khá), d (Trung Bình) |
| **Số Tiền** | Tiền thưởng |
| **Ghi Chú** | Lý do thưởng |

---

## 13. Module Garment Compliance — Tuân Thủ

**Đường dẫn:** `Công Ty May → Chất Lượng → Audits`

![Danh sách Compliance](images/23_compliance.png)
*Hình 31: Danh sách audit compliance*

![Chi tiết Audit](images/68_compliance_detail.png)
*Hình 32: Form view chi tiết audit — phát hiện lỗi, CAP*

### 13.1 Audit Compliance (garment.compliance.audit)

#### Bảng giải thích trường:

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã** | Char | ✅ | Mã tự động (CA-XXXXX) | `CA-2026-00001` |
| **Loại Audit** | Selection | ✅ | bsci (BSCI), wrap (WRAP), sedex (SEDEX/SMETA), sa8000 (SA8000), oeko_tex (OEKO-TEX), gots (GOTS), iso9001, iso14001, buyer (Buyer Audit), internal (Nội Bộ), other | `bsci` |
| **Ngày Audit** | Date | ✅ | Ngày thực hiện audit | `2026-03-01` |
| **Ngày Hết Hạn** | Date | | Ngày chứng chỉ hết hạn | `2027-03-01` |
| **Auditor** | Char | | Tổ chức/người audit | `SGS Vietnam` |
| **Buyer** | Many2one | | Khách hàng yêu cầu audit | `H&M Vietnam` |
| **Xếp Hạng** | Selection | | a (Xuất Sắc) → e (Không Đạt) | `b` |
| **Tổng Phát Hiện** | Integer | 🔄 | Tổng số finding | `5` |
| **Lỗi Nghiêm Trọng** | Integer | 🔄 | Số finding critical | `0` |
| **Chi Tiết Phát Hiện** | One2many | | Danh sách findings | Bảng |
| **Kế Hoạch Khắc Phục (CAP)** | One2many | | Corrective Action Plan | Bảng |
| **Chứng Chỉ / Báo Cáo** | Binary | | Upload file audit report | Upload |
| **Trạng Thái** | Selection | | scheduled → in_progress → completed / cap_required → closed | `closed` |

### 13.2 Audit Finding:

| Trường | Ý Nghĩa |
|--------|---------|
| **Hạng Mục** | health_safety / labor / wages / environment / management / chemical / fire_safety / building / discrimination / child_labor / other |
| **Mức Độ** | critical (Nghiêm Trọng), major (Lớn), minor (Nhỏ), observation (Quan Sát) |
| **Mô Tả** | Mô tả chi tiết phát hiện |
| **Bằng Chứng** | Bằng chứng (ảnh, tài liệu) |

### 13.3 CAP — Corrective Action Plan:

| Trường | Ý Nghĩa |
|--------|---------|
| **Mô Tả** | Nội dung cần khắc phục |
| **Người Phụ Trách** | Người chịu trách nhiệm |
| **Hạn Hoàn Thành** | Deadline khắc phục |
| **Trạng Thái** | draft → in_progress → done |

> ⚠️ Không thể **đóng audit** khi còn CAP chưa hoàn thành.

---

## 14. Module Garment Report — Báo Cáo

**Đường dẫn:** `Công Ty May → Báo Cáo`

![Báo Cáo menu](images/86_menu_bao_cao.png)
*Hình 32b: Menu Báo Cáo — hiệu suất chuyền, phân tích lỗi, báo cáo SX*

![Báo cáo](images/40_report_efficiency.png)
*Hình 33: Màn hình báo cáo & phân tích sản xuất*

### 14.1 Phân Tích Hiệu Suất (Efficiency Analysis)

![Báo cáo Hiệu Suất](images/40_report_efficiency.png)
*Hình 33: Báo cáo phân tích hiệu suất sản xuất*

Pivot view & graph view phân tích:
- Hiệu suất theo chuyền may
- Hiệu suất theo mẫu may
- So sánh năng suất thực tế vs mục tiêu

### 14.2 Phân Tích Lỗi (Defect Analysis)

![Phân Tích Lỗi](images/41_report_defect.png)
*Hình 33b: Báo cáo phân tích lỗi sản xuất*

Thống kê lỗi:
- Tỷ lệ lỗi theo loại (chỉ rối, bỏ mũi, vải lỗi, ...)
- Lỗi theo chuyền may
- Trend lỗi theo thời gian

---

## 15. Module Garment Washing — Xưởng Giặt

**Đường dẫn:** `Công Ty May → Sản Xuất → Lệnh Giặt`

### 15.1 Lệnh Giặt (Wash Order)

![Lệnh Giặt](images/19_wash_orders.png)
*Hình 33: Danh sách lệnh giặt*

![Chi tiết Lệnh Giặt](images/58_wash_detail.png)
*Hình 34: Form view chi tiết lệnh giặt — thông số giặt, QC*

#### Bảng giải thích trường — Lệnh Giặt (garment.wash.order):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Lệnh Giặt** | Char | ✅ | Mã tự động (WO-XXXXX) | `WO-2026-00001` |
| **Loại Lệnh** | Selection | ✅ | internal (Giặt Nội Bộ), external_in (Nhận Giặt Gia Công) | `internal` |
| ---- | ---- | ---- | **LIÊN KẾT NỘI BỘ** | ---- |
| **Lệnh Sản Xuất** | Many2one | | Lệnh SX nội bộ liên quan | `PO-2026-00001` |
| **Đơn Hàng May** | Many2one | 🔄 | Lấy từ lệnh SX | `GO-2026-00001` |
| **Mẫu May** | Many2one | | Style sản phẩm giặt | `Quần Jeans nam` |
| ---- | ---- | ---- | **KHÁCH GIA CÔNG** | ---- |
| **Khách Hàng / Công Ty Gửi** | Many2one | | Đối tác gửi giặt | `Công ty Denim VN` |
| **PO Khách Gửi** | Char | | Mã PO của khách | `PO-DEN-2026-012` |
| ---- | ---- | ---- | **CÔNG THỨC & QUY TRÌNH** | ---- |
| **Công Thức Giặt** | Many2one | | Recipe sử dụng | `Stone Wash Medium` |
| **Loại Giặt** | Selection | 🔄 | Lấy từ recipe: normal / enzyme / stone / bleach / acid / garment_dye / softener / special | `stone` |
| ---- | ---- | ---- | **SỐ LƯỢNG** | ---- |
| **SL Nhận Giặt (pcs)** | Integer | ✅ | Số SP nhận vào | `500` |
| **Trọng Lượng (kg)** | Float | | Tổng KL hàng | `350.5` |
| **SL Giặt Xong** | Integer | | Số SP đã giặt OK | `495` |
| **SL Giặt Lại (Re-wash)** | Integer | | Số SP cần giặt lại | `3` |
| **SL Loại Bỏ** | Integer | | Số SP hỏng không dùng được | `2` |
| ---- | ---- | ---- | **MÁY & NĂNG LƯỢNG** | ---- |
| **Máy Giặt** | Char | | Tên/mã máy sử dụng | `Máy Giặt Công Nghiệp #3` |
| **Công Suất Máy (kg)** | Float | | Capacity máy | `200.0` |
| **Nước Tiêu Thụ (lít)** | Float | | Tracking nước | `2,500` |
| **Điện Tiêu Thụ (kWh)** | Float | | Tracking điện | `85.5` |
| **Hơi Nước (kg steam)** | Float | | Tracking steam | `150.0` |
| ---- | ---- | ---- | **THỜI GIAN** | ---- |
| **Ngày Nhận Hàng** | Date | | Ngày nhận SP vào | `2026-02-15` |
| **Bắt Đầu Giặt** | Datetime | | Thời điểm bắt đầu | `2026-02-16 08:00` |
| **Kết Thúc Giặt** | Datetime | | Thời điểm kết thúc | `2026-02-16 16:00` |
| **Ngày Giao Dự Kiến** | Date | | Deadline giao | `2026-02-18` |
| **Ngày Giao Lại** | Date | | Ngày giao thực tế | `2026-02-17` |
| ---- | ---- | ---- | **CHI PHÍ** | ---- |
| **Đơn Giá Giặt (VNĐ/pcs)** | Float | | Giá giặt 1 SP | `15,000` |
| **Tổng Chi Phí** | Float | 🔄 | = SL Nhận × Đơn giá | `7,500,000` |
| **Chi Phí Hóa Chất** | Float | | Riêng chi phí hoá chất | `1,200,000` |
| ---- | ---- | ---- | **CHẤT LƯỢNG** | ---- |
| **Màu Trước Giặt** | Char | | Mã màu trước giặt | `Raw Indigo` |
| **Màu Sau Giặt** | Char | | Mã màu sau giặt | `Medium Blue` |
| **Cảm Giác Tay** | Selection | | soft / medium / stiff | `medium` |
| **Co Dọc (%)** | Float | | % co theo chiều dọc | `3.5` |
| **Co Ngang (%)** | Float | | % co theo chiều ngang | `2.0` |
| **QC Đạt** | Boolean | | Kết quả kiểm tra | ✅ |
| **Ghi Chú QC** | Text | | Comment QC | `Đạt yêu cầu` |
| ---- | ---- | ---- | **TÍNH TOÁN** | ---- |
| **Tỷ Lệ Đạt (%)** | Float | 🔄 | = Giặt Xong / Nhận × 100 | `99.0%` |
| **Tỷ Lệ Giặt Lại (%)** | Float | 🔄 | = Re-wash / Nhận × 100 | `0.6%` |
| **Trạng Thái** | Selection | | draft → confirmed → washing → qc → done → delivered / cancelled | `delivered` |

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

### 15.2 Công Thức Giặt (Wash Recipe)

![Công Thức Giặt](images/20_wash_recipes.png)
*Hình 35: Danh sách công thức giặt*

![Chi tiết Công Thức](images/20_wash_recipes.png)
*Hình 36: Form view chi tiết công thức giặt — hóa chất, nhiệt độ*

#### Bảng giải thích trường — Công Thức Giặt (garment.wash.recipe):

| Trường | Kiểu | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|---------|-----------------|
| **Tên Công Thức** | Char | Tên gọi recipe | `Stone Wash Medium` |
| **Mã** | Char | Mã duy nhất | `RC-001` |
| **Loại Giặt** | Selection | normal / enzyme / stone / bleach / acid / garment_dye / softener / special | `stone` |
| **Nhiệt Độ (°C)** | Float | Nhiệt độ nước giặt | `60.0` |
| **Thời Gian (phút)** | Float | Thời gian giặt | `45.0` |
| **Tỷ Lệ Nước (lít/kg)** | Float | Lượng nước / kg hàng | `8.0` |
| **Hóa Chất** | One2many | Danh sách hóa chất sử dụng | Bảng |
| **Quy Trình** | Text | Mô tả chi tiết các bước | Step-by-step |
| **Ghi Chú An Toàn** | Text | Lưu ý an toàn lao động | `Đeo găng tay, kính bảo hộ` |

---

## 16. Module Garment Subcontract — Gia Công

**Đường dẫn:** `Công Ty May → Sản Xuất → Đơn Gia Công`

![Đơn Gia Công](images/21_subcontract.png)
*Hình 37: Danh sách đơn gia công*

![Chi tiết Gia Công](images/59_subcontract_detail.png)
*Hình 38: Form view chi tiết đơn gia công — nguyên liệu, chi phí, QC*

### 16.1 Đơn Gia Công (Subcontract Order)

#### Bảng giải thích trường — Đơn Gia Công (garment.subcontract.order):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Đơn GC** | Char | ✅ | Mã tự động (SC-XXXXX) | `SC-2026-00001` |
| **Loại** | Selection | ✅ | outgoing (Gửi Gia Công — Outsource), incoming (Nhận Gia Công — Insource) | `outgoing` |
| **Loại Công Việc** | Selection | ✅ | cmt (CMT), sewing (May), cutting (Cắt), washing (Giặt), embroidery (Thêu), printing (In), finishing (Hoàn Thiện), packing (Đóng Gói), other | `embroidery` |
| **Đối Tác GC** | Many2one | ✅ | Công ty gia công | `Công ty Thêu ABC` |
| **PO Đối Tác** | Char | | Mã PO từ đối tác | `PO-ABC-123` |
| **Đơn Hàng May Gốc** | Many2one | | Liên kết đơn hàng nội bộ | `GO-2026-00001` |
| **Lệnh Sản Xuất** | Many2one | | Liên kết lệnh SX | `PO-2026-00001` |
| **Mẫu May** | Many2one | | Style gia công | `Áo Polo nam` |
| ---- | ---- | ---- | **CHI TIẾT GIA CÔNG** | ---- |
| **Chi Tiết** | One2many | | Dòng chi tiết (màu, size, SL) | Bảng |
| **Tổng SL GC** | Integer | 🔄 | Tổng từ các dòng | `2,000` |
| **Tổng SL Nhận Lại** | Integer | 🔄 | Tổng đã nhận lại | `1,950` |
| **Tổng SL Lỗi** | Integer | 🔄 | Tổng từ chối | `30` |
| **Tiến Độ (%)** | Float | 🔄 | = Nhận / Đặt × 100 | `97.5%` |
| ---- | ---- | ---- | **NGUYÊN LIỆU** | ---- |
| **NL Gửi Đi** | Text | | Chi tiết vải, phụ liệu gửi | `Vải Cotton 2,100m...` |
| **NL Trả Lại** | Text | | NL dư trả lại | `Vải dư 50m` |
| ---- | ---- | ---- | **THỜI GIAN** | ---- |
| **Ngày Đặt** | Date | | Ngày tạo đơn | `2026-02-01` |
| **Ngày Giao NL** | Date | | Ngày gửi hàng/NL cho đối tác | `2026-02-03` |
| **Ngày Nhận Dự Kiến** | Date | | Deadline nhận lại | `2026-02-20` |
| **Ngày Nhận Thực Tế** | Date | | Ngày nhận hàng thực tế | `2026-02-18` |
| **Trễ Hạn** | Boolean | 🔄 | Tự tính so với deadline | ❌ |
| ---- | ---- | ---- | **CHI PHÍ** | ---- |
| **Đơn Giá GC (VNĐ/pcs)** | Float | | Giá gia công 1 SP | `5,000` |
| **Tổng Chi Phí GC** | Float | 🔄 | = Tổng SL × Đơn giá | `10,000,000` |
| **Thanh Toán** | Selection | | unpaid / partial / paid | `paid` |
| **Đã Thanh Toán** | Float | | Số tiền đã trả | `10,000,000` |
| ---- | ---- | ---- | **CHẤT LƯỢNG** | ---- |
| **Yêu Cầu Kiểm Hàng** | Boolean | | Có cần QC không | ✅ |
| **QC Đạt** | Boolean | | Kết quả QC | ✅ |
| **Ghi Chú QC** | Text | | Comment kiểm hàng | `Đạt yêu cầu` |
| **Trạng Thái** | Selection | | draft → confirmed → sent → in_progress → partial_received → received → qc → done / cancelled | `done` |

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

## 17. Module Garment Finishing — Hoàn Thiện

**Đường dẫn:** `Công Ty May → Sản Xuất → Lệnh Hoàn Thiện`

![Lệnh Hoàn Thiện](images/14_finishing.png)
*Hình 39: Danh sách lệnh hoàn thiện*

![Chi tiết Hoàn Thiện](images/54_finishing_detail.png)
*Hình 40: Form view chi tiết lệnh hoàn thiện — các công đoạn, QC*

### 17.1 Lệnh Hoàn Thiện (Finishing Order)

#### Bảng giải thích trường — Lệnh Hoàn Thiện (garment.finishing.order):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Lệnh** | Char | ✅ | Mã tự động (FN-XXXXX) | `FN-2026-00001` |
| **Lệnh Sản Xuất** | Many2one | ✅ | LSX liên quan | `PO-2026-00001` |
| **Đơn Hàng May** | Many2one | 🔄 | Lấy từ lệnh SX | `GO-2026-00001` |
| **Mẫu May** | Many2one | 🔄 | Lấy từ lệnh SX | `Áo Polo nam` |
| **Khách Hàng** | Many2one | 🔄 | Lấy từ lệnh SX | `H&M Vietnam` |
| **Chuyền Hoàn Thiện** | Many2one | | Chuyền thực hiện (loại=finishing) | `Tổ Hoàn Thiện A` |
| **Ngày Bắt Đầu** | Date | | Ngày bắt đầu | `2026-02-20` |
| **Ngày KT Dự Kiến** | Date | | Deadline | `2026-02-25` |
| **Ngày HT Thực Tế** | Date | | Tự set khi done | `2026-02-24` |
| **SL Nhận Từ May** | Integer | | Số BTP nhận | `5,000` |
| ---- | ---- | ---- | **THỐNG KÊ CÔNG ĐOẠN** | ---- |
| **Đã Cắt Chỉ** | Integer | 🔄 | Tổng từ task type=thread_cut | `4,950` |
| **Đã Ủi** | Integer | 🔄 | Tổng từ task type=pressing | `4,900` |
| **Đã Đóng Tag** | Integer | 🔄 | Tổng từ task type=tagging | `4,900` |
| **Đã Gấp Xếp** | Integer | 🔄 | Tổng từ task type=folding | `4,850` |
| **QC Đạt** | Integer | 🔄 | Tổng từ task type=qc_check | `4,800` |
| **Lỗi Phát Hiện** | Integer | 🔄 | Tổng lỗi tất cả task | `50` |
| **Tỷ Lệ HT (%)** | Float | 🔄 | = Gấp Xếp / SL Nhận × 100 | `97.0%` |
| **Trạng Thái** | Selection | | draft → confirmed → in_progress → done / cancelled | `done` |

### 17.2 Công Đoạn Hoàn Thiện (Finishing Task)

| Trường | Kiểu | Ý Nghĩa | Giá trị |
|--------|------|---------|---------|
| **Ngày** | Date | Ngày thực hiện | `2026-02-21` |
| **Công Việc** | Selection | thread_cut (Cắt Chỉ), pressing (Ủi), tagging (Đóng Tag/Nhãn), folding (Gấp Xếp), qc_check (Kiểm Hàng) | `pressing` |
| **Công Nhân** | Many2one | Người thực hiện | `Nguyễn Thị Ủi` |
| **SL Hoàn Thành** | Integer | Số SP làm xong | `200` |
| **SL Lỗi** | Integer | Số SP lỗi | `3` |
| **Ghi Chú** | Char | Ghi chú thêm | `Ủi form cổ` |

> 📊 **Tỷ lệ hoàn thành** dựa trên công đoạn cuối (Gấp Xếp) so với Số lượng nhận.

---

## 18. Module Garment HR — Nhân Sự & Chấm Công

![Nhân Sự & Lương](images/85_menu_nhan_su.png)
*Hình 40b: Menu Nhân Sự & Lương — chấm công, tay nghề, lương khoán gộp chung*

**Đường dẫn:** `Công Ty May → Nhân Sự & Lương`

### 18.1 Phòng Ban / Tổ

**Đường dẫn:** `Cấu Hình → Phòng Ban` (trong Cấu Hình)

17 phòng ban/tổ tiêu biểu: Tổ Cắt, Chuyền 1-5 (Tổ May), Tổ Hoàn Thiện, Tổ QC, Tổ Giặt, Tổ Đóng Gói, Tổ Kho, Tổ Bảo Trì, Tổ Lái Xe, Phòng Kế Toán, Phòng Kế Hoạch, Phòng Nhân Sự, Phòng Kinh Doanh, Ban Giám Đốc.

### 18.2 Chấm Công (Attendance)

**Đường dẫn:** `Công Ty May → Nhân Sự & Lương → Chấm Công`

![Bảng Chấm Công](images/32_attendance.png)
*Hình 41: Danh sách chấm công*

![Chi tiết Chấm Công](images/65_attendance_detail.png)
*Hình 41b: Form view chi tiết chấm công*

#### Bảng giải thích trường — Chấm Công (garment.attendance):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Nhân Viên** | Many2one | ✅ | CN chấm công | `Nguyễn Thị May` |
| **Phòng Ban** | Many2one | 🔄 | Lấy từ NV | `Chuyền May 1` |
| **Ngày** | Date | ✅ | Ngày chấm công | `2026-02-15` |
| **Trạng Thái** | Selection | ✅ | present (Đi Làm), absent (Vắng), late (Đi Muộn), early_leave (Về Sớm), half_day (Nửa Ngày), business_trip (Công Tác), holiday (Nghỉ Lễ) | `present` |
| **Giờ Vào** | Float | | Giờ check-in (VD: 7.5 = 7:30) | `7.5` |
| **Giờ Ra** | Float | | Giờ check-out (VD: 17.0 = 17:00) | `17.0` |
| **Giờ Làm Việc** | Float | 🔄 | Tự tính = Ra - Vào - 1h (nghỉ trưa) | `8.5` |
| **Giờ Tăng Ca** | Float | | Giờ OT thêm | `2.0` |
| **Ca** | Selection | | day (Ca Ngày), night (Ca Đêm), overtime (Tăng Ca) | `day` |

> ⚠️ Mỗi nhân viên chỉ có **1 bản ghi chấm công/ngày** (ràng buộc duy nhất).

### 18.3 Tổng Hợp Công Tháng

**Đường dẫn:** `Công Ty May → Nhân Sự & Lương → Tổng Hợp Công Tháng`

![Tổng Hợp Công Tháng](images/33_attendance_sum.png)
*Hình 41c: Danh sách tổng hợp công tháng*

| Trường | Ý Nghĩa |
|--------|---------|
| **Nhân Viên** | CN tổng hợp |
| **Tháng / Năm** | Kỳ tổng hợp |
| **Tổng Ngày Công** | = Đi làm + Nửa ngày × 0.5 |
| **Ngày Đi Làm** | Số ngày đi đủ |
| **Ngày Vắng** | Số ngày vắng |
| **Số Lần Đi Muộn** | Tổng lần late |
| **Ngày Nửa Ca** | Số ngày half_day |
| **Tổng Giờ Tăng Ca** | Tổng OT hours |
| **Tổng Giờ Làm** | Tổng work hours |

> 💡 Nhấn **"Tính Tổng"** để tự động tổng hợp từ chấm công hàng ngày. Dữ liệu liên kết sang module **Lương** để tính lương tháng.

### 18.4 Nghỉ Phép (Leave)

![Nghỉ Phép](images/35_leave.png)
*Hình 42: Danh sách đơn nghỉ phép*

#### Bảng giải thích trường — Nghỉ Phép (garment.leave):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã Đơn** | Char | ✅ | Mã tự động (LV-XXXXX) | `LV-2026-00001` |
| **Nhân Viên** | Many2one | ✅ | Người xin nghỉ | `Nguyễn Thị May` |
| **Loại Nghỉ** | Selection | ✅ | annual (Phép Năm), sick (Ốm), maternity (Thai Sản), personal (Việc Riêng), marriage (Kết Hôn), funeral (Tang Lễ), unpaid (Không Lương), other | `annual` |
| **Từ Ngày** | Date | ✅ | Ngày bắt đầu nghỉ | `2026-02-20` |
| **Đến Ngày** | Date | ✅ | Ngày kết thúc nghỉ | `2026-02-22` |
| **Số Ngày** | Float | 🔄 | Tự tính = Đến - Từ + 1 | `3` |
| **Lý Do** | Text | | Lý do xin nghỉ | `Nghỉ phép năm` |
| **Người Duyệt** | Many2one | 🔄 | Tự set khi duyệt | `Trần Văn Manager` |
| **Trạng Thái** | Selection | | draft → submitted → approved / refused | `approved` |

### 18.5 Tay Nghề (Employee Skill)

![Tay Nghề Công Nhân](images/34_skills.png)
*Hình 42b: Danh sách tay nghề công nhân*

Ghi nhận kỹ năng cho từng nhân viên: loại kỹ năng (may, cắt, QC, ủi, ...) và trình độ (basic, intermediate, advanced, expert).

---

## 19. Module Garment Accounting — Kế Toán VN

**Đường dẫn:** `Công Ty May → Kế Toán`

![Kế Toán](images/84_menu_ke_toan.png)
*Hình 43b: Menu Kế Toán — hóa đơn bán/mua, thanh toán*

### 19.1 Hóa Đơn (Invoice)

![Hóa Đơn Bán](images/29_invoice_sale.png)
*Hình 43: Danh sách hóa đơn bán*

![Hóa Đơn Mua](images/30_invoice_purchase.png)
*Hình 43c: Danh sách hóa đơn mua*

![Chi tiết Hóa Đơn](images/63_invoice_detail.png)
*Hình 44: Form view chi tiết hóa đơn — thuế GTGT, công nợ*

#### Bảng giải thích trường — Hóa Đơn (garment.invoice):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Hóa Đơn** | Char | ✅ | Mã tự động (INV-S/P-XXXXX) | `INV-S-2026-00001` |
| **Loại HĐ** | Selection | ✅ | sale (Hóa Đơn Bán), purchase (Hóa Đơn Mua) | `sale` |
| **Đối Tác** | Many2one | ✅ | Khách hàng / Nhà cung cấp | `H&M Vietnam` |
| **Đơn Hàng May** | Many2one | | Liên kết đơn hàng (nếu có) | `GO-2026-00001` |
| **Ngày Hóa Đơn** | Date | ✅ | Ngày phát hành HĐ | `2026-03-01` |
| **Hạn Thanh Toán** | Date | | Deadline thanh toán | `2026-04-01` |
| **Tiền Tệ** | Many2one | | USD / VND / EUR | `USD` |
| ---- | ---- | ---- | **THUẾ GTGT** | ---- |
| **Thuế GTGT** | Selection | | 0 (0% - Xuất Khẩu), 5 (5%), 8 (8%), 10 (10%), none (Không Thuế) | `0` |
| **Tiền Hàng** | Float | 🔄 | Tổng tiền chưa thuế | `85,000` |
| **Tiền Thuế GTGT** | Float | 🔄 | = Tiền Hàng × % thuế | `0` |
| **Tổng Thanh Toán** | Float | 🔄 | = Tiền Hàng + Thuế | `85,000` |
| ---- | ---- | ---- | **CÔNG NỢ** | ---- |
| **Đã Thanh Toán** | Float | 🔄 | Tổng từ phiếu thanh toán | `50,000` |
| **Còn Nợ** | Float | 🔄 | = Tổng TT - Đã TT | `35,000` |
| ---- | ---- | ---- | **PHÂN LOẠI** | ---- |
| **Phân Loại Chi Phí** | Selection | | material / subcontract / transport / salary / utility / rent / equipment / other — chỉ cho HĐ mua | `material` |
| **Trạng Thái** | Selection | | draft → confirmed → paid / cancelled | `confirmed` |

### 19.2 Chi Tiết Hóa Đơn (Invoice Line):

| Trường | Ý Nghĩa |
|--------|---------|
| **Mô Tả** | Tên hàng hóa / dịch vụ |
| **Số Lượng** | SL (mặc định = 1) |
| **Đơn Vị** | pcs / m / kg / yard / set / lot / month / other |
| **Đơn Giá** | Giá đơn vị |
| **Thành Tiền** | 🔄 = SL × Đơn Giá |

### 19.3 Phiếu Thanh Toán (Payment)

![Thanh Toán](images/31_payments.png)
*Hình 45: Danh sách phiếu thanh toán*

![Chi tiết Thanh Toán](images/64_payment_detail.png)
*Hình 46: Form view chi tiết phiếu thanh toán*

#### Bảng giải thích trường — Phiếu Thanh Toán (garment.payment):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Phiếu** | Char | ✅ | Mã tự động (PM-XXXXX) | `PM-2026-00001` |
| **Hóa Đơn** | Many2one | | Liên kết hóa đơn | `INV-S-2026-00001` |
| **Đối Tác** | Many2one | ✅ | Bên nhận/trả tiền | `H&M Vietnam` |
| **Loại** | Selection | ✅ | inbound (Thu Tiền), outbound (Chi Tiền) | `inbound` |
| **Phương Thức** | Selection | | cash (Tiền Mặt), bank (Chuyển Khoản), lc (L/C), other | `bank` |
| **Ngày Thanh Toán** | Date | ✅ | Ngày thực hiện | `2026-03-15` |
| **Số Tiền** | Float | ✅ | Giá trị thanh toán | `50,000` |
| **Tiền Tệ** | Many2one | | USD / VND | `USD` |
| **Số Tham Chiếu / UNC** | Char | | Mã ủy nhiệm chi / tham chiếu | `UNC-VCB-123456` |
| **Trạng Thái** | Selection | | draft → confirmed / cancelled | `confirmed` |

---

## 20. Module Garment Warehouse — Quản Lý Kho

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng`

![Kho & Giao Hàng menu](images/83_menu_kho.png)
*Hình 47b: Menu Kho & Giao Hàng — nhập/xuất kho, giao hàng gộp chung*

![Phiếu Nhập Kho](images/25_warehouse_in.png)
*Hình 47: Danh sách phiếu nhập kho*

![Phiếu Xuất Kho](images/26_warehouse_out.png)
*Hình 47c: Danh sách phiếu xuất kho*

![Chi tiết Phiếu Kho](images/61_stock_detail.png)
*Hình 48: Form view chi tiết phiếu kho — chi tiết hàng hóa*

### 20.1 Phiếu Kho (Stock Move)

#### Bảng giải thích trường — Phiếu Kho (garment.stock.move):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Mã Phiếu** | Char | ✅ | Mã tự động (GI/GO/GT-XXXXX) | `GI-2026-00001` |
| **Loại Phiếu** | Selection | ✅ | in (Nhập Kho), out (Xuất Kho), transfer (Chuyển Kho) | `in` |
| **Ngày** | Date | ✅ | Ngày thực hiện | `2026-02-01` |
| **Kho Nguồn** | Selection | | npl (Kho NPL), btp (Kho BTP), tp (Kho Thành Phẩm), phu_lieu (Kho Phụ Liệu), other | `npl` |
| **Kho Đích** | Selection | | Tương tự Kho Nguồn | `btp` |
| **Đối Tác** | Many2one | | NCC hoặc Khách hàng | `Công ty Vải ABC` |
| **Đơn Hàng May** | Many2one | | Liên kết đơn hàng | `GO-2026-00001` |
| **Lệnh Sản Xuất** | Many2one | | Liên kết LSX | `PO-2026-00001` |
| **Người Phụ Trách** | Many2one | | NV thực hiện | `Trần Văn Kho` |
| **Chi Tiết** | One2many | | Các dòng hàng hóa | Bảng |
| **Tổng SL** | Float | 🔄 | Tổng số lượng các dòng | `2,000` |
| **Tổng Giá Trị** | Float | 🔄 | Tổng giá trị các dòng | `90,000,000` |
| **Trạng Thái** | Selection | | draft → confirmed → done / cancelled | `done` |

### 20.2 Chi Tiết Phiếu Kho (Stock Move Line):

| Trường | Kiểu | Ý Nghĩa | Giá trị |
|--------|------|---------|---------|
| **Loại Hàng** | Selection | fabric (Vải), accessory (Phụ Liệu), thread (Chỉ), button (Nút/Khóa), label (Nhãn/Tag), packaging (Bao Bì/Thùng), wip (BTP), finished (Thành Phẩm), other | `fabric` |
| **Mô Tả** | Char | Tên hàng | `Vải Cotton Oxford 150cm` |
| **Vải** | Many2one | Liên kết fabric (nếu là vải) | `FAB-001` |
| **Màu** | Many2one | Màu hàng | `Navy` |
| **Đơn Vị** | Selection | m / kg / yard / pcs / roll / box / set / other | `m` |
| **Số Lượng** | Float | Số lượng nhập/xuất | `2,000` |
| **Đơn Giá** | Float | Giá đơn vị | `45,000` |
| **Giá Trị** | Float | 🔄 = SL × Đơn giá | `90,000,000` |
| **Số Lô** | Char | Lot number / mã lô | `LOT-2026-01` |

---

## 21. Module Garment Delivery — Giao Hàng

**Đường dẫn:** `Công Ty May → Kho & Giao Hàng → Phiếu Giao Hàng`

### 21.1 Phương Tiện (Vehicle)

![Phương Tiện](images/28_vehicles.png)
*Hình 49: Danh sách phương tiện giao hàng*

#### Bảng giải thích trường — Phương Tiện (garment.vehicle):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Tên** | Char | ✅ | Tên gọi xe | `Xe tải 5 tấn Hyundai` |
| **Biển Số** | Char | ✅ | Biển số đăng ký (duy nhất) | `51C-12345` |
| **Loại Xe** | Selection | ✅ | truck_small (Tải Nhỏ <3.5T), truck_medium (Tải Trung 3.5-8T), truck_large (Tải Lớn >8T), container_20 (Container 20ft), container_40 (Container 40ft), van (Xe Van), motorbike (Xe Máy) | `truck_medium` |
| **Tài Xế Chính** | Many2one | | Lái xe phụ trách | `Nguyễn Văn Lái` |
| **Tải Trọng Tối Đa (kg)** | Float | | Trọng tải max | `5,000` |
| **Thể Tích Tối Đa (m³)** | Float | | Dung tích max | `20.0` |
| **Trạng Thái** | Selection | | available (Sẵn Sàng), in_use (Đang Sử Dụng), maintenance (Bảo Trì), retired (Ngừng) | `available` |

### 21.2 Đơn Giao Hàng (Delivery Order)

![Đơn Giao Hàng](images/27_delivery.png)
*Hình 50: Danh sách đơn giao hàng*

![Chi tiết Giao Hàng](images/62_delivery_detail.png)
*Hình 51: Form view chi tiết đơn giao hàng — container, B/L*

#### Bảng giải thích trường — Đơn Giao Hàng (garment.delivery.order):

| Trường | Kiểu | Bắt buộc | Ý Nghĩa | Giá trị / Ví dụ |
|--------|------|----------|---------|-----------------|
| **Số Phiếu** | Char | ✅ | Mã tự động (DL-XXXXX) | `DL-2026-00001` |
| **Loại Giao** | Selection | ✅ | customer (Giao Cho Khách), subcontract (Giao Cho GC), internal (Nội Bộ), return (Trả Hàng) | `customer` |
| **Ngày Giao** | Date | ✅ | Ngày giao hàng | `2026-03-15` |
| **Ngày Dự Kiến Đến** | Date | | ETA | `2026-04-05` |
| **KH / Đối Tác** | Many2one | ✅ | Nơi nhận hàng | `H&M Vietnam` |
| **Đơn Hàng May** | Many2one | | Liên kết đơn hàng | `GO-2026-00001` |
| **Packing List** | Many2one | | Liên kết packing list | `PL-2026-00001` |
| **Phương Tiện** | Many2one | | Xe vận chuyển | `Container 40ft #1` |
| **Tài Xế** | Many2one | | Người lái | `Nguyễn Văn Lái` |
| ---- | ---- | ---- | **THÔNG TIN VẬN CHUYỂN** | ---- |
| **Nơi Gửi** | Char | | Địa chỉ gửi | `Nhà Máy - KCN Bình Dương` |
| **Nơi Nhận** | Text | ✅ | Địa chỉ giao | `Hamburg, Germany` |
| **Phương Thức** | Selection | | road / sea / air / rail / courier | `sea` |
| ---- | ---- | ---- | **HÀNG HÓA** | ---- |
| **Tổng Số Thùng** | Integer | | Tổng cartons | `250` |
| **Tổng Số Cái** | Integer | | Tổng pieces | `10,000` |
| **Trọng Lượng Gross (Kg)** | Float | | Gross weight | `3,500` |
| **Trọng Lượng Net (Kg)** | Float | | Net weight | `3,200` |
| **Thể Tích (CBM)** | Float | | Cubic meters | `25.5` |
| ---- | ---- | ---- | **XUẤT KHẨU** | ---- |
| **Số Container** | Char | | Container number | `TGHU1234567` |
| **Số Seal** | Char | | Seal number | `SL-987654` |
| **Số B/L** | Char | | Bill of Lading | `BL-VN-2026-123` |
| **Số Invoice** | Char | | Invoice number | `INV-S-2026-00001` |
| ---- | ---- | ---- | **CHI TIẾT** | ---- |
| **Chi Tiết Hàng Giao** | One2many | | Danh sách hàng giao | Bảng |
| **Tổng SL Giao** | Integer | 🔄 | Tổng từ dòng chi tiết | `10,000` |
| **Ảnh Giao Hàng** | Binary | | Upload ảnh proof of delivery | Upload |
| **Trạng Thái** | Selection | | draft → confirmed → loading → in_transit → delivered / cancelled | `delivered` |

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

## 22. Module Garment Material — Nhập Nguyên Liệu

> **Module:** `garment_material` | **Chức năng:** Quản lý nhập nguyên liệu mua hàng và nguyên liệu khách gửi (CMT/buyer-supplied)

### 22.1 Tổng quan

Module Garment Material quản lý toàn bộ quy trình nhập nguyên liệu, bao gồm:
- **Nhập NL Mua Hàng (Purchase):** Mua nguyên phụ liệu từ nhà cung cấp
- **NL Khách Gửi (Buyer-Supplied / CMT):** Khách hàng gửi nguyên liệu để gia công
- **NL Trả Về Từ SX:** Nguyên liệu thừa trả lại kho
- **NL Từ Gia Công:** Nguyên liệu nhận từ đơn vị gia công
- **Phân Bổ NL Cho SX:** Cấp phát nguyên liệu cho lệnh sản xuất

### 22.2 Phiếu Nhập Nguyên Liệu

**Menu:** Công Ty May → Kho & Giao Hàng → Nhập NL Mua Hàng / NL Khách Gửi (CMT) / Tất Cả Phiếu Nhập NL

![Danh sách phiếu nhập NL](images/90_material_receipt_all.png)
*Hình: Danh sách tất cả phiếu nhập nguyên liệu*

![Phiếu nhập NL mua hàng](images/91_material_receipt_purchase.png)
*Hình: Danh sách phiếu nhập NL mua hàng*

![Phiếu NL khách gửi CMT](images/92_material_receipt_buyer.png)
*Hình: Danh sách phiếu NL khách gửi (CMT)*

#### Tạo phiếu nhập mới:

1. Nhấn **"Mới"** → Chọn **Loại Nhập** (Mua Hàng / Khách Gửi / ...)
2. Điền thông tin:
   - **Nhà Cung Cấp** (bắt buộc nếu Mua Hàng)
   - **Khách Hàng Gửi NL** (bắt buộc nếu Khách Gửi)
   - **Đơn Hàng May** (liên kết đơn hàng)
   - **Ngày Nhập / Ngày Dự Kiến** (tự tính trễ hạn)
   - **Số PO / Hóa Đơn / Thông Tin Vận Chuyển**
3. Thêm chi tiết nguyên liệu:
   - Loại NL (Vải chính, Lót, Dựng, Chỉ, Khóa, Nút, Nhãn, ...)
   - Vải/Phụ liệu, Màu sắc, Số lô
   - SL Đặt / SL Nhận / Đơn giá → Tự tính **Thiếu hụt** và **Giá trị**

![Form nhập NL mới](images/93_material_receipt_form_new.png)
*Hình: Form tạo phiếu nhập nguyên liệu mới*

#### Quy trình xử lý:

```mermaid
stateDiagram-v2
    [*] --> Nháp
    Nháp --> Xác_Nhận: Xác nhận (phải có chi tiết)
    Xác_Nhận --> Đang_Kiểm_Tra: Bắt đầu QC
    Đang_Kiểm_Tra --> Nhập_Kho: QC Đạt → Nhập kho
    Đang_Kiểm_Tra --> QC_Không_Đạt: QC Không Đạt
    QC_Không_Đạt --> Đã_Hủy: Hủy / Xử lý
    Nháp --> Đã_Hủy: Hủy
    Xác_Nhận --> Đã_Hủy: Hủy
```

- **Xác nhận:** Phải có ít nhất 1 dòng chi tiết
- **Đang Kiểm Tra:** Bắt đầu kiểm tra chất lượng (QC)
- **QC Đạt / Không Đạt:** Đánh giá chất lượng nguyên liệu
- **Nhập Kho:** Hoàn tất — chỉ được nhập khi QC đạt/đạt một phần
- **Hủy:** Không thể hủy phiếu đã nhập kho

#### Các loại nguyên liệu hỗ trợ:

| Loại | Mô tả |
|------|-------|
| fabric | Vải chính |
| lining | Vải lót |
| interlining | Vải dựng |
| thread | Chỉ may |
| zipper | Khóa kéo |
| button | Nút / Cúc |
| label | Nhãn mác |
| elastic | Thun / Chun |
| packaging | Bao bì |
| other | Khác |

### 22.3 Phân Bổ Nguyên Liệu Cho Sản Xuất

**Menu:** Công Ty May → Kho & Giao Hàng → Phân Bổ NL Cho SX

![Phân bổ NL](images/94_material_allocation.png)
*Hình: Danh sách phiếu phân bổ nguyên liệu*

![Form phân bổ NL](images/95_material_allocation_form.png)
*Hình: Form phân bổ nguyên liệu cho sản xuất*

#### Cách phân bổ:

1. Chọn **Đơn Hàng May** (bắt buộc) và **Lệnh SX** (tùy chọn)
2. Thêm dòng chi tiết: loại NL, mô tả, SL yêu cầu / SL xuất, số lô, liên kết phiếu nhập
3. Quy trình: **Nháp → Xác Nhận → Đã Xuất Kho**
4. Không thể hủy phiếu đã xuất kho

---

## 23. Module Garment Dashboard — Bảng Điều Khiển

> **Module:** `garment_dashboard` | **Chức năng:** Dashboard tổng quan KPI, tiến độ sản xuất, đơn hàng, cảnh báo

### 23.1 Tổng quan

Module Dashboard cung cấp cái nhìn tổng quan cho quản lý nhà máy:
- **KPI Tổng Quan:** Số liệu tổng hợp từ toàn bộ hệ thống
- **Tổng Quan Đơn Hàng:** Trạng thái, tiến độ, trễ hạn
- **Tiến Độ Sản Xuất:** % hoàn thành, sản lượng, tỷ lệ lỗi
- **Cảnh Báo:** Đơn trễ hạn, LSX hoàn thành thấp, tỷ lệ lỗi cao

### 23.2 KPI Tổng Quan

**Menu:** Công Ty May → Báo Cáo → Dashboard → Tổng Quan KPI

![Dashboard KPI](images/96_dashboard_kpi_graph.png)
*Hình: Biểu đồ KPI tổng quan nhà máy*

17 chỉ số KPI tự động cập nhật:

| KPI | Mô tả |
|-----|-------|
| Tổng Đơn Hàng | Số đơn hàng không bị hủy |
| Đơn Đang SX | Đơn đang ở các giai đoạn sản xuất |
| Đơn Hoàn Thành | Đơn đã giao / hoàn thành |
| Đơn Trễ Hạn | Đơn quá hạn giao chưa hoàn thành |
| Tổng LSX | Tổng lệnh sản xuất |
| LSX Đang Chạy | Lệnh SX đang sản xuất |
| LSX Hoàn Thành | Lệnh SX đã hoàn thành |
| SL Kế Hoạch | Tổng số lượng kế hoạch |
| SL Hoàn Thành | Tổng sản lượng hoàn thành |
| SL Lỗi | Tổng số lỗi phát hiện |
| Tổng QC | Tổng phiếu kiểm tra chất lượng |
| QC Đạt / Không Đạt | Phân loại kết quả QC |
| Tổng Giao Hàng | Phiếu giao hàng |
| Đã Giao | Phiếu đã giao thành công |
| Tổng Phiếu Nhập NL | Phiếu nhập nguyên liệu |
| Phiếu NL Hoàn Thành | Phiếu NL đã nhập kho |

### 23.3 Tổng Quan Đơn Hàng

**Menu:** Công Ty May → Báo Cáo → Dashboard → Tổng Quan Đơn Hàng

![Tổng quan đơn hàng](images/97_dashboard_order_overview.png)
*Hình: Tổng quan đơn hàng — hiển thị trạng thái, tiến độ, trễ hạn*

Thông tin hiển thị:
- Số đơn hàng, khách hàng, mẫu may
- Ngày đặt / Ngày giao / Số ngày còn lại
- Tổng SL / Tổng tiền
- **Trạng thái** (badge màu)
- **Trễ hạn** (đơn quá ngày giao sẽ hiển thị đỏ)
- **Số LSX** liên kết
- **% Hoàn Thành** (thanh tiến trình)

Bộ lọc: Trễ Hạn | Đang SX | Hoàn Thành | Nhóm theo Trạng Thái / Khách Hàng / Mẫu May / Tháng Giao

### 23.4 Tiến Độ Sản Xuất

**Menu:** Công Ty May → Báo Cáo → Dashboard → Tiến Độ Sản Xuất

![Tiến độ sản xuất](images/98_dashboard_production_progress.png)
*Hình: Tiến độ sản xuất — SL kế hoạch, hoàn thành, lỗi, % hoàn thành*

Thông tin chi tiết mỗi lệnh SX:
- SL Kế Hoạch / Hoàn Thành / Còn Lại / Lỗi
- **% Hoàn Thành** (thanh progressbar) + **% Lỗi**
- Chuyền may, ngày bắt đầu / kết thúc dự kiến
- Số ngày sản xuất thực tế

Mã màu:
- 🟢 **Xanh:** Hoàn thành ≥ 100%
- 🟡 **Vàng:** Hoàn thành 50–99%
- 🔴 **Đỏ:** Hoàn thành < 50% (đang SX)

### 23.5 Cảnh Báo & Phát Hiện Sớm

**Menu:** Công Ty May → Báo Cáo → Dashboard → Đơn Trễ Hạn / LSX Hoàn Thành Thấp / LSX Lỗi Cao

![Đơn trễ hạn](images/99_dashboard_late_orders.png)
*Hình: Danh sách đơn hàng trễ hạn*

![LSX hoàn thành thấp](images/100_dashboard_low_completion.png)
*Hình: Lệnh SX có tỷ lệ hoàn thành dưới 50%*

![LSX lỗi cao](images/101_dashboard_high_defect.png)
*Hình: Lệnh SX có tỷ lệ lỗi trên 5%*

3 báo cáo cảnh báo:
- **Đơn Trễ Hạn:** Đơn hàng quá ngày giao mà chưa hoàn thành
- **LSX Hoàn Thành Thấp:** Lệnh SX đang chạy nhưng % hoàn thành < 50%
- **LSX Lỗi Cao:** Lệnh SX có tỷ lệ lỗi > 5% — cần kiểm tra chuyền may

---

## 24. Module Garment CRM — Quan Hệ Khách Hàng

> **Menu:** Công Ty May → CRM

### 24.1 Lead / Cơ Hội Kinh Doanh

Quản lý toàn bộ pipeline bán hàng từ đầu mối (lead) đến chốt đơn.

**Các giai đoạn:**

| Giai Đoạn | Mô Tả |
|-----------|-------|
| Mới | Lead mới nhận được |
| Đã Đánh Giá | Đã xác minh thông tin khách hàng |
| Đã Gửi Báo Giá | Đã gửi quotation/proposal |
| Đang Thương Lượng | Đàm phán giá, điều kiện |
| Thành Công | Chốt đơn hàng |
| Thất Bại | Khách không đặt hàng |

**Cách tạo Lead:**
1. Vào **CRM → Lead / Cơ Hội** → **Tạo Mới**
2. Nhập tiêu đề, loại (Lead/Cơ Hội), khách hàng
3. Thêm thông tin: sản phẩm quan tâm, số lượng dự kiến, doanh thu kỳ vọng
4. Chọn nguồn (website, triển lãm, giới thiệu…), nhân viên phụ trách

**Chuyển Lead → Cơ Hội:** Nhấn **→ Chuyển Cơ Hội** trên lead

**Tạo Đơn Hàng từ CRM:** Khi cơ hội thành công → Nhấn **📋 Tạo Đơn Hàng** → Tự động tạo garment.order

![CRM Lead](images/102_crm_lead_all.png)
![CRM Lead Form](images/105_crm_lead_form_new.png)

### 24.2 Phản Hồi / Khiếu Nại Khách Hàng

Theo dõi feedback, khiếu nại, đề xuất từ khách hàng.

| Loại | Mô Tả |
|------|-------|
| Phản Hồi | Ý kiến chung |
| Khiếu Nại | Vấn đề cần giải quyết |
| Đề Xuất | Góp ý cải thiện |
| Khen Ngợi | Khách hàng hài lòng |

**Luồng xử lý:** Mới → Đang Xử Lý (chỉ định người) → Đã Giải Quyết → Đã Đóng

**Mức độ nghiêm trọng:** Thấp / Trung Bình / Cao / Nghiêm Trọng

![Feedback Form](images/108_crm_feedback_form_new.png)
![Feedback All](images/106_crm_feedback_all.png)

### 24.3 Hồ Sơ Buyer / Khách Hàng

Mở rộng thông tin khách hàng với các trường chuyên biệt ngành may:

- **Loại Buyer:** Thương hiệu, nhà bán lẻ, nhà nhập khẩu, đại lý, bán sỉ
- **Sản phẩm quan tâm, Incoterm ưa thích**
- **SL đặt hàng/năm, doanh thu/năm**
- **Yêu cầu tuân thủ** (BSCI, WRAP, Oeko-Tex…)
- **Tiêu chuẩn chất lượng** (AQL, testing…)
- **Nút thống kê:** Số đơn hàng, số lead, số phản hồi

![Buyers](images/109_crm_buyers.png)

---

## 25. Module Garment Label — In Tem & Quản Lý Pallet

> **Menu:** Công Ty May → Kho & Giao Hàng → Tem / QR Code, Quản Lý Thùng Hàng, Quản Lý Pallet

### 25.1 In Tem / QR Code

Hệ thống quản lý tem với QR code để theo dõi sản phẩm, thùng hàng, pallet và vị trí kho.

**Loại tem:**

| Loại | Prefix | Mô Tả |
|------|--------|-------|
| Tem Sản Phẩm | LP- | Dán trên sản phẩm, chứa thông tin style/màu/size |
| Tem Thùng Hàng | LC- | Dán trên thùng carton, chứa nội dung thùng |
| Tem Pallet | LT- | Dán trên pallet, chứa danh sách thùng |
| Tem Vị Trí Kho | LL- | Đánh dấu vị trí kệ/kho |

**Luồng:** Nháp → Đã In (🖨) → Đã Dán (✓)

**Nội dung QR tự động:** Mã tem | Loại | Đơn hàng | Mã style | Màu | Size | SL

**Quét QR:** Nhấn **📱 Quét QR** để cập nhật thời điểm quét cuối cùng

![Label Form](images/112_label_form_new.png)
![Label All](images/110_label_all.png)

### 25.2 Quản Lý Thùng Hàng (Carton Box)

Quản lý từng thùng hàng riêng lẻ, hỗ trợ đóng/tách/gộp thùng.

**Luồng trạng thái:** Nháp → Đã Đóng → Trên Pallet → Đã Xuất

**Chức năng chính:**
- **Đóng thùng:** Nhập nội dung (style, màu, size, SL) → Đóng
- **Xếp lên Pallet:** Chọn pallet → Nhấn **📦 Xếp Lên Pallet**
- **Tách thùng:** Chia 1 thùng thành 2 (chia đều SL và trọng lượng)
- **Gộp thùng:** Chọn nhiều thùng → Action **Gộp Thùng Hàng** (gộp SL + trọng lượng vào thùng đầu tiên)
- **Tạo tem QR:** Nhấn **🏷 Tạo Tem QR** → Tự động tạo tem loại carton

**CBM tự động:** Tính từ kích thước (Dài × Rộng × Cao / 1,000,000)

![Carton Box Form](images/116_carton_box_form_new.png)
![Carton Box All](images/115_carton_box_all.png)

### 25.3 Quản Lý Pallet

Quản lý pallet chứa nhiều thùng hàng, hỗ trợ gộp/tách pallet.

**Luồng trạng thái:** Nháp → Đang Xếp → Đã Đóng → Đã Xuất

**Chức năng chính:**
- **Tạo pallet:** Chọn loại (Chuẩn/Euro/Đặc biệt), kích thước, trọng tải
- **Xếp thùng:** Thêm thùng hàng vào pallet
- **Đóng pallet:** Khi xếp đủ thùng → Nhấn **✓ Đóng Pallet**
- **Tách pallet:** Chia 1 pallet thành 2 (chia đều số thùng)
- **Gộp pallet:** Chọn nhiều pallet → Action **Gộp Pallet** (chuyển tất cả thùng về pallet đầu tiên)
- **Xuất hàng:** Nhấn **📦 Xuất Hàng** khi pallet đã đóng

**Tổng hợp tự động:** Số thùng, tổng số cái, tổng trọng lượng

![Pallet Form](images/114_pallet_form_new.png)
![Pallet All](images/113_pallet_all.png)

---

## 26. Module Garment Inventory — Kiểm Kê Kho

> **Menu:** Công Ty May → Kho & Giao Hàng → Kiểm Kê Kho

### 26.1 Tổng Quan

Module kiểm kê kho (Stocktaking) cho phép thực hiện kiểm kê định kỳ hoặc đột xuất tại các kho nguyên liệu, thành phẩm, phụ liệu. Hỗ trợ quét QR code để nhập số lượng thực tế nhanh chóng.

### 26.2 Quy Trình Kiểm Kê

| Bước | Trạng Thái | Mô Tả |
|------|-----------|-------|
| 1 | Nháp | Tạo phiên kiểm kê, chọn kho, thêm danh sách hàng |
| 2 | Đang Kiểm Kê | Nhấn **▶ Bắt Đầu**, nhập số lượng thực tế |
| 3 | Hoàn Thành | Nhấn **✓ Hoàn Thành** khi đã kiểm đủ |
| 4 | Đã Xác Nhận | Manager duyệt, tự động tạo phiếu điều chỉnh kho |
| 5 | Hủy | Hủy phiên kiểm kê |

### 26.3 Chi Tiết Kiểm Kê (Inventory Lines)

Mỗi phiên kiểm kê gồm nhiều dòng chi tiết:

| Trường | Mô Tả |
|--------|-------|
| **Loại hàng** | Vải, Phụ liệu, Bao bì, Thành phẩm, Khác |
| **Mã hàng / Tên hàng** | Mã nội bộ & tên mô tả |
| **Tồn sổ sách** | Số lượng theo hệ thống |
| **Tồn thực tế** | Số lượng đếm được |
| **Chênh lệch** | = Thực tế - Sổ sách (tự động) |
| **Trạng thái** | ✅ Khớp / ⚠️ Thừa / ❌ Thiếu (tự động) |
| **Ghi chú** | Giải thích nguyên nhân lệch |

### 26.4 📷 Quét Barcode / QR Camera (Mới)

Tính năng quét barcode/QR code trực tiếp từ camera thiết bị, hỗ trợ kiểm kê nhanh:

**Cách sử dụng:**

1. Tạo phiên kiểm kê → nhấn **▶ Bắt Đầu Kiểm Kê**
2. Nhấn nút **📷 Quét Camera** trên thanh header
3. Trang Scanner mở ra → Nhấn **🎥 Mở Camera Quét Mã**
4. Cho phép trình duyệt truy cập camera
5. Đưa barcode/QR code vào khung quét — hệ thống tự động nhận diện
6. Khi quét thành công: tiếng beep + hiển thị kết quả + tự động thêm vào phiếu kiểm kê
7. Tiếp tục quét mã tiếp theo (không cần click gì thêm)

**Các định dạng mã hỗ trợ:** QR Code, EAN-13, EAN-8, Code 128, Code 39, Code 93, UPC-A, UPC-E, ITF, Data Matrix

**Tính năng:**

| Tính năng | Mô tả |
|-----------|-------|
| **Quét tự động liên tục** | Camera liên tục detect, không cần nhấn nút |
| **Beep khi quét thành công** | Phản hồi âm thanh rõ ràng |
| **Cộng dồn số lượng** | Quét cùng mã 2 lần → SL tự cộng thêm |
| **Lịch sử quét** | Hiển thị 20 mã quét gần nhất |
| **Nhập thủ công** | Input mã + SL bằng tay khi cần |
| **Liên kết tem QR** | Tự tìm tem garment.label, điền thông tin style/color/size |
| **Responsive** | Tối ưu cho cả mobile và desktop |

**Yêu cầu trình duyệt:** Chrome/Edge phiên bản 83+ (hỗ trợ BarcodeDetector API)

> 💡 **Nếu trình duyệt không hỗ trợ camera**, vẫn có thể dùng ô **Nhập Mã Thủ Công** hoặc nút **⌨️ Nhập QR Thủ Công** (wizard cũ).

### 26.5 Quét QR Thủ Công (Wizard)

Nhấn **⌨️ Nhập QR Thủ Công** để mở wizard nhập mã:
- Nhập mã QR bằng tay hoặc qua thiết bị quét USB
- Hệ thống tự động tìm và tăng số lượng thực tế
- Hỗ trợ quét liên tục nhiều mã

### 26.6 Điều Chỉnh Kho Tự Động

Khi Manager xác nhận phiên kiểm kê:
- Hệ thống tự động tạo phiếu điều chỉnh kho (garment.warehouse.move)
- Hàng thừa: Nhập thêm vào kho
- Hàng thiếu: Xuất bớt khỏi kho
- Ghi chú tự động: "Điều chỉnh kiểm kê: [mã phiên]"

![Kiểm kê kho - Danh sách](images/117_inventory_all.png)
*Hình: Danh sách các phiên kiểm kê kho*

![Kiểm kê kho - Form mới](images/118_inventory_form_new.png)
*Hình: Tạo phiên kiểm kê kho mới*

![Kiểm kê đã xác nhận](images/119_inventory_validated.png)
*Hình: Các phiên kiểm kê đã được xác nhận*

---

## 27. Module Garment Print — In Ấn, Xuất Excel & Cảnh Báo Tự Động

### 27.1 Tổng Quan

Module `garment_print` cung cấp 3 tính năng ưu tiên cao:

| Tính Năng | Mô Tả |
|-----------|--------|
| **Báo cáo PDF (QWeb)** | 5 báo cáo PDF chuyên nghiệp in trực tiếp từ hệ thống |
| **Xuất Excel** | Bảng lương & Sản lượng xuất sang file .xlsx |
| **Cảnh báo tự động** | 3 scheduled actions tự động cảnh báo qua Discuss |

### 27.2 Báo Cáo PDF (QWeb Reports)

> **Cách in:** Mở bản ghi → Nút **Print** → Chọn báo cáo tương ứng

| Báo Cáo | Model | Mô Tả |
|----------|-------|--------|
| **Packing List** | `garment.packing.list` | Danh sách đóng gói với thùng carton, trọng lượng, CBM |
| **Phiếu Giao Hàng** | `garment.delivery.order` | Phiếu giao hàng chi tiết theo style/màu/size |
| **Hóa Đơn** | `garment.invoice` | Hóa đơn bán/mua hàng với thuế GTGT tự động |
| **Phiếu Lương** | `garment.wage.calculation` | Phiếu lương cá nhân đầy đủ thu nhập/phụ cấp/khấu trừ |
| **Phiếu Kiểm Tra QC** | `garment.qc.inspection` | Báo cáo kiểm tra chất lượng với tỷ lệ đạt/lỗi |

Mỗi báo cáo được thiết kế song ngữ **Tiếng Việt / English**, có ô ký tên phù hợp quy trình thực tế.

### 27.3 Xuất File Excel

#### 27.3.1 Xuất Bảng Lương

> **Menu:** Công Ty May → Nhân Sự → Xuất Bảng Lương Excel

1. Chọn **Tháng** và **Năm**
2. (Tùy chọn) Lọc theo **Phòng ban** — để trống = tất cả
3. Nhấn **Xuất Excel**
4. Tải file `.xlsx` về máy

File Excel chứa 14 cột: STT, Mã NV, Họ Tên, Phòng Ban, Ngày Công, Lương CB, Lương Ngày Công, Tiền Khoán, Tiền Tăng Ca, Phụ Cấp, BHXH, Thuế TNCN, Tổng Thu Nhập, Thực Lĩnh. Có dòng tổng cộng cuối bảng.

#### 27.3.2 Xuất Sản Lượng

> **Menu:** Công Ty May → Sản Xuất → Xuất Sản Lượng Excel

1. Chọn **Từ ngày** và **Đến ngày**
2. (Tùy chọn) Lọc theo **Chuyền may** — để trống = tất cả
3. Nhấn **Xuất Excel**
4. Tải file `.xlsx` về máy

### 27.4 Cảnh Báo Tự Động (Scheduled Actions)

Hệ thống tự động kiểm tra và gửi cảnh báo qua kênh **Garment Alerts** trên Discuss:

| Cảnh Báo | Tần Suất | Điều Kiện |
|-----------|----------|-----------|
| **Đơn hàng trễ hạn** | Hàng ngày | Đơn hàng quá ngày giao mà chưa hoàn thành |
| **Tỷ lệ QC thấp** | Hàng ngày | Phiếu QC có tỷ lệ đạt < 90% trong 7 ngày qua |
| **Giao hàng sắp đến** | Hàng ngày | Đơn hàng có ngày giao trong 3 ngày tới |

Cảnh báo được gửi dạng bảng HTML chi tiết, dễ đọc trên cả desktop và mobile.

> ⚙️ **Cấu hình:** Vào **Settings → Technical → Scheduled Actions** → Tìm "Garment" để điều chỉnh tần suất hoặc tắt/bật.

---

## 28. Quản Lý Nhân Viên & Phân Quyền

### 27.1 Quản Lý Nhân Viên May

> **Menu:** Công Ty May → Nhân Sự → Nhân Viên May

Module HR được mở rộng với các trường chuyên biệt cho ngành may:

| Trường | Mô Tả |
|--------|-------|
| **Mã nhân viên** | Mã nội bộ (NV-xxx) |
| **Vai trò may** | Thợ may, Thợ cắt, QC, Tổ trưởng, Trưởng chuyền, Trưởng phòng, Kỹ thuật, Kho, Hoàn thiện, Giặt, Bảo trì, Khác |
| **Loại hợp đồng** | Chính thức, Thử việc, Thời vụ, Khoán, Thực tập |
| **Ngày vào làm** | Ngày bắt đầu công tác |
| **Chuyền may** | Liên kết với chuyền sản xuất |
| **CMND/CCCD, BHXH, MST** | Thông tin cá nhân |
| **Ngân hàng & STK** | Thông tin lương |
| **Liên hệ khẩn cấp** | Tên & SĐT người liên hệ |
| **Kỹ năng** | Danh sách kỹ năng (may, cắt, QC, ủi…) với mức độ |

**Các view đặc biệt:**
- **Tổ Trưởng / Trưởng Chuyền:** Lọc nhanh nhân viên có vai trò lãnh đạo
- **Theo Bộ Phận:** Nhóm nhân viên theo phòng ban

![Danh sách nhân viên](images/120_employee_all.png)
*Hình: Danh sách nhân viên may*

![Form nhân viên](images/121_employee_form.png)
*Hình: Thông tin chi tiết nhân viên với các trường chuyên biệt*

![Tổ trưởng](images/122_employee_leaders.png)
*Hình: Danh sách tổ trưởng / trưởng chuyền*

![Theo bộ phận](images/123_employee_by_dept.png)
*Hình: Nhân viên nhóm theo bộ phận*

### 27.2 Kỹ Năng Nhân Viên

> **Menu:** Công Ty May → Nhân Sự → Kỹ Năng Nhân Viên

Theo dõi kỹ năng của từng nhân viên:

| Loại kỹ năng | Mô Tả |
|--------------|-------|
| May | Kỹ năng may các loại đường may |
| Cắt | Kỹ năng cắt vải |
| QC | Kiểm tra chất lượng |
| Ủi / Là | Ủi hoàn thiện sản phẩm |
| Đóng gói | Kỹ năng đóng gói |
| Khác | Kỹ năng đặc biệt khác |

**Mức độ kỹ năng:** Cơ bản → Trung bình → Nâng cao → Chuyên gia

![Kỹ năng nhân viên](images/126_employee_skills.png)
*Hình: Danh sách kỹ năng nhân viên*

### 27.3 Phân Quyền 4 Cấp

Hệ thống phân quyền theo 4 cấp bậc, mỗi cấp kế thừa quyền từ cấp dưới:

| Cấp | Nhóm Quyền | Quyền Hạn |
|-----|-----------|-----------|
| 1 | **Nhân Viên (User)** | Xem tất cả, tạo/sửa dữ liệu liên quan |
| 2 | **Tổ Trưởng (Team Leader)** | + Quản lý nhóm/tổ, duyệt sản lượng |
| 3 | **Trưởng Phòng (Dept Manager)** | + Quản lý phòng ban, duyệt nghỉ phép, xem báo cáo phòng |
| 4 | **Quản Lý (Manager)** | Toàn quyền: tạo, sửa, xóa tất cả dữ liệu |

**Record Rules (Quy tắc truy cập):**
- Nhân viên: Chỉ xem đơn hàng liên quan
- Tổ trưởng: Xem đơn hàng của chuyền mình
- Trưởng phòng: Xem chấm công, nghỉ phép của phòng mình
- Quản lý: Xem tất cả

**Cách phân quyền:**
1. Vào **Settings → Users & Companies → Users**
2. Chọn user → Tab **Access Rights**
3. Tìm mục **Công Ty May** → Chọn cấp quyền phù hợp

![Cài đặt người dùng](images/127_settings_users.png)
*Hình: Quản lý người dùng*

![Phân quyền](images/128_user_permissions.png)
*Hình: Thiết lập quyền truy cập cho người dùng*

---

## 29. Module Garment Mobile — Responsive & Phê Duyệt

> **Module:** `garment_mobile` | **Tests:** 32 ✅

Module tối ưu giao diện cho **điện thoại và máy tính bảng**, đồng thời bổ sung **luồng phê duyệt đơn hàng** (Approval Workflow).

### 29.1 Mobile Dashboard (OWL Component)

Dashboard tối ưu cho mobile với công nghệ **OWL2** (Odoo Web Library):

**Các KPI hiển thị:**
- 📋 **Tổng đơn hàng** — tổng / hoàn thành
- 🏭 **Đang sản xuất** — số đơn đang active
- 🚨 **Đơn trễ hạn** — cần xử lý gấp
- ✅ **Tỉ lệ đạt QC** — pass rate 7 ngày gần nhất
- 📈 **Tiến độ SX** — thanh progress bar tổng thể
- ⏳ **Chờ duyệt** — số đơn pending approval

**Quick Actions (Hành Động Nhanh):**

8 nút bấm nhanh cho phép truy cập 1-tap vào các chức năng chính:
Đơn Hàng | Sản Xuất | Kiểm QC | Giao Hàng | Kho | Nhân Sự | Đóng Gói | Dashboard

**Cảnh báo:**
- 🚨 **Đơn hàng trễ hạn** — hiển thị top 5 đơn trễ nhất, số ngày trễ
- 📅 **Giao hàng sắp tới** — đơn giao trong 3 ngày tới, đếm ngược

**Truy cập:** Menu **Công Ty May → Báo Cáo → 📱 Mobile Dashboard**

### 29.2 Luồng Phê Duyệt Đơn Hàng (Approval Workflow)

Bổ sung luồng duyệt 4 trạng thái cho đơn hàng may:

```
Chưa Gửi Duyệt (draft) → Chờ Duyệt (pending) → Đã Duyệt (approved) ✅
                                                 → Từ Chối (rejected) ❌ → Gửi lại
```

**Các nút thao tác:**
| Nút | Trạng thái | Quyền |
|-----|-----------|-------|
| 📋 **Gửi Duyệt** | draft/rejected → pending | Tất cả user |
| ✅ **Duyệt** | pending → approved (+ auto confirm đơn hàng) | Manager |
| ❌ **Từ Chối** | pending → rejected (mở popup nhập lý do) | Manager |
| 🔄 **Đặt Lại** | any → draft | Manager |

**Wizard Từ Chối:**
- Khi nhấn "Từ Chối", mở popup yêu cầu nhập lý do
- Lý do từ chối hiển thị trong tab Phê Duyệt và chatter

**Tab Phê Duyệt trên form Đơn Hàng:**
- Trạng thái duyệt (badge màu)
- Người gửi duyệt / Ngày gửi
- Người duyệt / Ngày duyệt
- Lý do từ chối (nếu bị từ chối)

**Trên danh sách đơn hàng:**
- Cột "Trạng Thái Duyệt" (badge)
- Filter nhanh: Chờ Duyệt | Đã Duyệt | Từ Chối
- Group by: Trạng Thái Duyệt

### 29.3 Mobile Responsive CSS

Toàn bộ giao diện garment được tối ưu cho mobile:

| Tính năng | Chi tiết |
|-----------|---------|
| **Touch targets** | Tối thiểu 44px (theo Apple HIG) |
| **Input font** | 16px trên input (ngăn iOS zoom) |
| **Kanban** | 1 cột trên phone, 2 cột trên tablet |
| **List view** | Ẩn cột ít quan trọng, cuộn ngang |
| **Statusbar** | Cuộn ngang, overflow-x: auto |
| **Dialogs** | Full-width trên phone, max-height 90vh |
| **One2many** | Cuộn ngang, responsive |
| **Dark mode** | Hỗ trợ prefers-color-scheme |
| **Print** | Ẩn phần không cần khi in |

**Breakpoints:**
- 📱 Phone: < 767px (2 cột KPI, 1 cột kanban)
- 📱 Small phone: < 374px (font nhỏ hơn)
- 📋 Tablet: 768px - 1024px (3 cột KPI, 2 cột kanban)
- 🖥️ Desktop: > 1024px (4 cột KPI, bố cục gốc)

---

## 30. 🔐 Nhật Ký Kiểm Soát (Audit Log)

**Đường dẫn:** `Công Ty May → Cấu Hình → 🔐 Nhật Ký Kiểm Soát`

Tính năng Audit Log ghi nhận chi tiết mọi thay đổi trên dữ liệu quan trọng: **đơn hàng, lương, QC, lệnh sản xuất**. Giúp ban quản lý kiểm soát ai đã sửa/xóa dữ liệu, vào lúc nào, thay đổi gì.

### 30.1 Tính Năng Chính

| Tính Năng | Mô Tả |
|---|---|
| **Tự động ghi log** | Hệ thống tự ghi log khi tạo, sửa, xóa dữ liệu quan trọng |
| **Theo dõi đổi trạng thái** | Ghi riêng khi đơn hàng đổi trạng thái (xác nhận, hủy, hoàn thành...) |
| **Phân mức nghiêm trọng** | 3 mức: Thông tin (info), Cảnh báo (warning), Nghiêm trọng (critical) |
| **Lưu giá trị cũ → mới** | Hiển thị rõ ràng giá trị trước và sau khi thay đổi |
| **Ghi IP người dùng** | Lưu địa chỉ IP thực hiện thao tác |
| **Chỉ đọc** | Log không thể sửa hoặc xóa bởi người dùng |

### 30.2 Các Đối Tượng Được Theo Dõi

| Đối Tượng | Trường Theo Dõi |
|---|---|
| **Đơn Hàng** (garment.order) | Khách hàng, PO, Mẫu may, Ngày giao, Đơn giá, Trạng thái, Tổng SL |
| **Tính Lương** (garment.wage.calculation) | Trạng thái, Lương cơ bản, Tổng lương, Lương net, Thưởng, Khấu trừ |
| **Kiểm Tra QC** (garment.qc.inspection) | Loại KT, Kết quả, Trạng thái, SL kiểm, SL đạt, SL lỗi |
| **Lệnh Sản Xuất** (garment.production.order) | Đơn hàng, Chuyền may, Trạng thái, SL kế hoạch |

### 30.3 Phân Mức Nghiêm Trọng

| Mức | Màu | Khi Nào |
|---|---|---|
| 🔵 **Info** | Xanh | Tạo mới, sửa thông thường |
| 🟡 **Warning** | Vàng | Đổi trạng thái sang hủy/thanh toán/xác nhận |
| 🔴 **Critical** | Đỏ | Xóa bản ghi |

### 30.4 Cách Sử Dụng

1. **Xem log:** Vào `Cấu Hình → 🔐 Nhật Ký Kiểm Soát` — mặc định hiển thị log hôm nay
2. **Lọc nhanh:** Dùng bộ lọc theo hành động (Tạo/Sửa/Xóa), đối tượng (Đơn hàng/Lương/QC), hoặc mức nghiêm trọng
3. **Nhóm dữ liệu:** Nhóm theo Người dùng, Hành động, Đối tượng, hoặc Ngày
4. **Xem chi tiết:** Click vào dòng log để xem form chi tiết — bao gồm giá trị JSON cũ/mới

### 30.5 Phân Quyền

| Vai Trò | Quyền |
|---|---|
| Nhân viên / Trưởng nhóm | Không thấy menu Audit Log |
| Trưởng phòng (Dept Manager) | Xem log (chỉ đọc) |
| Quản trị viên (Administrator) | Xem + toàn quyền quản lý |

> 💡 **Mẹo:** Sử dụng bộ lọc **"Nghiêm Trọng"** để nhanh chóng phát hiện các thao tác xóa dữ liệu quan trọng. Kết hợp nhóm theo **"Người Dùng"** để kiểm soát ai thực hiện nhiều thay đổi nhất.

---

## 31. FAQ — Câu Hỏi Thường Gặp

### Q: Làm sao để thay đổi ngôn ngữ sang Tiếng Việt?
**A:** Vào **Settings → Translations → Load a Translation** → Chọn `Vietnamese / Tiếng Việt` → Install.

### Q: Mã tự động (GO-2026-00001) bị trùng hoặc sai?
**A:** Vào **Settings → Technical → Sequences** → Tìm sequence tương ứng → Kiểm tra & sửa Number Next.

### Q: Làm sao import dữ liệu hàng loạt?
**A:** Trên danh sách bất kỳ → Nhấn ⚙️ → **Import records** → Upload file CSV/Excel.

### Q: Hiệu suất chuyền hiển thị 0%?
**A:** Kiểm tra:
1. Chuyền may có gắn công nhân (worker_ids) không?
2. Style có nhập SAM không?
3. Sản lượng hàng ngày đã nhập chưa?

### Q: Tính lương không hiển thị tiền khoán?
**A:** Kiểm tra:
1. Worker Output đã nhập cho công nhân đó trong tháng chưa?
2. Piece Rate đã thiết lập cho style đó chưa?
3. Nhấn nút **"Tính Lương"** để cập nhật.

### Q: Module không hiển thị trong Apps?
**A:** 
1. Kiểm tra addons_path trong odoo.conf
2. Nhấn **"Update Apps List"** trong Apps
3. Bỏ filter "Apps" và tìm lại

### Q: Luồng nghiệp vụ chính là gì?
**A:** Đơn hàng → Mẫu → Tính giá → Nhập NL → Kế hoạch → Cắt → May → Giặt → Hoàn thiện → QC → Đóng gói → Giao hàng → Kế toán

### Q: Mối liên kết giữa các module?
**A:** Xem [Sơ đồ tổng quan](#2-sơ-đồ-tổng-quan--luồng-nghiệp-vụ) — tất cả module liên kết qua đơn hàng may (garment.order) và lệnh sản xuất (garment.production.order). Module CRM quản lý pipeline khách hàng, module label/pallet quản lý tem QR và đóng gói, module inventory hỗ trợ kiểm kê kho, HR quản lý nhân viên với phân quyền 4 cấp, dashboard tổng hợp dữ liệu từ toàn bộ hệ thống.

---

> 📞 **Hỗ trợ kỹ thuật:** Liên hệ đội phát triển  
> 📖 **Tài liệu Odoo:** https://www.odoo.com/documentation/19.0/
