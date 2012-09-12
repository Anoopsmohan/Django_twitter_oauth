import oauth, httplib, time, datetime
import simplejson

from django.conf import settings
from django.http import *
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from mytwitter.utils import *

CONSUMER = oauth.OAuthConsumer(
    settings.TWITTER_TOKEN, settings.TWITTER_SECRET
)
CONNECTION = httplib.HTTPSConnection(SERVER)


def main(request):
    """
    Render the home page
    """
    if request.session.has_key('access_token'):
        return HttpResponseRedirect(reverse('twitter_oauth_tweets'))
    else:
        return render_to_response('base.html')

def unauth(request):
    """
    Unauthenticate from twitter
    """
    response = HttpResponseRedirect(reverse('twitter_oauth_main'))
    request.session.clear()
    return response


def auth(request):
    """
    Authenticate with twitter
    """
    token = get_unauthorised_request_token(CONSUMER, CONNECTION)
    auth_url = get_authorisation_url(CONSUMER, token)
    response = HttpResponseRedirect(auth_url)
    request.session['unauthed_token'] = token.to_string()
    return response


def return_(request):
    """
    Call back function
    """
    unauthed_token = request.session.get('unauthed_token', None)
    if not unauthed_token:
        return HttpResponse("No un-authed token cookie")
    token = oauth.OAuthToken.from_string(unauthed_token)
    if token.key != request.GET.get('oauth_token', 'no-token'):
        return HttpResponse("Something went wrong! Tokens do not match")
    verifier = request.GET.get('oauth_verifier')
    access_token = exchange_request_token_for_access_token(
        CONSUMER, token, params={'oauth_verifier':verifier}
    )
    response = HttpResponseRedirect(
        reverse('twitter_oauth_tweets')
    )
    request.session['access_token'] = access_token.to_string()
    return response


def tweets(request):
    """
    Return last 5 tweets
    """
    access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse("You need an access token!")
    token = oauth.OAuthToken.from_string(access_token)
    auth = is_authenticated(CONSUMER, CONNECTION, token)
    if auth:
        creds = simplejson.loads(auth)
	tweets = get_tweets(CONSUMER, CONNECTION, token)
	my_tweets = simplejson.loads(tweets)[:5]
    return render_to_response(
        'list.html', {
            'user': creds,
            'tweets': my_tweets
        }
    )
