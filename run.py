from router import app
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('PORT', default=8000), )