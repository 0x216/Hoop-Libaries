from .env import name as env_name
from hoop.hula import Hula


def send_email(template_name, email, name, merge_vars, async=True, merge_language='handlebars'):
    if env_name() == 'prd' or '@hoop.co.uk' in email:
        data = {'email': email, 'template_name': template_name, 'name': name, 'merge_vars': merge_vars}

        Hula().execute('emails', 'send_email', data=data, version='v1')
