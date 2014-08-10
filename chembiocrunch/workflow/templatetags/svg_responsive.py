from django import template

register = template.Library()
import re

PATTERN = re.compile('width="\d+pt"')
H = re.compile('height="\d+pt"')

def add_responsive_tags(svg):
    
    svg = PATTERN.sub('width="100%" preserveAspectRatio="xMinYMin meet" ',svg)
    #svg = H.sub('height="100%"', svg)
    return svg


def add_responsive_height(svg):
    
    svg = PATTERN.sub('width="90%" preserveAspectRatio="xMinYMax" ',svg)
    svg = H.sub('height="90%"', svg)
    return svg

register.filter('add_responsive_tags', add_responsive_tags)
register.filter('add_responsive_height', add_responsive_tags)