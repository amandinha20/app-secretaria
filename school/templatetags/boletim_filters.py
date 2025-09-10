from django import template

def dict_get(d, key):
    return d.get(key)

register = template.Library()
register.filter('dict_get', dict_get)
