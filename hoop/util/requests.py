def user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def from_internal_ip(request):
    if user_ip(request) in ['188.39.83.162', '127.0.0.1']:
        return True
    return False
