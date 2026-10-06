"""A minimal standalone Flask app that serves the check-the-box practice problems.

Run it with `uv run check-the-box`, then open http://127.0.0.1:5000/.
"""

from flask import Flask, redirect, url_for

from check_the_box.ctb import ctb_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(ctb_bp)

    @app.route('/')
    def home():
        return redirect(url_for('ctb.check_the_box'))

    return app


def main():
    create_app().run(debug=False)


if __name__ == '__main__':
    main()
