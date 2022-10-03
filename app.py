# -*- coding: utf-8 -*-

import os
from flask import Flask
from tgbot import config
from flask_cors import CORS

app = Flask(__name__)
# config_env = os.environ.get("CONFIG_ENV")
#
#
# # if hasattr(config, config_env):
# #     if config_env == "DevelopmentConfig":
# #         os.environ["FLASK_ENV"] = "development"
# #
# #     app.config.from_object(getattr(config, config_env))
# # else:
# #     print("fatal error: can't configure app")
# #     exit(0)
#
# if app.config["USE_CORS"]:
#     CORS(app, resources=app.config["CORS"])
