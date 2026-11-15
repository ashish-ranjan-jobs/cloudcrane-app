#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Applied PWA on https://ashish-ranjan.cloud/CloudCrane/
Verifies pre-seeded sample data, interactive demo controls, timeline, search, filters,
offline PWA assets, and CRUD operations using headless Chrome.
"""

import time
import json
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://ashish-ranjan.cloud/CloudCrane/"

def run_tests():
    results = []

    def record(name, passed, detail=""):
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {name}: {detail}")
        results.append({"feature": name, "passed": passed, "detail": detail})

    print(f"=== Starting E2E Verification on {TARGET_URL} ===")

    # 1. Network & Assets Checks
    for path, desc in [
        ("", "Main PWA HTML"),
        ("manifest.json", "Web App Manifest"),
        ("sw.js", "Service Worker Script"),
        ("icon-192.png", "PWA 192px Icon"),
        ("icon.png", "PWA 512px Icon"),
    ]:
        try:
            full_url = TARGET_URL + path
            req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
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
        # Clear any old storage and load fresh like a first-time mobile visitor
        driver.get(TARGET_URL)
        driver.execute_script("localStorage.clear(); sessionStorage.clear(); location.reload();")
        time.sleep(1)

        # Check Title & Header
        title = driver.title
        record("Page Title", "Applied" in title, f"Title is '{title}'")

        brand_text = driver.find_element(By.TAG_NAME, "h1").text
        record("Header Branding", brand_text == "Applied", f"Brand text is '{brand_text}'")

        # Verify Demo Button in Header
        sample_btn = driver.find_element(By.ID, "sampleBtn")
        record("Header Demo Button", sample_btn.is_displayed(), "⚡ Demo button rendered in header")

        # Verify Pre-seeded Sample Data on First Visit
        cards = driver.find_elements(By.CLASS_NAME, "app-card")
        companies = [c.find_element(By.CLASS_NAME, "app-company").text for c in cards]
        record("Sample Data Auto-Population", len(cards) == 4, f"Found {len(cards)} cards: {companies}")
        record("Sample Data: CloudCrane present", "CloudCrane" in companies, "CloudCrane application pre-loaded")
        record("Sample Data: Stripe present", "Stripe" in companies, "Stripe offer pre-loaded")

        # Initial Stats from Sample Data (4 total, 1 applied, 2 interview, 1 offer -> 75% conv rate)
        s_total = driver.find_element(By.ID, "sTotal").text
        s_interview = driver.find_element(By.ID, "sInterview").text
        s_offer = driver.find_element(By.ID, "sOffer").text
        s_applied = driver.find_element(By.ID, "sApplied").text
        conv_rate = driver.find_element(By.ID, "conversionRate").text

        record("Sample Pipeline Counters", s_total == "4" and s_interview == "2" and s_offer == "1" and s_applied == "1",
               f"Total: {s_total}, Applied: {s_applied}, Interview: {s_interview}, Offer: {s_offer}")
        record("Sample Conversion Rate", conv_rate == "75%", f"Conversion rate is {conv_rate}")

        # Feature: Filter Tabs
        # Filter: Offer tab (Stripe)
        driver.find_element(By.XPATH, "//button[@data-filter='offer']").click()
        time.sleep(0.3)
        visible_cards = [c for c in driver.find_elements(By.CLASS_NAME, "app-card") if c.is_displayed()]
        offer_companies = [c.find_element(By.CLASS_NAME, "app-company").text for c in visible_cards]
        record("Filter Tab: Offer Only", offer_companies == ["Stripe"], f"Offer list: {offer_companies}")

        # Filter: Reset to All
        driver.find_element(By.XPATH, "//button[@data-filter='all']").click()
        time.sleep(0.3)
        cards_all = driver.find_elements(By.CLASS_NAME, "app-card")
        record("Filter Tab: Reset to All", len(cards_all) == 4, "All 4 applications visible")

        # Feature: Real-time Search
        search_input = driver.find_element(By.ID, "searchInput")
        search_input.send_keys("Anthropic")
        time.sleep(0.3)
        search_visible = [c.find_element(By.CLASS_NAME, "app-company").text for c in driver.find_elements(By.CLASS_NAME, "app-card") if c.is_displayed()]
        record("Live Search: Company Query", search_visible == ["Anthropic"], f"Found: {search_visible}")

        # Live search by tag
        driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input'));", search_input)
        search_input.send_keys("Remote")
        time.sleep(0.3)
        remote_matches = [c.find_element(By.CLASS_NAME, "app-company").text for c in driver.find_elements(By.CLASS_NAME, "app-card") if c.is_displayed()]
        record("Live Search: Tag Query", "CloudCrane" in remote_matches and "Linear" in remote_matches, f"Remote roles: {remote_matches}")

        # Search No Results Empty State
        driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input'));", search_input)
        search_input.send_keys("NonExistentCompanyXYZ")
        time.sleep(0.3)
        empty_search = driver.find_element(By.CLASS_NAME, "empty-state")
        record("Live Search: No Results Empty State", empty_search.is_displayed(), "Empty state rendered for missing query")

        # Clear search
        driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input'));", search_input)
        time.sleep(0.3)

        # Feature: Open Detail Modal & Check Status History Timeline
        cloudcrane_card = next(c for c in driver.find_elements(By.CLASS_NAME, "app-card") if "CloudCrane" in c.text)
        cloudcrane_card.click()
        time.sleep(0.4)
        edit_modal = driver.find_element(By.ID, "editModal")
        record("Open Detail Modal", "open" in edit_modal.get_attribute("class"), "Details sheet opened")

        # Timeline Verification
        timeline_items = driver.find_elements(By.CLASS_NAME, "timeline-item")
        record("Detail Timeline Entries", len(timeline_items) >= 2, f"Found {len(timeline_items)} timeline items for CloudCrane")

        # Progress CloudCrane to Offer Stage
        edit_status_select = driver.find_element(By.ID, "editStatusSelect")
        edit_status_select.send_keys("Offer")
        driver.find_element(By.ID, "editStageNote").send_keys("Completed final round demo. Received formal offer.")
        driver.find_element(By.ID, "saveEditBtn").click()
        time.sleep(0.4)

        # Check Updated Offer Count
        updated_offers = driver.find_element(By.ID, "sOffer").text
        record("Stage Update Progression", updated_offers == "2", f"Offer count increased to {updated_offers}")

        # Feature: Add New Application via Modal
        add_btn = driver.find_element(By.ID, "openAddBtn")
        add_btn.click()
        time.sleep(0.3)
        driver.find_element(By.ID, "companyInput").send_keys("OpenAI")
        driver.find_element(By.ID, "roleInput").send_keys("Platform Engineer")
        driver.find_element(By.ID, "tagsInput").send_keys("Kubernetes, Systems, SanFrancisco")
        driver.find_element(By.ID, "statusSelect").send_keys("Applied")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(0.5)

        total_after_add = driver.find_element(By.ID, "sTotal").text
        record("Add Application Submission", total_after_add == "5", f"Total applications now: {total_after_add}")

        # Feature: Demo Reload Button (#sampleBtn)
        sample_btn.click()
        time.sleep(0.5)
        reset_total = driver.find_element(By.ID, "sTotal").text
        record("Header Demo Reload Button", reset_total == "4", f"Pipeline cleanly re-seeded to 4 applications")

        # Data Persistence Check (Reload page)
        driver.refresh()
        time.sleep(1)
        persisted_total = driver.find_element(By.ID, "sTotal").text
        record("Data Persistence (Reload)", persisted_total == "4", f"Persisted across page reload: {persisted_total} apps")

        # Console Error Check
        logs = driver.get_log("browser")
        severe_errors = [l for l in logs if l["level"] == "SEVERE"]
        record("Console Error Audit", len(severe_errors) == 0, f"Errors: {severe_errors}")

    finally:
        driver.quit()

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    print(f"\n=== SUMMARY: {passed_count}/{total_count} Tests Passed ===")
    return passed_count == total_count

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
