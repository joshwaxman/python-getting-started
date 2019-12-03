from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import hello.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^talmud/(\w*).(\w*)', hello.views.talmud, name='talmud'),
    url(r'^talmud_dev/(\w*).(\w*)', hello.views.talmud_dev, name='talmud_dev'),
    url(r'^talmud', hello.views.talmud, name='talmud'),
    url(r'^about', hello.views.about, name='about'),
    url(r'^bio/(.*)', hello.views.bio, name='bio'),
    url(r'^dictionary/clark/(.*)', hello.views.clark, name='clark'),
    url(r'^dictionary/clark', hello.views.clark, name='clark'),
    url(r'^dictionary/klein/(.*)', hello.views.klein, name='klein'),
    url(r'^dictionary/klein', hello.views.klein, name='klein'),
    url(r'^dictionary/bdb/(.*)', hello.views.bdb, name='bdb'),
    url(r'^dictionary/bdb', hello.views.bdb, name='bdb'),
    url(r'^dictionary/distributional/(.*)', hello.views.distributional, name='distributional'),
    url(r'^dictionary/distributional', hello.views.distributional, name='distributional'),
    url(r'^dictionary', hello.views.dictionary, name='dictionary'),
    url(r'^trup/form', hello.views.trup_form, name='trup'),
    url(r'^trup/(.*)', hello.views.trup, name='trup'),
    url(r'^people', hello.views.people, name='people'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^convert/(.*)', hello.views.convert, name='convert'),
    url(r'^blog', hello.views.blog, name='blog'),
    url(r'^full_graph', hello.views.full_graph, name='full_graph'),

    path('admin/', admin.site.urls),
]
