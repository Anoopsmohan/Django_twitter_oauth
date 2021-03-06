import oauth
import urllib

from django.conf import settings


signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

SERVER = getattr(settings, 'OAUTH_SERVER', 'twitter.com')
REQUEST_TOKEN_URL = getattr(settings, 'OAUTH_REQUEST_TOKEN_URL', 'https://%s/oauth/request_token' % SERVER)
ACCESS_TOKEN_URL = getattr(settings, 'OAUTH_ACCESS_TOKEN_URL', 'https://%s/oauth/access_token' % SERVER)
AUTHORIZATION_URL = getattr(settings, 'OAUTH_AUTHORIZATION_URL', 'http://%s/oauth/authorize' % SERVER)

CONSUMER_KEY = getattr(settings, 'CONSUMER_KEY', 'jC93SqIa1dP54mKj4KVXw')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET', 'jFn1dcZA22descDumCiEmNW4uX5la79tJEMMkDW69O8')

# We use this URL to check if Twitters oAuth worked
TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'
TWITTER_FRIENDS = 'https://twitter.com/statuses/friends.json'
TWITTER_TWEETS = 'https://twitter.com/statuses/home_timeline.json'

def request_oauth_resource(consumer, url, access_token, parameters=None, signature_method=signature_method, http_method="GET"):
    """
    usage: request_oauth_resource( consumer, '/url/', your_access_token, parameters=dict() )
    Returns a OAuthRequest object
    """
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=access_token, http_method=http_method, http_url=url, parameters=parameters,
    )
    oauth_request.sign_request(signature_method, consumer, access_token)
    return oauth_request


def fetch_response(oauth_request, connection):
    url = oauth_request.to_url()
    connection.request(oauth_request.http_method, url)
    response = connection.getresponse()
    s = response.read()
    return s

def get_unauthorised_request_token(consumer, connection, signature_method=signature_method):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, http_url=REQUEST_TOKEN_URL
    )
    oauth_request.sign_request(signature_method, consumer, None)
    resp = fetch_response(oauth_request, connection)
    token = oauth.OAuthToken.from_string(resp)
    return token


def get_authorisation_url(consumer, token, signature_method=signature_method):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=token, http_url=AUTHORIZATION_URL
    )
    oauth_request.sign_request(signature_method, consumer, token)
    return oauth_request.to_url()

def get_oauth_url(oauth_request):
    url = oauth_request.to_url()
    package = urllib.urlopen(url)
    return package.read()

def exchange_request_token_for_access_token(consumer, request_token, signature_method=signature_method, params={}):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=request_token, http_url=ACCESS_TOKEN_URL, parameters=params
    )
    oauth_request.sign_request(signature_method, consumer, request_token)
    resp = get_oauth_url(oauth_request)
    return oauth.OAuthToken.from_string(resp) 

def is_authenticated(consumer, connection, access_token):
    oauth_request = request_oauth_resource(consumer, TWITTER_CHECK_AUTH, access_token)
    json = fetch_response(oauth_request, connection)
    if 'screen_name' in json:
        return json
    return False

def get_tweets(consumer, connection, access_token):
    """Get tweets on twitter"""
    oauth_request = request_oauth_resource(consumer, TWITTER_TWEETS, access_token)
    json = fetch_response(oauth_request, connection)
    return json
