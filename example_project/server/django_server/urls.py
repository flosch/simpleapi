from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/ajax/'}),
	(r'^api/', include('api.urls')),
	(r'^ajax/', include('ajax_client.urls')),
)
