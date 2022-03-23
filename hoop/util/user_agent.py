def is_mobile(request):
    user_agent = request.META['HTTP_USER_AGENT'].lower()
    for mobile_agent in ['android', 'iphone']:
        if mobile_agent in user_agent:
            return True
    return False
