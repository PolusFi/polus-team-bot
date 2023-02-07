import datetime

from aiogram import Bot
from bson import ObjectId

from tgbot.models.db import Database


db = Database()
db.create()


async def add_task(bot: Bot, data: dict):

    print(data)
    try:
        creator = db.getDoc(
            database='polus',
            collection='user',
            search={
                'email': data['creator_email']
            }
        )
        worker = db.getDoc(
            database='polus',
            collection='user',
            search={
                'email': data['person_email']
            }
        )

        try:
            # deadline = data['issue']['fields']['duedate'].split("-")
            deadline_obj = datetime.datetime.date(data['created_time'])
        except:
            deadline_obj = datetime.datetime.now()

        task_doc = {
            "name": data['name'],
            "project": data['project'],
            "story_point": sp,
            "deadline": deadline_obj,
            "status": True,
            "worker": worker['telegram_id'],
            "creator": creator['telegram_id'],
            "active": False
        }
        message = f"📃 <strong>NEW TASK ADDED</strong>\n\n" \
                  f"📁 Project: <strong>{data['project']}</strong>\n" \
                  f"🔖 Task: {data['emoji']} <strong><a href='{data['url']}'>{data['name']}</a></strong>\n" \
                  f"👤 User: <strong>@{worker['username']}</strong> ({data['person_name']})\n\n" \
                  f"💈 Story point: <strong>{sp}</strong>\n" \
                  f"📈 Deadline: <strong>{deadline_obj.strftime('%d/%m/%Y')}</strong>"
        data['id'] = db.addDoc(database='polus', collection='tasks', document=task_doc)
        await bot.send_message(
            chat_id=bot['config'].tg_bot.dev_chat,
            text=message
        )
    except Exception as e:
        print(e)


async def update_task(bot: Bot, data: dict):

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
    task_name = data['issue']['fields']['summary']

    try:
        project_name = data['issue']['fields']['parent']['fields']['summary']
    except:
        project_name = '-'

    try:
        deadline = data['issue']['fields']['duedate'].split("-")
        deadline_obj = datetime.datetime(int(deadline[0]), int(deadline[1]), int(deadline[2]))
    except:
        deadline_obj = datetime.datetime.now()
    try:
        sp = int(data['issue']['fields']['customfield_10016'])
    except:
        sp = 1

    task_doc = db.getDoc(
        database='polus',
        collection='tasks',
        search={
            'code': task_code
        })

    if task_doc:
        task_doc["name"] = task_name
        task_doc["code"] = task_code
        task_doc["project"] = project_name
        task_doc["story_point"] = sp
        task_doc["deadline"] = deadline_obj
        task_doc["worker"] = worker['telegram_id']
        task_doc["creator"] = creator['telegram_id']

        db.updateDoc(
            database='polus',
            collection='tasks',
            search={'_id': task_doc['_id']},
            update_doc=task_doc
        )
    else:
        add_task(bot, data)


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


async def comment_task(bot: Bot, data: dict):

    print(data['issue']['fields']['assignee']['accountId'], data['issue']['fields']['creator']['accountId'])

    task_code = data['issue']['key']
    comment = data['issue']['fields']['description']
    task = db.getDoc(
        database='polus',
        collection='tasks',
        search={
            'code': task_code
        }
    )
    worker = db.getDoc(
        database='polus',
        collection='user',
        search={
            'telegram_id': task['worker']
        }
    )

    message = f"<strong>✏️ NEW COMMENT</strong>\n\n" \
              f"📄 Task: {task['code']} {task['name']} ({task['project']})\n" \
              f"👤 @{worker['username']}\n\n" \
              f"{comment}"

    await bot.send_message(
        chat_id=bot['config'].tg_bot.dev_chat,
        text=message
    )


async def status_task(bot: Bot, data: dict):

    task_code = data['issue']['key']
    status = data['issue']['fields']['status']['name']
    task = db.getDoc(
        database='polus',
        collection='tasks',
        search={
            'code': task_code
        }
    )
    worker = db.getDoc(
        database='polus',
        collection='user',
        search={
            'telegram_id': task['worker']
        }
    )
    if status in ["Готово", "Done"]:
        message = f"<strong>🎉️ TASK DONE 🎉️</strong>\n\n" \
                  f"📄 Task: {task['code']} {task['name']} ({task['project']})\n" \
                  f"<code>Congrats</code> @{worker['username']}!"
    else:
        message = f"<strong>💡 TASK STATUS CHANGED</strong>\n\n" \
                  f"📄 Task: {task['code']} {task['name']} ({task['project']})\n" \
                  f"〽️ Status: {status}"

    await bot.send_message(
        chat_id=bot['config'].tg_bot.dev_chat,
        text=message
    )
