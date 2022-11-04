import asyncio

from flask import request, Response
from app import app
from aiogram import types, Dispatcher, Bot
import botwebhook as polus_team_bot

from tgbot.handlers.jira import add_task, start_task, end_task, comment_task, status_task, update_task

asyncio.run(polus_team_bot.on_startup(polus_team_bot.dp))


@app.route(polus_team_bot.WEBHOOK_PATH, methods=['POST', 'GET'])
async def bot_hook():

    try:
        types.Update()
        telegram_update = types.Update(**request.json)

        Dispatcher.set_current(polus_team_bot.dp)
        Bot.set_current(polus_team_bot.bot)

        await polus_team_bot.dp.process_update(update=telegram_update)

    except(Exception) as e:
        print(e)
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
    elif request.headers.get('Action') == "comment-task":
        await comment_task(polus_team_bot.bot, request.json)
    elif request.headers.get('Action') == "status-task":
        await status_task(polus_team_bot.bot, request.json)
    elif request.headers.get('Action') == "update-task":
        await update_task(polus_team_bot.bot, request.json)
    return Response('ok', status=200)
