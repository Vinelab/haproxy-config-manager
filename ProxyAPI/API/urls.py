from django.conf.urls import url, include, patterns
from rest_framework.urlpatterns import format_suffix_patterns
import ProxyView

urlpatterns = [
    url(r'^add/$', ProxyView.add),
    url(r'^remove/$', ProxyView.remove),
    url(r'^reload/$', ProxyView.reloadproxy),
    url(r'^reload//api/reload/$',ProxyView.reloadproxy),
]

urlpatterns = format_suffix_patterns(urlpatterns)
