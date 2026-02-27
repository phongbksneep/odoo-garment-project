#!/usr/bin/env python3
"""
Capture screenshots for CRM and Label/Pallet modules.
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

        # ===================== CRM =====================
        print("\n" + "=" * 50)
        print("  CRM Screenshots")
        print("=" * 50)

        # All Leads
        go_action(driver, "garment_crm", "action_crm_lead_all")
        shot(driver, "102_crm_lead_all.png")
        ok += 1

        # Leads only
        go_action(driver, "garment_crm", "action_crm_lead_leads")
        shot(driver, "103_crm_leads.png")
        ok += 1

        # Opportunities
        go_action(driver, "garment_crm", "action_crm_lead_opportunities")
        shot(driver, "104_crm_opportunities.png")
        ok += 1

        # New Lead form
        go_action(driver, "garment_crm", "action_crm_lead_all")
        if click_new_button(driver):
            shot(driver, "105_crm_lead_form_new.png")
            ok += 1

        # Feedback
        go_action(driver, "garment_crm", "action_crm_feedback_all")
        shot(driver, "106_crm_feedback_all.png")
        ok += 1

        # Complaint
        go_action(driver, "garment_crm", "action_crm_complaint")
        shot(driver, "107_crm_complaint.png")
        ok += 1

        # New Feedback form
        go_action(driver, "garment_crm", "action_crm_feedback_all")
        if click_new_button(driver):
            shot(driver, "108_crm_feedback_form_new.png")
            ok += 1

        # Buyers
        go_action(driver, "garment_crm", "action_garment_buyers")
        shot(driver, "109_crm_buyers.png")
        ok += 1

        # ===================== LABEL =====================
        print("\n" + "=" * 50)
        print("  Label / QR Code Screenshots")
        print("=" * 50)

        # All Labels
        go_action(driver, "garment_label", "action_label_all")
        shot(driver, "110_label_all.png")
        ok += 1

        # Product Labels
        go_action(driver, "garment_label", "action_label_product")
        shot(driver, "111_label_product.png")
        ok += 1

        # New Label form
        go_action(driver, "garment_label", "action_label_all")
        if click_new_button(driver):
            shot(driver, "112_label_form_new.png")
            ok += 1

        # ===================== PALLET =====================
        print("\n" + "=" * 50)
        print("  Pallet Screenshots")
        print("=" * 50)

        # All Pallets
        go_action(driver, "garment_label", "action_pallet_all")
        shot(driver, "113_pallet_all.png")
        ok += 1

        # New Pallet form
        if click_new_button(driver):
            shot(driver, "114_pallet_form_new.png")
            ok += 1

        # ===================== CARTON BOX =====================
        print("\n" + "=" * 50)
        print("  Carton Box Screenshots")
        print("=" * 50)

        # All Carton Boxes
        go_action(driver, "garment_label", "action_carton_box_all")
        shot(driver, "115_carton_box_all.png")
        ok += 1

        # New Carton Box form
        if click_new_button(driver):
            shot(driver, "116_carton_box_form_new.png")
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
