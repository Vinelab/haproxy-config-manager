from django.conf.urls import url, include, patterns
from rest_framework.urlpatterns import format_suffix_patterns
import ProxyView

urlpatterns = [
    url(r'^add/$', ProxyView.add),
    url(r'^remove/$', ProxyView.remove),
]

urlpatterns = format_suffix_patterns(urlpatterns)