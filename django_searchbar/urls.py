from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^', 'django_searchbar.views.homepage'),
)
