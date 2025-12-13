import csv
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re
from urllib.parse import quote
from src.utils.contants import BASE_URL, job_categories, OUTPUT_STATE, MAX_PAGE, OUTPUT_FILE
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ---------------- utils ----------------

def parse_create_date(text):
    if not text:
        return None
    now = datetime.now()
    text = text.lower()

    m = re.search(r"(\d+)\s*(minute|hour|day|week)s?\s*ago", text)
    if m:
        v, u = int(m.group(1)), m.group(2)
        dt = now - {
            "minute": timedelta(minutes=v),
            "hour": timedelta(hours=v),
            "day": timedelta(days=v),
            "week": timedelta(weeks=v),
        }[u]
        return dt.strftime("%m-%d-%Y")

    m_vi = re.search(r"(\d+)\s*(phút|giờ|ngày|tuần)\s*trước", text)
    if m_vi:
        v, u = int(m_vi.group(1)), m_vi.group(2)
        dt = now - {
            "phút": timedelta(minutes=v),
            "giờ": timedelta(hours=v),
            "ngày": timedelta(days=v),
            "tuần": timedelta(weeks=v),
        }[u]
        return dt.strftime("%m-%d-%Y")

    return None


def safe_text(locator):
    return locator.first.inner_text().strip() if locator.count() > 0 else None


# ---------------- config ----------------

query = f"?job_categories_ids={quote(','.join(map(str, job_categories)))}"
URL = BASE_URL + query

rows = []
detail_links = []

# ---------------- crawl list ----------------

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state=OUTPUT_STATE)
    page = context.new_page()

    for page_num in range(1, MAX_PAGE + 1):
        print(f"Fetching page {page_num}")
        page.goto(f"{BASE_URL}?page={page_num}", timeout=60000)

        previous_height = 0
        while True:
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height

        page.wait_for_selector('a[href*="/detail-jobs/"]', timeout=10000)

        cards = page.locator('a[href*="/detail-jobs/"]').all()
        print(f" → Found {len(cards)} jobs")

        for job in cards:
            title = job.inner_text().strip()
            link = "https://topdev.vn" + job.get_attribute("href")

            card = job.locator(
                "xpath=ancestor::div[contains(@class,'flex')]"
            ).first

            company = safe_text(
                card.locator('span.line-clamp-1.font-medium.text-text-500')
            )

            salary = safe_text(
                card.locator('span.text-brand-500.line-clamp-1.flex.items-center.font-semibold')
            )

            raw_date = safe_text(
                card.locator('span.flex.items-center.gap-1.text-xs.text-text-500')
            )

            period = None

            address = safe_text(
                card.locator('div.mt-2.grid span.line-clamp-1')
            )

            if not address:
                detail_links.append(link)

            rows.append({
                "created_date": parse_create_date(raw_date),
                "job_title": title,
                "company": company,
                "salary": salary,
                "address": address,
                "time": period,
                "link_description": link
            })

    # ---------------- crawl detail ONLY if needed ----------------
    for row in rows:
        try:
            page.goto(
                row["link_description"],
                timeout=60000,
                wait_until="domcontentloaded"
            )
            print("Fetching detail", row["link_description"])

            page.wait_for_timeout(500)

            per_text = page.locator(
                'span.break-none.flex.w-fit.items-center.gap-1.whitespace-nowrap.bg-text-50.p-1.text-xs.text-text-500'
            ).first.text_content()

            if per_text:
                #Remove label and svg if needed
                per_text = per_text.replace("Application deadline:", "").strip()

            row["time"] = per_text

            if not row["address"]:
                addr = safe_text(
                    page.locator('div.my-2.grid span.line-clamp-1')
                )
                row["address"] = addr
        except PlaywrightTimeoutError:
            print("⚠️ Timeout → skip", row["link_description"])
            continue
    browser.close()

# ---------------- save ----------------

with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["created_date", "job_title", "company", "salary", "address", "time", "link_description"]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} jobs to {OUTPUT_FILE}")

