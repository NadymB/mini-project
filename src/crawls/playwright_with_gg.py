from playwright.sync_api import sync_playwright
from src.utils.contants import OUTPUT_STATE

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    #Go to login page topdev to crawl salary with account authen
    page.goto("https://topdev.vn/job-seeker/login")

    #Close popup the first time to page
    try:
        close_btn = page.locator("#closePopupIntroducePromotion")
        if close_btn.count() > 0:
            close_btn.first.click()
            page.wait_for_timeout(500)
    except:
        pass

    page.wait_for_selector("a:has-text('Tiếp tục với Google')", timeout=10000)
    page.click("a:has-text('Tiếp tục với Google')")

    page.wait_for_timeout(5000)

    print("Please enter email and password Google manual.")

    #Wait to redirect back topdev after login
    page.wait_for_url("https://topdev.vn/users/callback", timeout=0)

    print("✅ Login Google successfully!")

    #Save session to crawl again
    context.storage_state(path=OUTPUT_STATE)
    print(f"✅ Session saved at {OUTPUT_STATE}")

    browser.close()
