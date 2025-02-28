from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_field_pref(form, alimento_id):
    return form[f'pref_{alimento_id}']

@register.filter
def get_field_rest(form, alimento_id):
    return form[f'rest_{alimento_id}'] 