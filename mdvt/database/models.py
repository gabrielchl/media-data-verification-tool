from sqlalchemy.sql import func

from mdvt import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sul_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.id, self.sul_id, self.username)


class UserSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    key = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(50))

    def __repr__(self):
        return '<UserSetting {} {} {} {}>'.format(
            self.id, self.user_id, self.key, self.value)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    claim_id = db.Column(db.String(255), nullable=False)
    filter_type = db.Column(db.String(255), nullable=False)
    filter_value = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<Question {} {} {} {} {} {}>'.format(
            self.id, self.page_id, self.type, self.claim_id,
            self.filter_type, self.filter_value)


class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    undo = db.Column(db.Boolean, nullable=False, default=False)
    triggered_change = db.Column(db.Boolean, nullable=False, default=False)
    time_created = db.Column(db.DateTime, nullable=False,
                             server_default=func.now())

    def __repr__(self):
        return '<Contribution {} {} {} {} {} {} {}>'.format(
            self.id, self.user_id, self.page_id, self.data_type, self.data,
            self.undo, self.triggered_change, self.time_created)
