from hashlib import sha256

from flask import flash
from flask_wtf import FlaskForm

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app import app
from flask import session, abort


def get_sha256_hash(data: str) -> str:
    hashed_method = sha256()
    hashed_method.update(data.encode())
    return hashed_method.hexdigest()


def flash_errors(form: FlaskForm) -> None:
    for field, errors in form.errors.items():
        for err in errors:
            flash(err, category="error")


def remove_url_suffix(url: str, suffix: str | list[str]) -> str:
    if type(suffix) == list:
        for sfx in suffix:
            url = url.removesuffix(sfx)
    elif type(suffix) == str:
        url = url.removesuffix(sfx)
    return url


def utc_to_local(dt: datetime, format: str | None = None):

    time_zone = ZoneInfo("Asia/Colombo")
    local_dt = dt.astimezone(tz=time_zone)
    
    return local_dt if format is None else local_dt.strftime(format) 


def session_get_or_404(key: str):
    print('here')
    if data := session.get(key, False):
        return data
    abort(404)
    