from playwright.sync_api import sync_playwright
from src.utils.helper import safe_text, is_empty, parse_date
from src.utils.contants import BASE_URL, COOKIES_TOPDEV_FILE, MAX_PAGE, RAW_DATA_FILE
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from src.db.db_client import get_engine_pg
from src.db.command_sql import CREATE_RAW_JOBS_TABLE_SQL, INSERT_RAW_JOBS_SQL

rows = []
# ---------------- crawl list ----------------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        storage_state=COOKIES_TOPDEV_FILE
    )
    page = context.new_page()

    for page_num in range(1, MAX_PAGE + 1):
        print(f"Fetching page {page_num}")
        page.goto(f"{BASE_URL}?page={page_num}", timeout=60000, wait_until="domcontentloaded")

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

            if is_empty(raw_date) or is_empty(salary):
                continue

            rows.append({
                "created_date": parse_date(raw_date),
                "job_title": title,
                "company": company,
                "salary": salary,
                "address": address,
                "time": period,
                "url": link,
                "jd": roles
            })

    # ---------------- crawl detail ONLY if needed ----------------
    for row in rows:
        try:
            page.goto(
                row["url"],
                timeout=60000,
                wait_until="domcontentloaded"
            )
            print("Fetching detail", row["url"])

            page.wait_for_timeout(500)

            per_text = page.locator(
                'span.break-none.flex.w-fit.items-center.gap-1.whitespace-nowrap.bg-text-50.p-1.text-xs.text-text-500'
            ).first.text_content()

            if per_text:
                #Remove label and svg if needed
                per_text = per_text.replace("Application deadline:", "").strip()

            row["time"] = parse_date(per_text)

            # get your role & responsibilities
            lis = page.locator("div.prose-ul ul li, span[class*='td-text'], span[style*='font-family']")
            texts = lis.all_inner_texts()

            row["jd"] = "\n".join([t.strip() for t in texts if t.strip()])

            if not row["address"]:
                addr = safe_text(
                    page.locator('div.my-2.grid span.line-clamp-1')
                )
                row["address"] = addr
        except PlaywrightTimeoutError:
            print("⚠️ Timeout → skip", row["url"])
            continue
    browser.close()

# ----------------Insert into DB----------------
if not rows:
    print("No data to insert")
    exit(0)

engine = get_engine_pg()
with engine.begin() as conn:
    conn.execute(CREATE_RAW_JOBS_TABLE_SQL)
    conn.execute(INSERT_RAW_JOBS_SQL, rows)

print(f"Inserted {len(rows)} raw jobs")