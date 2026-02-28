#!/usr/bin/env python3
"""
Capture screenshots for Inventory, Employee Management, and Permission modules.
Phase 12: Kiểm kê kho, Quản lý nhân viên, Phân quyền
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
    driver.get(f"{BASE_URL}/web/login")
    time.sleep(2)
    driver.find_element(By.ID, "login").clear()
    driver.find_element(By.ID, "login").send_keys(username)
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    wait_page_ready(driver)
    print("✅ Logged in")


def go_action(driver, module, action_xml_id, wait=3):
    url = f"{BASE_URL}/odoo/action-{module}.{action_xml_id}"
    driver.get(url)
    time.sleep(wait)
    wait_page_ready(driver)


def shot(driver, filename):
    path = os.path.join(IMG_DIR, filename)
    driver.save_screenshot(path)
    size = os.path.getsize(path)
    print(f"  ✅ {filename} ({size:,} bytes)")


def click_first_record(driver):
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


def click_new_button(driver):
    try:
        new_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".o_list_button_add, .o-kanban-button-new"))
        )
        new_btn.click()
        time.sleep(2)
        wait_page_ready(driver)
        return True
    except Exception:
        return False


def main():
    driver = create_driver()
    ok = 0
    try:
        login(driver)

        # ===================== INVENTORY =====================
        print("\n" + "=" * 50)
        print("  Kiểm Kê Kho (Inventory) Screenshots")
        print("=" * 50)

        # All Inventory Sessions
        go_action(driver, "garment_inventory", "action_garment_inventory")
        shot(driver, "117_inventory_all.png")
        ok += 1

        # New Inventory Form
        if click_new_button(driver):
            shot(driver, "118_inventory_form_new.png")
            ok += 1

        # Validated Inventory
        go_action(driver, "garment_inventory", "action_garment_inventory_validated")
        shot(driver, "119_inventory_validated.png")
        ok += 1

        # ===================== EMPLOYEE MANAGEMENT =====================
        print("\n" + "=" * 50)
        print("  Quản Lý Nhân Viên (Employee) Screenshots")
        print("=" * 50)

        # All Employees
        go_action(driver, "garment_hr", "action_garment_employee")
        shot(driver, "120_employee_all.png")
        ok += 1

        # Employee Form (click first record)
        if click_first_record(driver):
            shot(driver, "121_employee_form.png")
            ok += 1

        # Leaders view
        go_action(driver, "garment_hr", "action_garment_employee_leaders")
        shot(driver, "122_employee_leaders.png")
        ok += 1

        # By Department
        go_action(driver, "garment_hr", "action_garment_employee_by_dept")
        shot(driver, "123_employee_by_dept.png")
        ok += 1

        # ===================== HR - ATTENDANCE =====================
        print("\n" + "=" * 50)
        print("  Chấm Công & Nghỉ Phép Screenshots")
        print("=" * 50)

        # Attendance
        go_action(driver, "garment_hr", "action_attendance")
        shot(driver, "124_attendance_list.png")
        ok += 1

        # Leave
        go_action(driver, "garment_hr", "action_leave")
        shot(driver, "125_leave_list.png")
        ok += 1

        # Skills
        go_action(driver, "garment_hr", "action_employee_skill")
        shot(driver, "126_employee_skills.png")
        ok += 1

        # ===================== SECURITY / PERMISSIONS =====================
        print("\n" + "=" * 50)
        print("  Phân Quyền (Permissions) Screenshots")
        print("=" * 50)

        # Go to Settings > Users
        driver.get(f"{BASE_URL}/odoo/settings/users")
        time.sleep(3)
        wait_page_ready(driver)
        shot(driver, "127_settings_users.png")
        ok += 1

        # Try to open a user to show permission groups
        if click_first_record(driver):
            shot(driver, "128_user_permissions.png")
            ok += 1

        # Go to Settings > Groups (Technical)
        driver.get(f"{BASE_URL}/odoo/settings")
        time.sleep(3)
        wait_page_ready(driver)
        shot(driver, "129_settings_general.png")
        ok += 1

        print(f"\n{'=' * 50}")
        print(f"  DONE: {ok} screenshots captured")
        total = len([f for f in os.listdir(IMG_DIR) if f.endswith('.png')])
        print(f"  Total PNG files in docs/images/: {total}")
        print(f"{'=' * 50}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
