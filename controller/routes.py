from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify, Response, flash, session
import requests
from controller import db_access, functions
import _conf as conf
import json
from uuid import uuid4
from flask_login import login_required, current_user, login_user, logout_user, login_manager
from model.user import User

from controller.functions import get_policy_json

# JSON vocabularies that are added to all JSON views served by this application.
JSON_CONTEXT_ACTIONS = {
    '@vocab': 'http://www.w3.org/ns/odrl/2/',
    'label': 'http://www.w3.org/2000/01/rdf-schema#label',
    'definition': 'http://www.w3.org/2004/02/skos/core#definition',
    'containedItemClass': 'http://purl.org/linked-data/registry#containedItemClass',
    'comment': 'http://www.w3.org/2000/01/rdf-schema#comment',
    'register': 'http://purl.org/linked-data/registry#register'
}
JSON_CONTEXT_POLICIES = {
    '@vocab': 'http://www.w3.org/ns/odrl/2/',
    'label': 'http://www.w3.org/2000/01/rdf-schema#label',
    'created': 'http://purl.org/dc/terms/created',
    'comment': 'http://www.w3.org/2000/01/rdf-schema#comment',
    'sameAs': 'http://www.w3.org/2002/07/owl#sameAs',
    'register': 'http://purl.org/linked-data/registry#register',
    'containedItemClass': 'http://purl.org/linked-data/registry#containedItemClass',
    'hasVersion': 'http://purl.org/dc/terms/hasVersion',
    'language': 'http://purl.org/dc/terms/language',
    'legalCode': 'http://creativecommons.org/ns#legalcode',
    'jurisdiction': 'http://creativecommons.org/ns#jurisdiction',
    'seeAlso': 'http://www.w3.org/2000/01/rdf-schema#seeAlso',
    'creator': 'http://purl.org/dc/terms/creator',
    'logo': 'http://xmlns.com/foaf/0.1/logo',
    'status': 'http://www.w3.org/ns/adms#status'
}
JSON_CONTEXT_PARTIES = {
    '@vocab': 'http://www.w3.org/ns/odrl/2/',
    'label': 'http://www.w3.org/2000/01/rdf-schema#label',
    'comment': 'http://www.w3.org/2000/01/rdf-schema#comment',
    'register': 'http://purl.org/linked-data/registry#register',
    'containedItemClass': 'http://purl.org/linked-data/registry#containedItemClass',
}

routes = Blueprint('controller', __name__)


@routes.before_request
def csrf_protect():
    # For all POST methods, verify that the CSRF token is correct
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


@routes.route('/')
def home():
    return render_template('page_home.html')


@routes.route('/about')
def about():
    return render_template('about.html')


@routes.route('/contact_submit', methods=['POST'])
def contact_submit():
    # Sends an email via mailjet with the contents of the contact form submission
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    if conf.MAILJET_SECRETS and conf.MAILJET_EMAIL_RECEIVERS and conf.MAILJET_EMAIL_SENDER:
        email_body = 'Name: {name}\nEmail: {email}\n\n{message}'.format(name=name, email=email, message=message)
        data = {
            'Messages': [{
                'From': {'Email': conf.MAILJET_EMAIL_SENDER, 'Name': 'Licence Catalogue Contact Form'},
                'To': [{'Email': email, 'Name': ''} for email in conf.MAILJET_EMAIL_RECEIVERS],
                'Subject': '[Licence Catalogue Contact Form] Enquiry from ' + email,
                'TextPart': email_body
            }]
        }
        requests.post(
            conf.MAILJET_SECRETS['API_ENDPOINT'],
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            auth=(conf.MAILJET_SECRETS['MJ_APIKEY_PUBLIC'], conf.MAILJET_SECRETS['MJ_APIKEY_PRIVATE'])
        )
        return redirect(url_for('controller.about'))
    else:
        flash(('Message not sent', 'Contact form is currently disabled'))
        return redirect(url_for('controller.about'))


@routes.route('/_search_results')
def search_results():
    # For AJAX requests searching through licences. Filters through licences according to the rules supplied and returns
    # a maximum of 10 licences.
    rules = json.loads(request.args.get('rules'))
    results = functions.filter_policies(rules)
    return jsonify(results=results)


@routes.route('/licence/index.json')
def view_licence_list_json():
    # Redirect for alternate URL for JSON view
    redirect_url = url_for('controller.licence_routes', _format='application/json')
    uri = request.values.get('uri')
    if uri is not None:
        redirect_url += '&uri=' + uri
    return redirect(redirect_url)


@routes.route('/licence/')
@routes.route('/licence/<licence_id>')
def licence_routes(licence_id=None):
    """
    All routes for licences. If a licence URI is specified in a GET variable or if the licence ID is specified in the
    URL, displays the relevant licence.
    Otherwise, shows the 'Find A Licence' page.
    """
    licence_uri = request.values.get('uri')
    if not licence_uri and licence_id:
        licence_uri = conf.BASE_URI + 'licence/' + licence_id
    if licence_uri is None:
        return view_licence_list()
    else:
        return view_licence(licence_uri)


def view_licence_list():
    """
    'Find a Licence' page. Displays up to ten licences initially, with no filter applied. User can update the filter
    and the page updates accordingly via the search_results() route.
    Also available as JSON, JSON-LD and Turtle/RDF. These views return all licences, no search is applied.
    """
    licences = [db_access.get_policy(policy_uri) for policy_uri in db_access.get_all_policies()]
    actions = db_access.get_all_actions()
    for action in actions:
        action.update({'LINK': url_for('controller.action_register', uri=action['URI'])})

    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return functions.get_policies_json(licences)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        policies_rdf = functions.get_policies_rdf(licences).serialize(format='turtle')
        return Response(policies_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_policies_rdf(licences).serialize(format='json-ld', context=JSON_CONTEXT_POLICIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        licences = functions.filter_policies([])
        return render_template(
            'licence_search.html',
            licences=licences,
            actions=actions,
            permalink=conf.PERMALINK_BASE + 'licence/',
            rdf_link=url_for('controller.licence_routes', _format='text/turtle'),
            json_link=url_for('controller.licence_routes', _format='application/json'),
            json_ld_link=url_for('controller.licence_routes', _format='application/ld+json'),
            search_url=url_for('controller.search_results')
        )


def view_licence(policy_uri):
    """
    Displays information about a licence, including its attributes and rules (which are sorted into permissions, duties,
    and prohibitions before display).
    Also available as JSON, JSON-LD and Turtle/RDF.
    """
    try:
        policy = db_access.get_policy(policy_uri)
    except ValueError:
        abort(404)
        return
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    rules = [db_access.get_rule(rule_uri) for rule_uri in policy['RULES']]
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return get_policy_json(policy, rules)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        policy_rdf = functions.get_policy_rdf(policy, rules).serialize(format='turtle')
        return Response(policy_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_policy_rdf(policy, rules).serialize(format='json-ld', context=JSON_CONTEXT_POLICIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        permissions = []
        duties = []
        prohibitions = []
        for rule in rules:
            rule['ASSIGNORS'] = [db_access.get_party(assignor) for assignor in rule['ASSIGNORS']]
            rule['ASSIGNEES'] = [db_access.get_party(assignee) for assignee in rule['ASSIGNEES']]
            if rule['LABEL'] is None:
                rule['LABEL'] = rule['URI']
            if rule['TYPE_LABEL'] == 'Permission':
                permissions.append(rule)
            elif rule['TYPE_LABEL'] == 'Duty':
                duties.append(rule)
            elif rule['TYPE_LABEL'] == 'Prohibition':
                prohibitions.append(rule)
        return render_template(
            'view_licence.html',
            permalink=conf.PERMALINK_BASE + 'licence/?uri=' + policy_uri,
            rdf_link=url_for('controller.licence_routes', _format='text/turtle', uri=policy_uri),
            json_link=url_for('controller.licence_routes', _format='application/json', uri=policy_uri),
            json_ld_link=url_for('controller.licence_routes', _format='application/ld+json', uri=policy_uri),
            licence=policy,
            permissions=permissions,
            duties=duties,
            prohibitions=prohibitions
        )


@routes.route('/action/index.json')
def view_action_list_json():
    # Redirect for alternate URL for JSON view
    return redirect('/action/?_format=application/json')


@routes.route('/action/')
def action_register():
    """
    Displays all actions in alphabetical order and grouped into their first letter.
    Specific actions in this register are usually pointed to via element ID
    i.e. licences.com/action/#http://www.w3.org/ns/odrl/2/read
    Also available as JSON, JSON-LD and Turtle/RDF.
    """
    action_uri = request.values.get('uri')
    if action_uri:
        return redirect(url_for('controller.action_register') + '#' + action_uri)
    actions = db_access.get_all_actions()
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return functions.get_actions_json(actions)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        actions_rdf = functions.get_actions_rdf(actions).serialize(format='turtle')
        return Response(actions_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_actions_rdf(actions).serialize(format='json-ld', context=JSON_CONTEXT_ACTIONS)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        action_groups = {}
        for action in actions:
            if not action['LABEL']:
                action['LABEL'] = action['URI']
            first_char = action['LABEL'][0].upper()
            licences_using_action = db_access.get_policies_using_action(action['URI'])
            action['LICENCES'] = sorted(licences_using_action, key=lambda x: x['LABEL'].lower())
            if first_char in action_groups:
                action_groups[first_char].append(action)
            else:
                action_groups[first_char] = [action]
        for group in action_groups:
            action_groups[group].sort(key=lambda x: x['LABEL'].lower())
        return render_template(
            'action_register.html',
            action_groups=action_groups,
            permalink=conf.PERMALINK_BASE + 'action/',
            rdf_link=url_for('controller.action_register', _format='text/turtle'),
            json_link=url_for('controller.action_register', _format='application/json'),
            json_ld_link=url_for('controller.action_register', _format='application/ld+json')
        )


@routes.route('/logout')
def logout():
    """
    Log the user out and redirect them to the page they're currently on.
    """
    logout_user()
    next = request.args.get('next')
    flash('You have been logged out.', 'alert alert-success')
    return redirect(next or url_for('controller.home'))


@routes.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET request to this endpoint responds with the login page. POST requests verify if the credentials entered
    are valid. If an authenticated (logged in) user requests this endpoint, they will simply be redirected to
    the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('controller.home'))

    username = request.form.get('username')
    password = request.form.get('password')
    next = request.args.get('next')

    if request.method == 'POST':
        if username == conf.USERNAME and password == conf.PASSWORD:
            login_user(User(conf.USERNAME))
            next = next if next else request.url
            flash('You are logged in', 'alert alert-success')
            return redirect(next or url_for('controller.home'))
        else:
            flash('Invalid username or password', 'alert alert-danger')
            return redirect(url_for('controller.login', next=next))

    return render_template('login.html', next=next)


@routes.route('/licence/create')
def create_licence_form():
    """
    'Create a Licence' page. Consists of three steps:
    1. User builds the rules they want in their licence, which might include actions, assignors and assignees.
    2. The page suggests some similar licences to the user in case that licence already exists
    3. The user enters other information about the licence such as its name, description, etc.

    Assignors and assignees are selected from a list of permitted 'parties', which consists of a list pulled from
    http://catalogue.linked.data.gov.au/org/json combined with the parties that are already in the database.
    """
    if not current_user.is_authenticated: # Unauthenticated users will be redirected to the login page.
        return redirect(url_for('controller.login', next=request.url))
    actions = db_access.get_all_actions()
    parties = db_access.get_all_parties()
    try:
        external_parties = json.loads(requests.get('http://catalogue.linked.data.gov.au/org/json').text)
        for external_party in external_parties:
            if not any(external_party['view_taxonomy_term'] == party['URI'] for party in parties):
                parties.append({
                    'URI': external_party['view_taxonomy_term'],
                    'LABEL': external_party['name'],
                    'COMMENT': external_party['description__value']
                })
    except requests.ConnectionError:
        pass
    actions.sort(key=lambda x: (x['LABEL'] is None, x['LABEL']))
    parties.sort(key=lambda x: (x['LABEL'] is None, x['LABEL']))
    for action in actions:
        action['LINK'] = url_for('controller.action_register', uri=action['URI'])
    for party in parties:
        party['LINK'] = url_for('controller.party_register', uri=party['URI'])
        if not party['LABEL']:
            party['LABEL'] = party['URI']
    return render_template('create_licence.html', actions=actions, parties=parties,
                           search_url=url_for('controller.search_results'))


@routes.route('/licence/create', methods=['POST'])
def create_licence():
    """
    Creates a new licence.
    At this time all new licences have their type automatically set, and their status set to 'submitted'.
    All things in the form submission except the CSRF token and the Rules (which are popped out) are assumed to be
    policy attributes.
    If successful, redirects to the new licence.
    If not, redirects back to the form and flashes an error message at top of page.
    """
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted'
    }
    attributes.update(request.form.items())
    attributes.pop('_csrf_token', None)
    uri = conf.BASE_URI + str(uuid4())
    rules = json.loads(attributes.pop('rules'))
    for rule in rules:
        rule['ACTIONS'] = [action['URI'] for action in rule['ACTIONS']]
    try:
        functions.create_policy(uri, attributes, rules)
    except ValueError as error:
        flash(error.args, category='error')
        return redirect(url_for('controller.create_licence_form'))
    return redirect(url_for('controller.licence_routes', uri=uri))


@routes.route('/party/index.json')
def view_party_list_json():
    # Redirect for alternate URL for JSON view
    return redirect('/party/?_format=application/json')


@routes.route('/party/')
def party_register():
    """
    Displays all parties in alphabetical order and grouped into their first letter.
    Specific parties in this register are usually pointed to via element ID
    i.e. licences.com/parties/#http://test.linked.data.gov.au/board/B-0068
    Also available as JSON, JSON-LD and Turtle/RDF.
    """
    party_uri = request.values.get('uri')
    if party_uri:
        return redirect(url_for('controller.party_register') + '#' + party_uri)
    parties = db_access.get_all_parties()
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return functions.get_parties_json(parties)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        parties_rdf = functions.get_parties_rdf(parties).serialize(format='turtle')
        return Response(parties_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_parties_rdf(parties).serialize(format='json-ld', context=JSON_CONTEXT_PARTIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        party_groups = {}
        for party in parties:
            if not party['LABEL']:
                party['LABEL'] = party['URI']
            rules_involving_party = db_access.get_rules_for_party(party['URI'])
            licences_involving_party = []
            for rule_involving_party in rules_involving_party:
                licences_involving_party.extend(db_access.get_policies_for_rule(rule_involving_party))
            party['LICENCES'] = sorted(licences_involving_party, key=lambda x: x['LABEL'].lower())
            first_char = party['LABEL'][0].upper()
            if first_char in party_groups:
                party_groups[first_char].append(party)
            else:
                party_groups[first_char] = [party]
        for group in party_groups:
            party_groups[group].sort(key=lambda x: x['LABEL'].lower())
        return render_template(
            'party_register.html',
            party_groups=party_groups,
            permalink=conf.PERMALINK_BASE + 'party/',
            rdf_link=url_for('controller.party_register', _format='text/turtle'),
            json_link=url_for('controller.party_register', _format='application/json'),
            json_ld_link=url_for('controller.party_register', _format='application/ld+json')
        )


@routes.route('/object')
def view_object():
    # Route for viewing something by URI, regardless of whether it is a licence, action, party, etc.
    object_uri = request.values.get('uri')
    if object_uri is None:
        flash(('Object not found', 'Please supply a URI to view an object.'), category='error')
        return redirect(url_for('controller.home'))
    else:
        if db_access.policy_exists(object_uri):
            return redirect(url_for('controller.licence_routes', uri=object_uri))
        if db_access.action_exists(object_uri):
            return redirect(url_for('controller.action_register', uri=object_uri))
        if db_access.party_exists(object_uri):
            return redirect(url_for('controller.party_register', uri=object_uri))
        abort(404)
