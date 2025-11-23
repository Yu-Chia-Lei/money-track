from django import template

register = template.Library()

@register.filter
def lookup(list_of_social_accounts, provider_name):
    """
    過濾器：從社交帳號列表中找出指定 provider 的帳號。
    用法: {% with google_account=accounts|lookup:"google" %}
    """
    # list_of_social_accounts 是一個 SocialAccount QuerySet
    # provider_name 例如 'google', 'facebook'
    try:
        return list_of_social_accounts.filter(provider=provider_name)
    except AttributeError:
        return []
    #