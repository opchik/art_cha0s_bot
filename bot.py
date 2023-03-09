import asyncio
from aiogram import Bot, Dispatcher
import configparser  
import time 

config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config['BOTDATA']['BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

from handlers import common, creator, customer, profile
from admin import admin


async def main():
    dp.include_router(common.router)
    dp.include_router(creator.router)
    dp.include_router(customer.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
            
        except Exception as e:
            logging.error(e)
            bot.stop_polling()
            time.sleep(5)
            logging.info("Running again!")
