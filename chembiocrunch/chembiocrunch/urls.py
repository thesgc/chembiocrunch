from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from workflow import urls as workflowurls
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from workflow.views import login

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url="accounts/login/")),

    # Examples:
    # url(r'^$', 'chembiocrunch.views.home', name='home'),
    # url(r'^chembiocrunch/', include('chembiocrunch.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^my_workflows/', include(workflowurls)),

    url(r'^accounts/login/', login.Login.as_view(), name="login" ),
    url(r'^accounts/logout/', login.Logout.as_view(), name="logout" ),
    url(r'^logged_out/', login.Login.as_view(logout=True), name="loggedout" ),


)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )

if "django_webauth" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            url(r'^webauth/', include('django_webauth.urls', 'webauth')),
                            )