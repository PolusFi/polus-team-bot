import os

from router import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('PORT', default=8000), )
