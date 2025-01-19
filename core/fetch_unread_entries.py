import concurrent.futures
import time
import traceback

from common.logger import logger
from core.process_entries import process_entry


def fetch_unread_entries(config, miniflux_client):
    try:
        entries = miniflux_client.get_entries(status=["unread"], limit=10000)
    except Exception as e:
        logger.error("Failed to fetch unread entries: %s" % e)
        return

    start_time = time.time()

    if len(entries["entries"]) > 0:
        logger.info("Get unread entries: " + str(len(entries["entries"])))
    else:
        logger.info("No new entries")

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config.llm_max_workers
    ) as executor:
        futures = [
            executor.submit(process_entry, miniflux_client, entry)
            for entry in entries["entries"]
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error("generated an exception: %s" % e)

    if len(entries["entries"]) > 0 and time.time() - start_time >= 3:
        logger.info("Done")

    logger.info("fetch_unread_entries completed")
