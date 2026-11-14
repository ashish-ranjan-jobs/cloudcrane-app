#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Applied PWA on https://ashish-ranjan.cloud
Tests every single feature and interaction using headless Chrome.
"""

import time
import json
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://ashish-ranjan.cloud/"

def run_tests():
    results = []

    def record(name, passed, detail=""):
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {name}: {detail}")
        results.append({"feature": name, "passed": passed, "detail": detail})

    print(f"=== Starting E2E Verification on {TARGET_URL} ===")

    # 1. Network & Assets Checks
    for path, desc in [
        ("/", "Main PWA HTML"),
        ("/manifest.json", "Web App Manifest"),
        ("/sw.js", "Service Worker Script"),
        ("/icon-192.png", "PWA 192px Icon"),
        ("/icon.png", "PWA 512px Icon"),
    ]:
        try:
            req = urllib.request.Request(TARGET_URL.rstrip("/") + path, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                code = resp.getcode()
                record(f"HTTP Asset: {desc}", code == 200, f"Status code {code}")
        except Exception as e:
            record(f"HTTP Asset: {desc}", False, str(e))

    # 2. Browser Interactive Tests
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=390,844") # Mobile viewport
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        # Clear storage and load fresh
        driver.get(TARGET_URL)
        driver.execute_script("localStorage.clear(); location.reload();")
        time.sleep(1)

        # Check Title & Header
        title = driver.title
        record("Page Title", "Applied" in title, f"Title is '{title}'")

        brand_text = driver.find_element(By.TAG_NAME, "h1").text
        record("Header Branding", brand_text == "Applied", f"Brand text is '{brand_text}'")

        # Initial Empty State
        empty_el = driver.find_element(By.CLASS_NAME, "empty-state")
        record("Initial Empty State", empty_el.is_displayed(), "Empty state message shown correctly")

        # Stats counters initially 0
        total_stat = driver.find_element(By.ID, "sTotal").text
        record("Initial Stats Zeroed", total_stat == "0", f"Total count is {total_stat}")

        # Feature: Open Add Modal
        add_btn = driver.find_element(By.ID, "openAddBtn")
        add_btn.click()
        time.sleep(0.3)
        modal = driver.find_element(By.ID, "addModal")
        record("Open Add Application Modal", "open" in modal.get_attribute("class"), "Modal overlay active")

        # Feature: Add Application 1 (CloudCrane)
        driver.find_element(By.ID, "companyInput").send_keys("CloudCrane")
        driver.find_element(By.ID, "roleInput").send_keys("Full Stack Engineer")
        driver.find_element(By.ID, "tagsInput").send_keys("Remote, AI, Cloud")
        driver.find_element(By.ID, "salaryInput").send_keys("$150,000 / year")
        
        # Select Stage: interview
        status_select = driver.find_element(By.ID, "statusSelect")
        status_select.send_keys("Interview")

        # Submit
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(0.5)

        # Verify Application 1 added
        cards = driver.find_elements(By.CLASS_NAME, "app-card")
        record("Add Application Submission", len(cards) == 1, "CloudCrane card added to pipeline")

        card_company = driver.find_element(By.CLASS_NAME, "app-company").text
        record("Card Content: Company", card_company == "CloudCrane", f"Company: '{card_company}'")

        tags = [t.text for t in driver.find_elements(By.CLASS_NAME, "app-tag")]
        record("Card Content: Tags", "#Remote" in tags and "#AI" in tags, f"Tags parsed: {tags}")

        # Stats check
        s_interview = driver.find_element(By.ID, "sInterview").text
        s_total = driver.find_element(By.ID, "sTotal").text
        conv_rate = driver.find_element(By.ID, "conversionRate").text
        record("Pipeline Counter: Interview", s_interview == "1" and s_total == "1", f"Total: {s_total}, Interview: {s_interview}")
        record("Conversion Rate Analytics", conv_rate == "100%", f"Conversion rate is {conv_rate}")

        # Feature: Add Application 2 (Google)
        add_btn.click()
        time.sleep(0.3)
        driver.find_element(By.ID, "companyInput").send_keys("Google")
        driver.find_element(By.ID, "roleInput").send_keys("Staff Software Engineer")
        driver.find_element(By.ID, "tagsInput").send_keys("Backend, Infra")
        driver.find_element(By.ID, "statusSelect").send_keys("Applied")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(0.5)

        cards = driver.find_elements(By.CLASS_NAME, "app-card")
        record("Add Second Application", len(cards) == 2, "Both cards in list")

        conv_rate_2 = driver.find_element(By.ID, "conversionRate").text
        record("Conversion Rate Recalculated", conv_rate_2 == "50%", f"1 of 2 converted = {conv_rate_2}")

        # Feature: Filter Tabs
        # Filter: Interview tab
        driver.find_element(By.XPATH, "//button[@data-filter='interview']").click()
        time.sleep(0.3)
        visible_cards = [c for c in driver.find_elements(By.CLASS_NAME, "app-card") if c.is_displayed()]
        companies = [c.find_element(By.CLASS_NAME, "app-company").text for c in visible_cards]
        record("Filter Tab: Interview Only", companies == ["CloudCrane"], f"Filtered list: {companies}")

        # Filter: Offer tab (empty)
        driver.find_element(By.XPATH, "//button[@data-filter='offer']").click()
        time.sleep(0.3)
        empty_displayed = driver.find_element(By.CLASS_NAME, "empty-state").is_displayed()
        record("Filter Tab: Empty State", empty_displayed, "Empty view prompt rendered")

        # Filter: Reset to All
        driver.find_element(By.XPATH, "//button[@data-filter='all']").click()
        time.sleep(0.3)
        cards_all = driver.find_elements(By.CLASS_NAME, "app-card")
        record("Filter Tab: Reset to All", len(cards_all) == 2, "2 applications visible")

        # Feature: Real-time Search
        search_input = driver.find_element(By.ID, "searchInput")
        search_input.send_keys("Google")
        time.sleep(0.3)
        search_visible = [c.find_element(By.CLASS_NAME, "app-company").text for c in driver.find_elements(By.CLASS_NAME, "app-card") if c.is_displayed()]
        record("Live Search: Company Query", search_visible == ["Google"], f"Found: {search_visible}")

        search_input.clear()
        search_input.send_keys("Remote")
        time.sleep(0.3)
        tag_search_visible = [c.find_element(By.CLASS_NAME, "app-company").text for c in driver.find_elements(By.CLASS_NAME, "app-card") if c.is_displayed()]
        record("Live Search: Tag Query", tag_search_visible == ["CloudCrane"], f"Found: {tag_search_visible}")

        search_input.clear()
        search_input.send_keys("xyznonexistent")
        time.sleep(0.3)
        no_res = driver.find_element(By.CLASS_NAME, "empty-state").is_displayed()
        record("Live Search: No Results Empty State", no_res, "Empty state rendered for missing query")

        driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input'));", search_input)
        time.sleep(0.5)

        # Feature: Detail Modal & Stage History Timeline
        cloudcrane_card = next(c for c in driver.find_elements(By.CLASS_NAME, "app-card") if "CloudCrane" in c.text)
        cloudcrane_card.click()
        time.sleep(0.3)

        edit_modal = driver.find_element(By.ID, "editModal")
        record("Open Detail Modal", "open" in edit_modal.get_attribute("class"), "Details sheet opened")

        # Check initial timeline item
        initial_timeline = driver.find_elements(By.CLASS_NAME, "timeline-item")
        record("Initial Timeline Entry", len(initial_timeline) >= 1, f"Found {len(initial_timeline)} timeline items")

        # Update stage to Offer with transition note
        driver.find_element(By.ID, "editStatusSelect").send_keys("Offer")
        driver.find_element(By.ID, "editStageNote").send_keys("Received offer letter!")
        driver.find_element(By.ID, "saveEditBtn").click()
        time.sleep(0.5)

        # Reopen to verify updated timeline
        cloudcrane_card = next(c for c in driver.find_elements(By.CLASS_NAME, "app-card") if "CloudCrane" in c.text)
        cloudcrane_card.click()
        time.sleep(0.3)

        updated_timeline = driver.find_elements(By.CLASS_NAME, "timeline-item")
        stages = [item.find_element(By.CLASS_NAME, "timeline-stage").text.lower() for item in updated_timeline]
        record("Stage History Progression", "offer" in stages and len(updated_timeline) >= 2, f"Timeline entries: {stages}")

        driver.find_element(By.ID, "closeEditBtn").click()
        time.sleep(0.3)

        # Feature: Persistence across Browser Reload (Local Storage Data Integrity)
        driver.refresh()
        time.sleep(1)

        reloaded_cards = driver.find_elements(By.CLASS_NAME, "app-card")
        reloaded_companies = [c.find_element(By.CLASS_NAME, "app-company").text for c in reloaded_cards]
        record("Data Persistence (Reload)", "CloudCrane" in reloaded_companies and "Google" in reloaded_companies, f"Persisted: {reloaded_companies}")

        # Feature: Delete Application
        google_card = next(c for c in driver.find_elements(By.CLASS_NAME, "app-card") if "Google" in c.text)
        google_card.click()
        time.sleep(0.3)
        driver.find_element(By.ID, "deleteAppBtn").click()
        time.sleep(0.5)

        remaining_cards = driver.find_elements(By.CLASS_NAME, "app-card")
        remaining_companies = [c.find_element(By.CLASS_NAME, "app-company").text for c in remaining_cards]
        record("Delete Application", len(remaining_cards) == 1 and remaining_companies == ["CloudCrane"], f"Remaining: {remaining_companies}")

        # Feature: Export Functionality (Doesn't throw errors)
        export_btn = driver.find_element(By.ID, "exportBtn")
        driver.execute_script("arguments[0].click();", export_btn)
        time.sleep(0.5)
        # Check browser console for errors
        logs = driver.get_log("browser")
        severe_errors = [l for l in logs if l["level"] == "SEVERE"]
        record("Console Error Audit", len(severe_errors) == 0, f"Errors: {severe_errors}")

    finally:
        driver.quit()

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n=== SUMMARY: {passed}/{total} Tests Passed ===")
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
