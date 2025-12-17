import csv
from playwright.sync_api import sync_playwright
from src.utils.helper import safe_text, is_empty, parse_date
from src.utils.contants import BASE_URL, COOKIES_TOPDEV_FILE, MAX_PAGE, RAW_DATA_FILE
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import os

rows = []
detail_links = []
# ---------------- crawl list ----------------

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state=COOKIES_TOPDEV_FILE)
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

        cards = page.locator('div.text-card-foreground:has(span.line-clamp-1.font-medium)').all()
        print(f" → Found {len(cards)} jobs")

        for job in cards:
            link_el = job.locator('a[href*="/detail-jobs/"]')

            if link_el.count() == 0:
                continue

            href = link_el.first.get_attribute("href")
            link = f"https://topdev.vn{href}"

            title = safe_text(link_el.first)

            company = safe_text(
                job.locator('span.line-clamp-1.font-medium.text-text-500')
            )

            salary = safe_text(
                job.locator('span.text-brand-500.line-clamp-1.flex.items-center.font-semibold')
            )

            raw_date = safe_text(
                job.locator('span.flex.items-center.gap-1.text-xs.text-text-500')
            )

            period = None
            roles = None

            address = safe_text(
                job.locator('div.mt-2.grid span.line-clamp-1')
            )

            if not address:
                detail_links.append(link)

            if is_empty(raw_date) or is_empty(salary):
                continue

            rows.append({
                "created_date": parse_date(raw_date),
                "job_title": title,
                "company": company,
                "salary": salary,
                "address": address,
                "time": period,
                "link_description": link,
                "jd": roles
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

            # get your role & responsibilities
            lis = page.locator("div.prose-ul ul li")
            texts = lis.all_inner_texts()

            row["jd"] = "\n".join([t.strip() for t in texts if t.strip()])

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

file_exists = os.path.exists(RAW_DATA_FILE)
with open(RAW_DATA_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["created_date", "job_title", "company", "salary", "address", "time", "link_description", "jd"],
        quoting=csv.QUOTE_ALL,
        escapechar="\\"
    )
    if not file_exists:
        writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} jobs to {RAW_DATA_FILE}")

