import sys

from clint.textui import colored, prompt, puts
from django.core.management.base import BaseCommand as DjangoBaseCommand

from hoop.util import env
from hoop.util.dates import encode_date

from .validators import date_validator, uuid_validator


class BaseCommand(DjangoBaseCommand):
    title = None

    def handle(self, *args, **options):
        if self.title:
            puts()
            puts(colored.yellow(self.title))
            puts(colored.yellow('================================================================'))
            puts()

        try:
            self.run()
        except KeyboardInterrupt:
            puts()
            self.info('Exiting...')

            sys.exit(0)

    def run(self):
        raise NotImplemented

    def get_date(self, label, default=None):
        if default:
            default = encode_date(default)

        return prompt.query(label, default=default, validators=[date_validator])

    def get_uuid(self, label):
        return prompt.query(label, validators=[uuid_validator])

    def subtitle(self, text):
        puts()
        puts(colored.yellow(text))
        puts(colored.yellow('----------------------------------------------------------------'))
        puts()

    def confirmation(self, rows):
        self.subtitle('Confirm Details')

        for row in rows:
            if row:
                puts(colored.yellow(row[0] + ': ') + row[1])
            else:
                puts()

        puts()

        # On production we want to default
        # to aborting the command
        if env.name() == 'prd':
            abort = prompt.yn('Abort?')
        else:
            abort = not prompt.yn('Proceed?')

        if abort:
            self.info('Exiting...')

            sys.exit(0)

    def success(self, text, abort=False):
        puts(colored.green(text))
        puts()

        if abort:
            sys.exit(0)

    def info(self, text, abort=False):
        puts(colored.yellow(text))
        puts()

        if abort:
            sys.exit(0)

    def error(self, text, abort=False):
        puts(colored.red(text))
        puts()

        if abort:
            sys.exit(1)
