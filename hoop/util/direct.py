import json

DIRECT_COOKIE_KEY = 'hoop-do'
DIRECT_COOKIE_MAX_AGE = 30 * 24 * 60 * 60 # 30 Days


def set_direct_org_cookie(org_id, request, response):
    current_do_list = request.COOKIES.get(DIRECT_COOKIE_KEY)

    if current_do_list:
        try:
            org_ids = json.loads(current_do_list)
            if org_id not in org_ids:
                org_ids.append(org_id)
        except (json.JSONDecodeError, AttributeError):
            org_ids = [org_id]
    else:
        org_ids = [org_id]

    domain = request.get_host().split(':')[0]
    response.set_cookie(DIRECT_COOKIE_KEY, json.dumps(org_ids), domain=domain, max_age=DIRECT_COOKIE_MAX_AGE)


def is_direct_mode(request, org_id):
    if org_id is None:
        return False

    direct_orgs_cookie = request.COOKIES.get(DIRECT_COOKIE_KEY)
    if not direct_orgs_cookie:
        return False

    try:
        org_ids = json.loads(direct_orgs_cookie)
    except json.JSONDecodeError:
        return False

    return org_id in org_ids
