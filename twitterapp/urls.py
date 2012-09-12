from django.conf.urls.defaults import *

from mytwitter.views import *

urlpatterns = patterns('mytwitter.views',
    url(r'^$', view=main, name='twitter_oauth_main'),
    url(r'^auth/$', view=auth, name='twitter_oauth_auth'),
    url(
        r'^login/authenticated/$', view=return_, name='twitter_oauth_return'    ),
    url(r'^list/$', view=tweets, name='twitter_oauth_tweets'),
    url(r'^clear/$', view=unauth, name='twitter_oauth_unauth'),
)
