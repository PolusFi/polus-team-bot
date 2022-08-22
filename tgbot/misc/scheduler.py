import asyncio
import datetime
from aiogram import Bot

from tgbot.models.db import Database

db = Database()
db.create()

async def schedule(bot: Bot):
    # async def sendmsg():
    #     return await bot.send_message(-1001694899040, datetime.datetime.now())
    while True:
        meeting_docs = db.getDocs(database='polus', collection='meetings', search={'status': True})
        for meeting in meeting_docs:
            if meeting['date'].day == datetime.datetime.now().day:
                await bot.send_message(-1001694899040, datetime.datetime.now())