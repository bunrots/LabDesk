from __future__ import annotations

import os

from flask import Flask

from .db import close_db, init_app, init_db
from .routes import bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "labdesk.sqlite"),
        APP_VERSION="v0.2.0",
        DEFAULT_LAB_HEADER="المخبر الطبي\nتقرير نتائج مخبرية",
        DEFAULT_LAB_FOOTER="اسم الفني: __________    التوقيع: __________    الختم: __________",
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    init_app(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(bp)

    with app.app_context():
        init_db()

    return app
