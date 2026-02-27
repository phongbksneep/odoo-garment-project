#!/usr/bin/env python3
"""
Capture screenshots for new features: Material Receipt + Dashboard.
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
    print(f"✅ {filename} ({size:,} bytes)")


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


def main():
    driver = create_driver()
    ok = 0
    try:
        login(driver)

        # ===================== MATERIAL RECEIPT =====================
        print("\n" + "=" * 50)
        print("  Material Receipt Screenshots")
        print("=" * 50)

        # All receipts
        go_action(driver, "garment_material", "action_material_receipt_all")
        shot(driver, "90_material_receipt_all.png")
        ok += 1

        # Purchase receipts
        go_action(driver, "garment_material", "action_material_receipt_purchase")
        shot(driver, "91_material_receipt_purchase.png")
        ok += 1

        # Buyer-supplied receipts
        go_action(driver, "garment_material", "action_material_receipt_buyer")
        shot(driver, "92_material_receipt_buyer.png")
        ok += 1

        # Create new receipt form
        go_action(driver, "garment_material", "action_material_receipt_all")
        try:
            new_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".o_list_button_add, .o-kanban-button-new"))
            )
            new_btn.click()
            time.sleep(2)
            wait_page_ready(driver)
            shot(driver, "93_material_receipt_form_new.png")
            ok += 1
        except Exception as e:
            print(f"⚠️ Could not open new form: {e}")

        # Material allocation
        go_action(driver, "garment_material", "action_material_allocation")
        shot(driver, "94_material_allocation.png")
        ok += 1

        # Allocation new form
        try:
            new_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".o_list_button_add, .o-kanban-button-new"))
            )
            new_btn.click()
            time.sleep(2)
            wait_page_ready(driver)
            shot(driver, "95_material_allocation_form.png")
            ok += 1
        except Exception as e:
            print(f"⚠️ Could not open allocation form: {e}")

        # ===================== DASHBOARD =====================
        print("\n" + "=" * 50)
        print("  Dashboard Screenshots")
        print("=" * 50)

        # KPI Dashboard
        go_action(driver, "garment_dashboard", "action_garment_dashboard_kpi")
        shot(driver, "96_dashboard_kpi_graph.png")
        ok += 1

        # Order Overview
        go_action(driver, "garment_dashboard", "action_order_overview")
        shot(driver, "97_dashboard_order_overview.png")
        ok += 1

        # Production Progress
        go_action(driver, "garment_dashboard", "action_production_progress")
        shot(driver, "98_dashboard_production_progress.png")
        ok += 1

        # Late Orders
        go_action(driver, "garment_dashboard", "action_late_orders")
        shot(driver, "99_dashboard_late_orders.png")
        ok += 1

        # Low Completion
        go_action(driver, "garment_dashboard", "action_low_completion")
        shot(driver, "100_dashboard_low_completion.png")
        ok += 1

        # High Defect
        go_action(driver, "garment_dashboard", "action_high_defect")
        shot(driver, "101_dashboard_high_defect.png")
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
