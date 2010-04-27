from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    (r'^api/', include('api.urls')),
)
