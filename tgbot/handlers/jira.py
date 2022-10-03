import datetime

from aiogram import Bot
from bson import ObjectId

from tgbot.models.db import Database


db = Database()
db.create()


async def add_task(bot: Bot, data: dict):

    print(data['issue']['fields']['assignee']['accountId'], data['issue']['fields']['creator']['accountId'])

    creator = db.getDoc(
        database='polus',
        collection='user',
        search={
            'jira_id': data['issue']['fields']['creator']['accountId']
        }
    )
    worker = db.getDoc(
        database='polus',
        collection='user',
        search={
            'jira_id':
                data['issue']['fields']['assignee']['accountId']
        }
    )
    task_code = data['issue']['key']
    project = data['issue']['fields']['project']['name']
    task_name = data['issue']['fields']['summary']

    try:
        deadline = data['issue']['fields']['duedate'].split("-")
        deadline_obj = datetime.datetime(int(deadline[0]), int(deadline[1]), int(deadline[2]))
    except:
        deadline_obj = datetime.datetime.now()
    try:
        softline = data['issue']['fields']['customfield_10036'].split("-")
        softline_obj = datetime.datetime(int(softline[0]), int(softline[1]), int(softline[2]))
    except:
        softline_obj = datetime.datetime.now()

    task_doc = db.getDoc(
        database='polus',
        collection='tasks',
        search={
            'code': task_code
        })

    if not task_doc:
        task_doc = {
            "name": task_name,
            "code": task_code,
            "softline": softline_obj,
            "deadline": deadline_obj,
            "status": True,
            "worker": worker['telegram_id'],
            "creator": creator['telegram_id'],
            "active": False
        }
        message = f"📃 <strong>NEW TASK ADDED</strong>\n\n" \
                  f"📁 Project: <strong>{project}</strong>\n" \
                  f"🔖 Task: <strong>{task_code} {task_name}</strong>\n" \
                  f"👤 User: <strong>@{worker['username']}</strong>\n\n" \
                  f"📉 Softline: <strong>{softline_obj.strftime('%d/%m/%Y')}</strong>\n" \
                  f"📈 Deadline: <strong>{deadline_obj.strftime('%d/%m/%Y')}</strong>"
        data['id'] = db.addDoc(database='polus', collection='tasks', document=task_doc)
        await bot.send_message(
            chat_id=bot['config'].tg_bot.dev_chat,
            text=message
        )
    print(creator['username'], worker['username'], task_code, project, task_name, softline_obj, deadline_obj)


async def start_task(bot: Bot, data: dict):

    print(data['issue']['fields']['assignee']['accountId'], data['issue']['fields']['creator']['accountId'])

    creator = db.getDoc(
        database='polus',
        collection='user',
        search={
            'jira_id': data['issue']['fields']['creator']['accountId']
        }
    )
    worker = db.getDoc(
        database='polus',
        collection='user',
        search={
            'jira_id': data['issue']['fields']['assignee']['accountId']
        }
    )
    task_code = data['issue']['key']
    project = data['issue']['fields']['project']['name']
    task_name = data['issue']['fields']['summary']
    task = db.getDoc(
        database='polus',
        collection='tasks',
        search={
            'code': task_code
        }
    )

    task['active'] = True
    db.updateDoc(
        database='polus',
        collection='tasks',
        search={'_id': task['_id']},
        update_doc=task
    )


async def end_task(bot: Bot, data: dict):

    print(data['issue']['fields']['assignee']['accountId'], data['issue']['fields']['creator']['accountId'])

    creator = db.getDoc(
        database='polus',
        collection='user',
        search={
            'jira_id': data['issue']['fields']['creator']['accountId']
        }
    )
    worker = db.getDoc(
        database='polus',
        collection='user',
        search={
            'jira_id': data['issue']['fields']['assignee']['accountId']
        }
    )
    task_code = data['issue']['key']
    project = data['issue']['fields']['project']['name']
    task_name = data['issue']['fields']['summary']
    task = db.getDoc(
        database='polus',
        collection='tasks',
        search={
            'code': task_code
        }
    )

    task['active'] = False
    db.updateDoc(
        database='polus',
        collection='tasks',
        search={'_id': task['_id']},
        update_doc=task
    )
