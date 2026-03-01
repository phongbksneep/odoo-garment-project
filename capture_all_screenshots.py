#!/usr/bin/env python3
"""
Capture ALL screenshots for Garment ERP user guide.
Handles search_default filters by clearing facets via JS.
"""
import os
import sys
import time
import signal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class OperationTimeout(BaseException):
    pass


def timeout_handler(signum, frame):
    raise OperationTimeout("Operation timed out")

BASE_URL = "http://localhost:8069"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "images")
os.makedirs(IMG_DIR, exist_ok=True)

ok_count = 0
fail_count = 0


def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--force-device-scale-factor=1")
    opts.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(3)
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(10)
    return driver


def wait_page_ready(driver, timeout=10):
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


def clear_search_filters(driver):
    """Remove all active search facets."""
    try:
        driver.execute_script("""
            document.querySelectorAll('.o_searchview_facet .o_facet_remove, .o_facet_remove')
                .forEach(function(el) { el.click(); });
        """)
        time.sleep(0.8)
        # Double check
        facets = driver.find_elements(By.CSS_SELECTOR, ".o_facet_remove")
        for f in reversed(facets):
            try:
                f.click()
                time.sleep(0.2)
            except Exception:
                pass
        if facets:
            time.sleep(1)
    except Exception:
        pass


def login(driver):
    driver.get(f"{BASE_URL}/web/login")
    time.sleep(2)
    shot(driver, "01_login.png")
    driver.find_element(By.ID, "login").clear()
    driver.find_element(By.ID, "login").send_keys("admin")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("admin")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    shot(driver, "02_home.png")


def go_action(driver, module, action, wait=5, clear_filters=True):
    url = f"{BASE_URL}/odoo/action-{module}.{action}"
    try:
        driver.get(url)
    except TimeoutException:
        pass  # eager strategy might timeout, page still usable
    time.sleep(wait)
    wait_page_ready(driver)
    if clear_filters:
        clear_search_filters(driver)
    time.sleep(0.5)


def shot(driver, filename):
    global ok_count
    path = os.path.join(IMG_DIR, filename)
    driver.save_screenshot(path)
    size = os.path.getsize(path)
    print(f"  OK {filename} ({size:,} bytes)", flush=True)
    ok_count += 1


def click_first_record(driver, timeout=4):
    try:
        cell = WebDriverWait(driver, timeout).until(
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


def cap_list(driver, fname, mod, act):
    global fail_count
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(30)  # 30 second timeout per screenshot
        go_action(driver, mod, act)
        shot(driver, fname)
        signal.alarm(0)
    except BaseException as e:
        signal.alarm(0)
        if isinstance(e, KeyboardInterrupt):
            raise
        print(f"  FAIL {fname}: {type(e).__name__}: {str(e)[:80]}")
        fail_count += 1
    finally:
        signal.signal(signal.SIGALRM, old_handler)


def cap_detail(driver, fname, mod, act):
    global fail_count
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(30)  # 30 second timeout
        go_action(driver, mod, act)
        signal.alarm(0)
        signal.alarm(15)  # 15 seconds to click and capture
        if click_first_record(driver, timeout=3):
            shot(driver, fname)
        else:
            shot(driver, fname)
            print(f"    (no records, captured list)")
        signal.alarm(0)
    except BaseException as e:
        signal.alarm(0)
        if isinstance(e, KeyboardInterrupt):
            raise
        print(f"  FAIL {fname}: {type(e).__name__}: {str(e)[:80]}")
        fail_count += 1
    finally:
        signal.signal(signal.SIGALRM, old_handler)


# ============================================================
# ALL SCREENSHOTS DEFINITIONS
# ============================================================

LIST_VIEWS = [
    ("03_garment_orders.png",    "garment_base",        "action_garment_order"),
    ("04_styles.png",            "garment_base",        "action_garment_style"),
    ("05_fabrics.png",           "garment_base",        "action_garment_fabric"),
    ("06_accessories.png",       "garment_base",        "action_garment_accessory"),
    ("11_samples.png",           "garment_sample",      "action_sample_order"),
    ("12_costing.png",           "garment_costing",     "action_cost_sheet"),
    ("07_production_orders.png", "garment_production",  "action_production_order"),
    ("08_cutting_orders.png",    "garment_production",  "action_cutting_order"),
    ("09_daily_output.png",      "garment_production",  "action_daily_output"),
    ("10_sewing_lines.png",      "garment_production",  "action_sewing_line"),
    ("13_cutting_advanced.png",  "garment_cutting",     "action_cutting_order_adv"),
    ("14_finishing.png",         "garment_finishing",    "action_finishing_order"),
    ("15_planning.png",          "garment_planning",    "action_production_plan"),
    ("16_line_loading.png",      "garment_planning",    "action_line_loading"),
    ("17_machines.png",          "garment_maintenance",  "action_machine"),
    ("18_maintenance.png",       "garment_maintenance",  "action_maintenance_request"),
    ("19_wash_orders.png",       "garment_washing",     "action_wash_order"),
    ("20_wash_recipes.png",      "garment_washing",     "action_wash_recipe"),
    ("21_subcontract.png",       "garment_subcontract", "action_subcontract_order"),
    ("22_qc_inspections.png",    "garment_quality",     "action_qc_inspection"),
    ("23_compliance.png",        "garment_compliance",  "action_compliance_audit"),
    ("24_packing.png",           "garment_packing",     "action_packing_list"),
    ("25_warehouse_in.png",      "garment_warehouse",   "action_stock_in"),
    ("26_warehouse_out.png",     "garment_warehouse",   "action_stock_out"),
    ("27_delivery.png",          "garment_delivery",    "action_delivery_order"),
    ("28_vehicles.png",          "garment_delivery",    "action_vehicle"),
    ("29_invoice_sale.png",      "garment_accounting",  "action_invoice_sale"),
    ("30_invoice_purchase.png",  "garment_accounting",  "action_invoice_purchase"),
    ("31_payments.png",          "garment_accounting",  "action_payment"),
    ("32_attendance.png",        "garment_hr",          "action_attendance"),
    ("33_attendance_sum.png",    "garment_hr",          "action_attendance_summary"),
    ("34_skills.png",            "garment_hr",          "action_employee_skill"),
    ("35_leave.png",             "garment_hr",          "action_leave"),
    ("36_piece_rate.png",        "garment_payroll",     "action_piece_rate"),
    ("37_worker_output.png",     "garment_payroll",     "action_worker_output"),
    ("38_wage.png",              "garment_payroll",     "action_wage_calculation"),
    ("39_bonus.png",             "garment_payroll",     "action_bonus"),
    ("40_report_efficiency.png", "garment_report",      "action_efficiency_analysis"),
    ("41_report_defect.png",     "garment_report",      "action_defect_analysis"),
]

DETAIL_VIEWS = [
    ("50_order_detail.png",       "garment_base",        "action_garment_order"),
    ("51_style_detail.png",       "garment_base",        "action_garment_style"),
    ("52_production_detail.png",  "garment_production",  "action_production_order"),
    ("53_qc_detail.png",          "garment_quality",     "action_qc_inspection"),
    ("54_finishing_detail.png",   "garment_finishing",    "action_finishing_order"),
    ("55_sample_detail.png",      "garment_sample",      "action_sample_order"),
    ("56_costing_detail.png",     "garment_costing",     "action_cost_sheet"),
    ("57_cutting_detail.png",     "garment_cutting",     "action_cutting_order_adv"),
    ("58_wash_detail.png",        "garment_washing",     "action_wash_order"),
    ("59_subcontract_detail.png", "garment_subcontract", "action_subcontract_order"),
    ("60_packing_detail.png",     "garment_packing",     "action_packing_list"),
    ("61_stock_detail.png",       "garment_warehouse",   "action_stock_in"),
    ("62_delivery_detail.png",    "garment_delivery",    "action_delivery_order"),
    ("63_invoice_detail.png",     "garment_accounting",  "action_invoice_sale"),
    ("64_payment_detail.png",     "garment_accounting",  "action_payment"),
    ("65_attendance_detail.png",  "garment_hr",          "action_attendance"),
    ("66_wage_detail.png",        "garment_payroll",     "action_wage_calculation"),
    ("67_bonus_detail.png",       "garment_payroll",     "action_bonus"),
    ("68_compliance_detail.png",  "garment_compliance",  "action_compliance_audit"),
    ("69_maint_req_detail.png",   "garment_maintenance", "action_maintenance_request"),
    ("70_machine_detail.png",     "garment_maintenance", "action_machine"),
    ("71_output_detail.png",      "garment_production",  "action_daily_output"),
    ("72_sewing_detail.png",      "garment_production",  "action_sewing_line"),
    ("73_plan_detail.png",        "garment_planning",    "action_production_plan"),
]

CRM_LIST = [
    ("102_crm_lead_all.png",     "garment_crm", "action_crm_lead_all"),
    ("106_crm_feedback_all.png", "garment_crm", "action_crm_feedback_all"),
    ("109_crm_buyers.png",       "garment_crm", "action_garment_buyers"),
]
CRM_DETAIL = [
    ("105_crm_lead_form_new.png",     "garment_crm", "action_crm_lead_all"),
    ("108_crm_feedback_form_new.png", "garment_crm", "action_crm_feedback_all"),
]

LABEL_LIST = [
    ("110_label_all.png",      "garment_label", "action_label_all"),
    ("113_pallet_all.png",     "garment_label", "action_pallet_all"),
    ("115_carton_box_all.png", "garment_label", "action_carton_box_all"),
]
LABEL_DETAIL = [
    ("112_label_form_new.png",      "garment_label", "action_label_all"),
    ("114_pallet_form_new.png",     "garment_label", "action_pallet_all"),
    ("116_carton_box_form_new.png", "garment_label", "action_carton_box_all"),
]

INVENTORY_LIST = [
    ("117_inventory_all.png",       "garment_inventory", "action_garment_inventory"),
    ("119_inventory_validated.png", "garment_inventory", "action_garment_inventory_validated"),
]
INVENTORY_DETAIL = [
    ("118_inventory_form_new.png", "garment_inventory", "action_garment_inventory"),
]

HR_LIST = [
    ("120_employee_all.png",     "garment_hr", "action_garment_employee"),
    ("122_employee_leaders.png", "garment_hr", "action_garment_employee_leaders"),
    ("123_employee_by_dept.png", "garment_hr", "action_garment_employee_by_dept"),
    ("126_employee_skills.png",  "garment_hr", "action_employee_skill"),
]
HR_DETAIL = [
    ("121_employee_form.png", "garment_hr", "action_garment_employee"),
]

MATERIAL_LIST = [
    ("90_material_receipt_all.png",      "garment_material", "action_material_receipt_all"),
    ("91_material_receipt_purchase.png", "garment_material", "action_material_receipt_purchase"),
    ("92_material_receipt_buyer.png",    "garment_material", "action_material_receipt_buyer"),
    ("94_material_allocation.png",       "garment_material", "action_material_allocation"),
]
MATERIAL_DETAIL = [
    ("93_material_receipt_form_new.png", "garment_material", "action_material_receipt_all"),
    ("95_material_allocation_form.png",  "garment_material", "action_material_allocation"),
]

DASHBOARD_LIST = [
    ("96_dashboard_kpi_graph.png",           "garment_dashboard", "action_garment_dashboard_kpi"),
    ("97_dashboard_order_overview.png",      "garment_dashboard", "action_order_overview"),
    ("98_dashboard_production_progress.png", "garment_dashboard", "action_production_progress"),
    ("99_dashboard_late_orders.png",         "garment_dashboard", "action_late_orders"),
    ("100_dashboard_low_completion.png",     "garment_dashboard", "action_low_completion"),
    ("101_dashboard_high_defect.png",        "garment_dashboard", "action_high_defect"),
]

MENU_NAMES = [
    ("80_menu_don_hang.png",   "Đơn Hàng"),
    ("81_menu_san_xuat.png",   "Sản Xuất"),
    ("82_menu_chat_luong.png", "Chất Lượng"),
    ("83_menu_kho.png",        "Kho"),
    ("84_menu_ke_toan.png",    "Kế Toán"),
    ("85_menu_nhan_su.png",    "Nhân Sự"),
    ("86_menu_bao_cao.png",    "Báo Cáo"),
    ("87_menu_cau_hinh.png",   "Cấu Hình"),
]


def capture_menus(driver):
    global fail_count
    driver.get(f"{BASE_URL}/odoo/action-garment_base.action_garment_order")
    time.sleep(3)
    wait_page_ready(driver)

    for fname, text in MENU_NAMES:
        try:
            els = driver.find_elements(By.XPATH,
                f"//header//button[contains(./@class,'dropdown')]"
                f"[.//span[contains(text(),'{text}')] or contains(text(),'{text}')]"
                f" | //header//a[contains(./@class,'dropdown')]"
                f"[.//span[contains(text(),'{text}')] or contains(text(),'{text}')]"
            )
            if not els:
                els = driver.find_elements(By.XPATH,
                    f"//*[contains(@class,'o_menu_sections')]//*[contains(text(),'{text}')]"
                )
            if els:
                els[0].click()
                time.sleep(1)
                shot(driver, fname)
                try:
                    driver.find_element(By.CSS_SELECTOR, ".o_action_manager").click()
                except Exception:
                    pass
                time.sleep(0.5)
            else:
                print(f"  WARN {fname}: Menu '{text}' not found")
                fail_count += 1
        except Exception as e:
            print(f"  FAIL {fname}: {e}")
            fail_count += 1


def capture_settings(driver):
    try:
        driver.get(f"{BASE_URL}/odoo/settings/users")
        time.sleep(3)
        wait_page_ready(driver)
        shot(driver, "127_settings_users.png")
        if click_first_record(driver, timeout=3):
            shot(driver, "128_user_permissions.png")
    except Exception as e:
        print(f"  FAIL settings: {e}")


def main():
    driver = create_driver()
    cap_count = [0]  # screenshots taken with current driver

    def ensure_driver(force_new=False):
        """Recreate driver if session died or too many screenshots taken."""
        nonlocal driver
        need_new = force_new or cap_count[0] >= 10
        if not need_new and check_driver_health():
            return driver
        print("  >> Recreating Chrome driver...")
        try:
            driver.quit()
        except Exception:
            pass
        # Kill any stale chromedriver processes
        os.system("pkill -f chromedriver 2>/dev/null")
        time.sleep(1)
        driver = create_driver()
        login_only(driver)
        cap_count[0] = 0
        return driver

    def login_only(d):
        try:
            d.get(f"{BASE_URL}/web/login")
        except TimeoutException:
            pass
        time.sleep(2)
        d.find_element(By.ID, "login").clear()
        d.find_element(By.ID, "login").send_keys("admin")
        d.find_element(By.ID, "password").clear()
        d.find_element(By.ID, "password").send_keys("admin")
        d.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)

    def check_driver_health():
        """Quick health check with timeout. Returns True if driver is alive."""
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        try:
            signal.alarm(5)
            driver.title
            signal.alarm(0)
            return True
        except BaseException:
            signal.alarm(0)
            return False
        finally:
            signal.signal(signal.SIGALRM, old_handler)

    def safe_cap_list(fname, mod, act):
        nonlocal driver
        driver = ensure_driver()
        cap_list(driver, fname, mod, act)
        cap_count[0] += 1
        if not check_driver_health():
            cap_count[0] = 999

    def safe_cap_detail(fname, mod, act):
        nonlocal driver
        driver = ensure_driver()
        cap_detail(driver, fname, mod, act)
        cap_count[0] += 1
        if not check_driver_health():
            cap_count[0] = 999

    try:
        # 1) Login
        print(f"\n{'='*60}\n  STEP 1: Login\n{'='*60}")
        login(driver)

        # 2) List Views
        print(f"\n{'='*60}\n  STEP 2: List Views ({len(LIST_VIEWS)})\n{'='*60}")
        for f, m, a in LIST_VIEWS:
            safe_cap_list(f, m, a)

        # 3) Detail Views
        print(f"\n{'='*60}\n  STEP 3: Detail Views ({len(DETAIL_VIEWS)})\n{'='*60}")
        for f, m, a in DETAIL_VIEWS:
            safe_cap_detail(f, m, a)

        # 4) Menus
        print(f"\n{'='*60}\n  STEP 4: Menus ({len(MENU_NAMES)})\n{'='*60}")
        driver = ensure_driver()
        capture_menus(driver)

        # 5) CRM
        print(f"\n{'='*60}\n  STEP 5: CRM\n{'='*60}")
        for f, m, a in CRM_LIST:
            safe_cap_list(f, m, a)
        for f, m, a in CRM_DETAIL:
            safe_cap_detail(f, m, a)

        # 6) Label
        print(f"\n{'='*60}\n  STEP 6: Label/Pallet/Carton\n{'='*60}")
        for f, m, a in LABEL_LIST:
            safe_cap_list(f, m, a)
        for f, m, a in LABEL_DETAIL:
            safe_cap_detail(f, m, a)

        # 7) Inventory
        print(f"\n{'='*60}\n  STEP 7: Inventory\n{'='*60}")
        for f, m, a in INVENTORY_LIST:
            safe_cap_list(f, m, a)
        for f, m, a in INVENTORY_DETAIL:
            safe_cap_detail(f, m, a)

        # 8) HR
        print(f"\n{'='*60}\n  STEP 8: HR\n{'='*60}")
        for f, m, a in HR_LIST:
            safe_cap_list(f, m, a)
        for f, m, a in HR_DETAIL:
            safe_cap_detail(f, m, a)

        # 9) Material
        print(f"\n{'='*60}\n  STEP 9: Material\n{'='*60}")
        for f, m, a in MATERIAL_LIST:
            safe_cap_list(f, m, a)
        for f, m, a in MATERIAL_DETAIL:
            safe_cap_detail(f, m, a)

        # 10) Dashboard
        print(f"\n{'='*60}\n  STEP 10: Dashboard\n{'='*60}")
        for f, m, a in DASHBOARD_LIST:
            safe_cap_list(f, m, a)

        # 11) Settings
        print(f"\n{'='*60}\n  STEP 11: Settings\n{'='*60}")
        driver = ensure_driver()
        capture_settings(driver)

    except Exception as e:
        print(f"\nFATAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    total = ok_count + fail_count
    print(f"\n{'='*60}")
    print(f"  RESULT: {ok_count}/{total} OK, {fail_count} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
