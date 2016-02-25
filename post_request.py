from flask import Flask, jsonify, make_response, request, current_app
import os
app = Flask(__name__)

IS_PRODUCTION = (os.getenv('PYTHON_ENV', False) == "production")

if not IS_PRODUCTION:
    app.debug = True

import argparse
import json
import pprint
import sys
import urllib
import urllib2
import oauth2
import requests
from lxml import html
from bs4 import BeautifulSoup

# Util for X-Origin
from datetime import timedelta
from functools import update_wrapper

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 2
PHOTO_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

PHOTO_BOX_PATH = 'http://www.yelp.com/biz_photos/'

CREDENTIAL_FILE = 'credentials.json'

def make_request(credentials, host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(str(credentials['CONSUMER_KEY']), str(credentials['CONSUMER_SECRET']))

    oauth_request = oauth2.Request(
        method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': str(credentials['TOKEN']),
            'oauth_consumer_key': str(credentials['CONSUMER_KEY'])

        }
    )
    token = oauth2.Token(str(credentials['TOKEN']), str(credentials['TOKEN_SECRET']))
    oauth_request.sign_request(
        oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()
    return response

def search(credentials, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return make_request(credentials, API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(credentials, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return make_request(credentials, API_HOST, business_path)

def get_photo_box_images(url_prefix, business_id, PHOTO_LIMIT):
    #TODO: change filter to generically get data from parameter
    # food,inside,outside,drink,menu
    PIC_FILTER = '?tab=food'

    photo_box_url = ''.join([url_prefix, business_id, PIC_FILTER])
    print photo_box_url, "pic box"
    page = requests.get(photo_box_url)
    if not page:
        print (u'No photo box page for {0} found.'.format(business_id))
        return

    soup = BeautifulSoup(page.text, 'html.parser')
    # s = soup.find_all("img", class_="photo-box-img")
    photo_sources = soup.findAll("img",{"class":"photo-box-img", "src":True, "height":"226"})
    if not photo_sources:
        print (u'No photo box sources for {0} found.'.format(business_id))
        return

    photo_urls = []
    for i, photo_source in enumerate(photo_sources):
        if i < PHOTO_LIMIT:
            photo_urls.append(''.join(['http:', photo_source['src']]))
    return photo_urls

def query_api(credentials, term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    businesses = None
    search_list = search(credentials, term, location)
    if not search_list:
        print (u'Business list for {0} in {1} not found.'.format(term, location))
        return

    businesses = search_list.get('businesses')
    if not businesses:
        print (u'No businesses for {0} in {1} found.'.format(term, location))
        return

    data = {}
    data['status'] = 'success'
    records = []
    # Get business information and photo box images for each businesses
    for rank in range(min(SEARCH_LIMIT, len(businesses))):

        # Get business id
        business_id = businesses[rank]['id']

        # print(business_id)
        print ('Querying business info for "{0}" ...'.format(business_id))

        if business_id:
            business = get_business(credentials, business_id)

            # Get images in photo box for current business
            photo_urls = get_photo_box_images(PHOTO_BOX_PATH, business_id, PHOTO_LIMIT)
            if photo_urls:
                record = {}
                record['business_id'] = business['id']

                record['business_name'] = business['name']

                business_location = business['location']
                record['display_address'] = business_location['display_address']

                record['coordinate'] = business_location['coordinate']

                record['business_url'] = business['url']

                record['rating_img_url'] = business['rating_img_url']

                record['photo_urls'] = photo_urls

                records.append(record)

    data['businesses'] = records

    return json.dumps(data)

def get_credentials(credential_file_path):
    error_code = 200
    credentials = {}

    try:
        with open(credential_file_path) as data_file:
            credentials = json.load(data_file)
        f.close()
    except IOError:
        error_code = 400
        sys.exit("Could not read file:", credential_file_path)
    finally:
        return credentials, error_code

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route("/", methods=["GET"])
@crossdomain(origin='*')
def main():
    with open('credentials.json') as data_file:
        credentials = json.load(data_file)

    json_data, error_code = None, None

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--term', dest='term', default=request.args.get("term", None),
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=request.args.get("location", None), type=str,
                        help='Search location (default: %(default)s)')
    input_values = parser.parse_args()

    try:
        json_data = query_api(credentials, input_values.term, input_values.location)

    except urllib2.HTTPError as error:
        error_code = error.code
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))
    finally:
        return json_data, error_code

if __name__ == "__main__":
    app.run()
    # main()
