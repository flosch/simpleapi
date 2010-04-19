from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^api/', include('api.urls')),
	(r'^ajax/', include('ajax_client.urls')),
)
