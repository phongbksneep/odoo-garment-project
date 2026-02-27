#!/usr/bin/env python3
"""
Capture all screenshots for Garment ERP user guide.
Uses Selenium with Chrome headless to navigate Odoo and capture screenshots.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://localhost:8069"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "images")
os.makedirs(IMG_DIR, exist_ok=True)


def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--force-device-scale-factor=1")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(3)
    return driver


def wait_page_ready(driver, timeout=8):
    """Wait for page to be fully loaded"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".o_list_view, .o_kanban_view, .o_form_view, "
                 ".o_graph_view, .o_pivot_view, .o_action_manager, "
                 ".o_content, .o_web_client"))
        )
    except TimeoutException:
        pass
    time.sleep(1.5)


def login(driver, username="admin", password="admin"):
    """Login to Odoo and capture login page"""
    driver.get(f"{BASE_URL}/web/login")
    time.sleep(2)
    driver.save_screenshot(os.path.join(IMG_DIR, "01_login.png"))
    print("✅ 01_login.png")

    driver.find_element(By.ID, "login").clear()
    driver.find_element(By.ID, "login").send_keys(username)
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    driver.save_screenshot(os.path.join(IMG_DIR, "02_home.png"))
    print("✅ 02_home.png")


def go_action(driver, module, action_xml_id, wait=3):
    """Navigate to a specific Odoo action URL"""
    url = f"{BASE_URL}/odoo/action-{module}.{action_xml_id}"
    driver.get(url)
    time.sleep(wait)
    wait_page_ready(driver)


def shot(driver, filename):
    """Save screenshot and report"""
    path = os.path.join(IMG_DIR, filename)
    driver.save_screenshot(path)
    size = os.path.getsize(path)
    print(f"✅ {filename} ({size:,} bytes)")


def click_first_record(driver):
    """Click the first record in a list view to open form view"""
    try:
        cell = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".o_data_row td.o_data_cell"))
        )
        cell.click()
        time.sleep(2)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".o_form_view"))
        )
        time.sleep(1)
        return True
    except Exception:
        return False


# ============================================================
# Screenshot definitions
# ============================================================
LIST_VIEWS = [
    # -- Đơn Hàng --
    ("03_garment_orders.png",   "garment_base",       "action_garment_order"),
    ("04_styles.png",           "garment_base",       "action_garment_style"),
    ("05_fabrics.png",          "garment_base",       "action_garment_fabric"),
    ("06_accessories.png",      "garment_base",       "action_garment_accessory"),
    ("11_samples.png",          "garment_sample",     "action_sample_order"),
    ("12_costing.png",          "garment_costing",    "action_cost_sheet"),
    # -- Sản Xuất --
    ("07_production_orders.png","garment_production", "action_production_order"),
    ("08_cutting_orders.png",   "garment_production", "action_cutting_order"),
    ("09_daily_output.png",     "garment_production", "action_daily_output"),
    ("10_sewing_lines.png",     "garment_production", "action_sewing_line"),
    ("13_cutting_advanced.png", "garment_cutting",    "action_cutting_order_adv"),
    ("14_finishing.png",        "garment_finishing",   "action_finishing_order"),
    ("15_planning.png",         "garment_planning",   "action_production_plan"),
    ("16_line_loading.png",     "garment_planning",   "action_line_loading"),
    ("17_machines.png",         "garment_maintenance", "action_machine"),
    ("18_maintenance.png",      "garment_maintenance", "action_maintenance_request"),
    ("19_wash_orders.png",      "garment_washing",    "action_wash_order"),
    ("20_wash_recipes.png",     "garment_washing",    "action_wash_recipe"),
    ("21_subcontract.png",      "garment_subcontract","action_subcontract_order"),
    # -- Chất Lượng --
    ("22_qc_inspections.png",   "garment_quality",    "action_qc_inspection"),
    ("23_compliance.png",       "garment_compliance", "action_compliance_audit"),
    # -- Kho & Giao Hàng --
    ("24_packing.png",          "garment_packing",    "action_packing_list"),
    ("25_warehouse_in.png",     "garment_warehouse",  "action_stock_in"),
    ("26_warehouse_out.png",    "garment_warehouse",  "action_stock_out"),
    ("27_delivery.png",         "garment_delivery",   "action_delivery_order"),
    ("28_vehicles.png",         "garment_delivery",   "action_vehicle"),
    # -- Kế Toán --
    ("29_invoice_sale.png",     "garment_accounting", "action_invoice_sale"),
    ("30_invoice_purchase.png", "garment_accounting", "action_invoice_purchase"),
    ("31_payments.png",         "garment_accounting", "action_payment"),
    # -- Nhân Sự & Lương --
    ("32_attendance.png",       "garment_hr",         "action_attendance"),
    ("33_attendance_sum.png",   "garment_hr",         "action_attendance_summary"),
    ("34_skills.png",           "garment_hr",         "action_employee_skill"),
    ("35_leave.png",            "garment_hr",         "action_leave"),
    ("36_piece_rate.png",       "garment_payroll",    "action_piece_rate"),
    ("37_worker_output.png",    "garment_payroll",    "action_worker_output"),
    ("38_wage.png",             "garment_payroll",    "action_wage_calculation"),
    ("39_bonus.png",            "garment_payroll",    "action_bonus"),
    # -- Báo Cáo --
    ("40_report_efficiency.png","garment_report",     "action_efficiency_analysis"),
    ("41_report_defect.png",    "garment_report",     "action_defect_analysis"),
]

DETAIL_VIEWS = [
    ("50_order_detail.png",       "garment_base",       "action_garment_order"),
    ("51_style_detail.png",       "garment_base",       "action_garment_style"),
    ("52_production_detail.png",  "garment_production", "action_production_order"),
    ("53_qc_detail.png",          "garment_quality",    "action_qc_inspection"),
    ("54_finishing_detail.png",   "garment_finishing",   "action_finishing_order"),
    ("55_sample_detail.png",      "garment_sample",     "action_sample_order"),
    ("56_costing_detail.png",     "garment_costing",    "action_cost_sheet"),
    ("57_cutting_detail.png",     "garment_cutting",    "action_cutting_order_adv"),
    ("58_wash_detail.png",        "garment_washing",    "action_wash_order"),
    ("59_subcontract_detail.png", "garment_subcontract","action_subcontract_order"),
    ("60_packing_detail.png",     "garment_packing",    "action_packing_list"),
    ("61_stock_detail.png",       "garment_warehouse",  "action_stock_in"),
    ("62_delivery_detail.png",    "garment_delivery",   "action_delivery_order"),
    ("63_invoice_detail.png",     "garment_accounting", "action_invoice_sale"),
    ("64_payment_detail.png",     "garment_accounting", "action_payment"),
    ("65_attendance_detail.png",  "garment_hr",         "action_attendance"),
    ("66_wage_detail.png",        "garment_payroll",    "action_wage_calculation"),
    ("67_bonus_detail.png",       "garment_payroll",    "action_bonus"),
    ("68_compliance_detail.png",  "garment_compliance", "action_compliance_audit"),
    ("69_maint_req_detail.png",   "garment_maintenance","action_maintenance_request"),
    ("70_machine_detail.png",     "garment_maintenance","action_machine"),
    ("71_output_detail.png",      "garment_production", "action_daily_output"),
    ("72_sewing_detail.png",      "garment_production", "action_sewing_line"),
    ("73_plan_detail.png",        "garment_planning",   "action_production_plan"),
]


def main():
    driver = create_driver()
    ok = 0
    fail = 0
    try:
        # 1) Login
        print("\n{'='*50}\n  STEP 1: Login\n{'='*50}")
        login(driver)

        # 2) List views
        print(f"\n{'='*50}\n  STEP 2: List View Screenshots ({len(LIST_VIEWS)})\n{'='*50}")
        for fname, mod, act in LIST_VIEWS:
            try:
                go_action(driver, mod, act)
                shot(driver, fname)
                ok += 1
            except Exception as e:
                print(f"❌ {fname}: {e}")
                fail += 1

        # 3) Detail/Form views
        print(f"\n{'='*50}\n  STEP 3: Detail View Screenshots ({len(DETAIL_VIEWS)})\n{'='*50}")
        for fname, mod, act in DETAIL_VIEWS:
            try:
                go_action(driver, mod, act)
                if click_first_record(driver):
                    shot(driver, fname)
                    ok += 1
                else:
                    # No records; just capture the empty list
                    shot(driver, fname)
                    ok += 1
                    print(f"   ⚠️ (no records, captured list view)")
            except Exception as e:
                print(f"❌ {fname}: {e}")
                fail += 1

        # 4) Menu dropdown screenshots
        print(f"\n{'='*50}\n  STEP 4: Menu Structure Screenshots\n{'='*50}")
        driver.get(f"{BASE_URL}/odoo/action-garment_base.action_garment_order")
        time.sleep(3)
        wait_page_ready(driver)

        menu_shots = [
            ("80_menu_don_hang.png",   "Đơn Hàng"),
            ("81_menu_san_xuat.png",   "Sản Xuất"),
            ("82_menu_chat_luong.png", "Chất Lượng"),
            ("83_menu_kho.png",        "Kho"),
            ("84_menu_ke_toan.png",    "Kế Toán"),
            ("85_menu_nhan_su.png",    "Nhân Sự"),
            ("86_menu_bao_cao.png",    "Báo Cáo"),
            ("87_menu_cau_hinh.png",   "Cấu Hình"),
        ]

        for fname, text in menu_shots:
            try:
                els = driver.find_elements(By.XPATH,
                    f"//header//button[contains(./@class,'dropdown')]"
                    f"[.//span[contains(text(),'{text}')] or contains(text(),'{text}')]"
                    f" | //header//a[contains(./@class,'dropdown')]"
                    f"[.//span[contains(text(),'{text}')] or contains(text(),'{text}')]"
                )
                if not els:
                    # Try broader search
                    els = driver.find_elements(By.XPATH,
                        f"//*[contains(@class,'o_menu_sections')]//*[contains(text(),'{text}')]"
                    )
                if els:
                    els[0].click()
                    time.sleep(1)
                    shot(driver, fname)
                    ok += 1
                    # Close dropdown
                    try:
                        driver.find_element(By.CSS_SELECTOR, ".o_action_manager").click()
                    except:
                        pass
                    time.sleep(0.5)
                else:
                    print(f"⚠️  {fname}: Menu '{text}' not found")
                    fail += 1
            except Exception as e:
                print(f"❌ {fname}: {e}")
                fail += 1

        print(f"\n{'='*50}")
        print(f"  DONE: {ok} OK, {fail} FAIL")
        print(f"  Images dir: {IMG_DIR}")
        total_files = len([f for f in os.listdir(IMG_DIR) if f.endswith('.png')])
        print(f"  Total PNG files: {total_files}")
        print(f"{'='*50}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
