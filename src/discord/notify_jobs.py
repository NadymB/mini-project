from src.utils.logger import get_logger
import requests

logger = get_logger(__name__)

def notify_discord(df, webhook_url):
    """
    Send ALL jobs to Discord (auto split by Discord limit)
    """
    if df.empty:
        logger.info("No data to notify Discord")
        return

    header = "🔥 **New Data jobs (last 7 days)** 🔥\n\n"

    chunks = []
    current = header

    for _, row in df.iterrows():
        msg = (
            f"**{row['job_title']}**\n"
            f"🏢 {row['company']}\n"
            f"📍 {row['address']}\n"
            f"💰 {row['salary']}\n"
            f"🧠 **AI Summary:**\n{row['jd_summary']}\n\n"
            f"🔗 {row.get('url')}\n\n"
        )

        # if over 2000 chars -> push chunk
        if len(current) + len(msg) > 1900:
            chunks.append(current)
            current = msg
        else:
            current += msg

    # push rest of
    if current.strip():
        chunks.append(current)

    logger.info("Sending %d Discord messages", len(chunks))

    for i, content in enumerate(chunks, 1):
        payload = {"content": content}
        resp = requests.post(webhook_url, json=payload, timeout=10)

        if resp.status_code != 204:
            logger.error(
                "Discord notify failed (part %d/%d): %s - %s",
                i, len(chunks), resp.status_code, resp.text
            )
        else:
            logger.info("Discord message %d/%d sent", i, len(chunks))