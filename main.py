import os
from bot import create_bot
from search import search
from logger import logger


if __name__ == "__main__":
    # create bot
    logger.info("created bot")
    updater = create_bot()
    bot = updater.bot

    # start bot
    logger.info("starting bot")
    updater.start_polling()

    while True:
        try:
            search()
        except KeyboardInterrupt:
            break

    # stop bot
    try:
        logger.info("stopping bot")
        updater.stop()
        logger.info("exiting")
    except KeyboardInterrupt:
        logger.info("exiting immediately")
        os._exit(os.EX_OK)
