from django import template
from django.template import TemplateSyntaxError

from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from urllib2 import urlopen

from django.core.cache import cache

register = template.Library()


class RemoteInclude(template.Node):

    STALE_REFRESH = 1
    STALE_CREATED = 2
    ERROR_LOADING = _('Unable to retrieve remote file')

    def __init__(self, url, should_cache=False, timeout=3600):
        self.url = url
        self.should_cache = should_cache
        self.timeout = timeout

    def get_url(self):
        output = ''
        try:
            rf = urlopen(self.url, timeout=10)
            output = rf.read()
            rf.close()
        except IOError:
            output = self.ERROR_LOADING
        return output

    def render(self, context):
        output = ''

        if self.should_cache:
            cache_key = self.url + 'cg_ri'
            output = cache.get(cache_key)
            if output == None or output == self.ERROR_LOADING:
                #print('retrieving from url')
                output = self.get_url()
                cache.set(cache_key, output, self.timeout)
            else:
                #print('retrieving from cache')
                output = cache.get(cache_key)
        else:
            output = self.get_url()
        return output


# Simple Remote Include, doesn't do any caching 
# Form: {% sri url %}
def sri(parser, token):

    bits = list(token.split_contents())

    if len(bits) != 2:
        raise TemplateSyntaxError, _("%r takes one argument" % bits[0])
    
    return RemoteInclude(bits[1])
sri = register.tag(sri)


# Caching remote include - puts remote URL into a cache that
# expires in the specified amount of time.
# Form: {% cri url timeout_in_seconds %}
def cri(parser, token):

    bits = list(token.split_contents())

    if len(bits) != 3:
        raise TemplateSyntaxError, _("%r takes two arguments.  The URL and the amount of time to cache the contents of the URL" % bits[0])

    timeout = 30
    try:
        timeout = int(bits[2])
    except ValueError:
        raise TemplateSyntaxError, _("The cri tag requires a valid integer in seconds for the cache timeout value: \'%s\' given" % bits[2])

    return RemoteInclude(url=bits[1], timeout=int(bits[2]), should_cache=True)
cri = register.tag(cri)