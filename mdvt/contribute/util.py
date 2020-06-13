from flask import session

import requests
import secrets

from mdvt import db
from mdvt.config.config import config
from mdvt.database.models import Contribution, FilteredRef, Question
from mdvt.database.util import db_get_existing_entry


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
        config['COMMONS_API_URI'],
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
        config['COMMONS_API_URI'],
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
        config['COMMONS_API_URI'],
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
        config['COMMONS_API_URI'],
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
        config['COMMONS_API_URI'],
        params=params
    ).json()

    return list(response['query']['pages'].keys())[0]


def gen_csrf(question_id):
    csrf = secrets.token_hex(16)
    session['csrf'] = [question_id, csrf]
    return csrf


# TODO: solve 414 or use id instead of titles
def get_questions(filter_type, filter_value, continue_key=None):
    true_count = 0
    false_count = 0
    skip_count = 0
    question_ids = (FilteredRef.query
                    .filter(FilteredRef.filter_type == filter_type)
                    .filter(FilteredRef.filter_value == filter_value)
                    .all())
    for question_id in question_ids:
        question = Question.query.filter_by(id=question_id.id).first()
        true_count = (Contribution.query
                      .filter(Contribution.question_id == question.id)
                      .filter(Contribution.answer == 'true')
                      .count())
        false_count = (Contribution.query
                       .filter(Contribution.question_id == question.id)
                       .filter(Contribution.answer == 'false')
                       .count())
        skip_count = (Contribution.query
                      .filter(Contribution.question_id == question.id)
                      .filter(Contribution.answer == 'skip')
                      .filter(Contribution.user_id == session['user_id'])
                      .count())
        if not true_count and not false_count and not skip_count:
            page = requests.get(
                config['COMMONS_API_URI'],
                params={
                    'action': 'query',
                    'format': 'json',
                    'pageids': question.page_id,
                }
            ).json()

            claim_value = (requests.get(
                config['COMMONS_API_URI'],
                params={
                    'action': 'wbgetclaims',
                    'format': 'json',
                    'claim': question.claim_id,
                }
            ).json()['claims']['P180'][0]['mainsnak']
                    ['datavalue']['value']['id'])

            claim = requests.get(
                config['WIKIDATA_API_URI'],
                params={
                    'action': 'wbgetentities',
                    'format': 'json',
                    'ids': claim_value,
                    'languages': 'en'
                }
            ).json()['entities'][claim_value]
            claim_label = claim['labels']['en']['value']
            claim_description = claim['descriptions']['en']['value']

            page_id = question.page_id

            return_question = {
                'question_id': question.id,
                'media_page': api_info_url(str(page_id)),
                'media_page_id': page_id,
                'media_title': page['query']['pages'][str(page_id)]['title'],
                'depict_id': claim_value,
                'depict_label': claim_label,
                'depict_description': claim_description,
                'claim_id': question.claim_id,
                'csrf': gen_csrf(question.id)
            }
            return return_question

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
        config['COMMONS_API_URI'],
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
                        existing_claim = (
                            db_get_existing_entry(Question,
                                                  type='P180',
                                                  claim_id=depict['id']))
                        if existing_claim is None:
                            new_question = Question(page_id=entity['pageid'],
                                                    type='P180',
                                                    claim_id=depict['id'])
                            db.session.add(new_question)
                            db.session.commit()
                            db.session.add(FilteredRef(
                                question_id=new_question.id,
                                filter_type=filter_type,
                                filter_value=filter_value
                            ))
                            db.session.commit()
            except KeyError:
                continue

        get_questions(filter_type, filter_value, continue_key)


def get_file_depicts(file_name):
    statements = requests.get(
        config['COMMONS_API_URI'],
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
            config['WIKIDATA_API_URI'],
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
