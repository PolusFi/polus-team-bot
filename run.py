import asyncio
import os

from router import app
from scheduler import meeting_notification

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('PORT', default=8000), )
    asyncio.run(meeting_notification())
