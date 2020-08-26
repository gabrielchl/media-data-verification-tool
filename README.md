# Media Data Verification Tool

This is (so far) a prototype / demo for [my proposal](https://phabricator.wikimedia.org/T247576) for GSoC 2020.

## Quick start guide
1. Create the file mdvt/config/config.py with the following contents:
```
config = {}

config['SECRET_KEY'] = '<flask secret key>'
config['OAUTH_URI'] = 'https://meta.wikimedia.org/w/index.php'
config['OAUTH_TOKEN'] = '<oauth token>'
config['OAUTH_SECRET'] = '<oauth secret>'
config['DATABASE_URI'] = '<sqlalchemy db uri>'
```
2. Run the Flask shell with `flask shell`
3. Run the following commands in the Flask shell to create tables for the database:
```
>>> from mdvt.database.models import User, UserSetting, Contribution
>>> from mdvt import db
>>> db.create_all()
```
4. Install front end dependencies with `npm i`
5. Build JavaScript with `npm run dev` (use `npm run build` for production)
5. Run the tool with `flask run`
