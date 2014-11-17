from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from workflow import urls as workflowurls


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from workflow import views
from qpcr import urls as qpcr_urls
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^crunch$', RedirectView.as_view(url="/crunch/accounts/login/")),
    url(r'^crunch/$', RedirectView.as_view(url="/crunch/accounts/login/")),

    url(r'^$', RedirectView.as_view(url="/crunch/accounts/login/")),

    # Examples:
    # url(r'^$', 'chembiocrunch.views.home', name='home'),
    # url(r'^chembiocrunch/', include('chembiocrunch.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^crunch/admin/', include(admin.site.urls)),

    url(r'^crunch/my_workflows/', include(workflowurls)),

    url(r'^crunch/accounts/login/', views.Login.as_view(), name="login" ),
    url(r'^crunch/accounts/logout/', views.Logout.as_view(), name="logout" ),
    url(r'^crunch/logged_out/', views.Login.as_view(logout=True), name="loggedout" ),

    url(r'^crunch/qpcr/', include(qpcr_urls)),


)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#                             url(r'^__debug__/', include(debug_toolbar.urls)),
#                             )

if "django_webauth" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            url(r'^crunch/webauth/', include('django_webauth.urls', 'webauth')),
                            )

#if "ic50" in settings.INSTALLED_APPS:
from ic50 import urls as ic50urls
urlpatterns += patterns('',
    url(r'^crunch/ic50_builder/', include(ic50urls) ),
)
