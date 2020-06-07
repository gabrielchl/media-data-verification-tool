from flask import session

import requests
import secrets

from mdvt import db
from mdvt.database.models import Question


def api_all_images(continue_key=None):
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'allimages',
        'aisort': 'timestamp',
        'aidir': 'descending',
        'ailimit': 50
    }

    if continue_key is not None:
        params['aicontinue'] = continue_key

    response = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params=params
    ).json()

    return (response['query']['allimages'],
            response['continue']['aicontinue'])


def api_category_members(category_name, continue_key=None):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'info',
        'generator': 'categorymembers',
        'inprop': 'url',
        'gcmtitle': category_name,
        'gcmnamespace': '14|6'
    }

    if continue_key is not None:
        params['gcmcontinue'] = continue_key

    response = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params=params
    ).json()

    return (list(response['query']['pages'].values()),
            response['continue']['gcmcontinue'])


def api_tagged_changes(tag, continue_key=None):
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'recentchanges',
        'rctag': tag,
        'rcprop': 'title|timestamp|ids',
        'rclimit': 'max',
        'rctype': 'edit|new|log|categorize|external'
    }

    if continue_key is not None:
        params['rccontinue'] = continue_key

    response = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params=params
    ).json()

    return (response['query']['recentchanges'],
            response['continue']['rccontinue'])


def api_info_url(pageid):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'info',
        'pageids': pageid,
        'inprop': 'url'
    }

    response = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params=params
    ).json()

    return response['query']['pages'][pageid]['fullurl']


def api_get_id(title):
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title
    }

    response = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params=params
    ).json()

    return list(response['query']['pages'].keys())[0]


def get_contrib_request(filter_type, filter_value, continue_key=None):
    if filter_type == 'recent':
        latest_files, continue_key = api_all_images(continue_key)

        for file in latest_files:
            file_depicts = get_file_depicts(file['title'])
            if file_depicts is not None:
                (depict_id, depict_label,
                 depict_description, claim_id) = file_depicts
            else:
                continue

            contribute_request = {
                'media_page': file['descriptionurl'],
                'media_page_id': api_get_id('File:{}', file['title']),
                'media_title': file['title'],
                'depict_id': depict_id,
                'depict_label': depict_label,
                'depict_description': depict_description,
                'claim_id': claim_id,
                'csrf': gen_csrf()
            }
            return contribute_request
    elif filter_type == 'category':
        pages, continue_key = api_category_members(filter_value, continue_key)

        for page in pages:
            if page['ns'] != 6:
                continue
            file_depicts = get_file_depicts(page['title'])
            if file_depicts is not None:
                (depict_id, depict_label,
                 depict_description, claim_id) = file_depicts
            else:
                continue

            contribute_request = {
                'media_page': page['fullurl'],
                'media_page_id': page['pageid'],
                'media_title': page['title'],
                'depict_id': depict_id,
                'depict_label': depict_label,
                'depict_description': depict_description,
                'claim_id': claim_id,
                'csrf': gen_csrf()
            }
            return contribute_request
    elif filter_type == 'tag':
        changes, continue_key = api_tagged_changes(filter_value, continue_key)

        for change in changes:
            if change['ns'] != 6:
                continue
            file_depicts = get_file_depicts(change['title'])
            if file_depicts is not None:
                (depict_id, depict_label,
                 depict_description, claim_id) = file_depicts
            else:
                continue

            contribute_request = {
                'media_page': api_info_url(str(change['pageid'])),
                'media_page_id': change['pageid'],
                'media_title': change['title'],
                'depict_id': depict_id,
                'depict_label': depict_label,
                'depict_description': depict_description,
                'claim_id': claim_id,
                'csrf': gen_csrf()
            }
            return contribute_request

    return get_contrib_request(filter_type, filter_value, continue_key)


def gen_csrf():
    csrf = secrets.token_hex(16)
    session['csrf'] = csrf
    return csrf


# TODO: solve 414 or use id instead of titles
def get_questions(filter_type, filter_value, continue_key=None):
    got_questions = False
    if filter_type == 'recent':
        latest_files, continue_key = api_all_images(continue_key)
        file_titles = {file['title'] for file in latest_files}
    elif filter_type == 'category':
        pages, continue_key = api_category_members(filter_value, continue_key)
        file_titles = {page['title'] for page in pages}
    elif filter_type == 'tag':
        changes, continue_key = api_tagged_changes(filter_value, continue_key)
        file_titles = {change['title'] for change in changes}

    statements = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params={
            'action': 'wbgetentities',
            'format': 'json',
            'sites': 'commonswiki',
            'titles': '|'.join(file_titles)
        }
    ).json()

    if 'entities' in statements:
        entities = list(statements['entities'].values())

        for entity in entities:
            try:
                statements = entity['statements']

                if type(statements) is dict:
                    for depict in statements['P180']:
                        db.session.add(Question(page_id=entity['pageid'],
                                                type='P180',
                                                claim_id=depict['id'],
                                                filter_type='filter_type',
                                                filter_value='filter_value'))
                        db.session.commit()
                        got_questions = True
            except KeyError:
                continue

    if got_questions:
        return
    else:
        get_questions(filter_type, filter_value, continue_key)


def get_file_depicts(file_name):
    statements = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params={
            'action': 'wbgetentities',
            'format': 'json',
            'sites': 'commonswiki',
            'titles': file_name
        }
    ).json()

    try:
        statements = (list(statements['entities'].values())
                      [0]['statements'])

        if 'P180' not in statements:
            return None

        depict_id = (statements['P180'][0]['mainsnak']['datavalue']
                     ['value']['id'])
        claim_id = statements['P180'][0]['id']

        depict = requests.get(
            'https://www.wikidata.org/w/api.php',
            params={
                'action': 'wbgetentities',
                'format': 'json',
                'ids': depict_id,
                'languages': 'en'
            }
        ).json()['entities'][depict_id]
        depict_label = depict['labels']['en']['value']
        depict_description = depict['descriptions']['en']['value']

        return (depict_id, depict_label, depict_description, claim_id)
    except KeyError:
        return None
