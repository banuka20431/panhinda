import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask security params
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret-key")

    # Flask SQLAlchemy params
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI", f"sqlite:///{os.path.join(basedir, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true"
    )

    # Flask session params
    SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT", "False").lower() == "true"
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")

    # Mail server params
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "***@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "***")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True").lower() == "true"

    # Custom paths
    USER_DATA_PATH = os.environ.get(
        "USER_DATA_PATH", os.path.join(basedir, "static", "user_data")
    )

    LOG_DIR = os.environ.get("LOG_DIR", os.path.join(basedir, "logs"))

    APP_URL = os.environ.get("APP_URL", "your-website-url")