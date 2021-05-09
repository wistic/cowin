from bot import sendMessage, start_bot
from logger import logger

if __name__ == "__main__":
    logger.info("bot started")
    updater = start_bot()
    logger.info("started polling")
    updater.start_polling()
    bot = updater.bot
    updater.idle()
