import asyncio

from flask import request, Response
from app import app
from aiogram import types, Dispatcher, Bot
import botwebhook as polus_team_bot

from tgbot.handlers.jira import add_task, start_task, end_task

asyncio.run(polus_team_bot.on_startup(polus_team_bot.dp))


@app.route(polus_team_bot.WEBHOOK_PATH, methods=['POST', 'GET'])
async def bot_hook():

    types.Update()
    telegram_update = types.Update(**request.json)

    Dispatcher.set_current(polus_team_bot.dp)
    Bot.set_current(polus_team_bot.bot)

    await polus_team_bot.dp.process_update(update=telegram_update)
    return Response('ok', status=200)


@app.route("/jira", methods=['POST'])
async def jira_hook():
    print(request.headers.get('Action'))
    if request.headers.get('Action') == "new-task":
        await add_task(polus_team_bot.bot, request.json)
    elif request.headers.get('Action') == "started-task":
        await add_task(polus_team_bot.bot, request.json)
        await start_task(polus_team_bot.bot, request.json)
    elif request.headers.get('Action') == "end-task":
        await end_task(polus_team_bot.bot, request.json)
    return Response('ok', status=200)
