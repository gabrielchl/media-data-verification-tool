from mdvt import db
from mdvt.database.models import UserSetting


def db_insert_if_not_exist(entry, **kwargs):
    existing_entry = db_get_existing_entry(entry, **kwargs)
    if existing_entry is not None:
        return existing_entry
    else:
        db.session.add(entry)
        db.session.commit()
        return entry


def db_get_existing_entry(model, **kwargs):
    existing_entry = model.query
    for key, value in kwargs.items():
        existing_entry = existing_entry.filter(getattr(model, key) == value)
    existing_entry = existing_entry.first()
    return existing_entry


def db_get_user_setting(user_id, key, default=None):
    entry = db_get_user_setting_entry(user_id, key)
    if entry is not None:
        return db_get_user_setting_entry(user_id, key).value
    else:
        return default


def db_get_user_setting_entry(user_id, key):
    return UserSetting.query.filter_by(user_id=user_id, key=key).first()


def db_set_or_update_user_setting(user_id, key, value):
    entry = db_get_user_setting_entry(user_id, key)
    if entry is not None:
        entry.value = value
        db.session.commit()
    else:
        print('here')
        db.session.add(UserSetting(user_id=user_id,
                                   key=key,
                                   value=value))
        db.session.commit()
