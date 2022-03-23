from django.db import DEFAULT_DB_ALIAS
from django.db.transaction import Atomic, get_connection


class LockedAtomicTransaction(Atomic):
    """
    https://stackoverflow.com/questions/19686204/django-orm-and-locking-table#41831049

    Does a atomic transaction, but also locks the entire table for any transactions, for the duration of this
    transaction. Although this is the only way to avoid concurrency issues in certain situations, it should be used with
    caution, since it has impacts on performance, for obvious reasons...
    """

    def __init__(self, model, using=None, savepoint=None):
        if using is None:
            using = DEFAULT_DB_ALIAS
        super().__init__(using, savepoint)
        self.model = model

    def __enter__(self):
        super(LockedAtomicTransaction, self).__enter__()

        cursor = None
        try:
            cursor = get_connection(self.using).cursor()
            cursor.execute('UNLOCK TABLES')
            cursor.execute('LOCK TABLE {db_table_name} READ'.format(db_table_name=self.model._meta.db_table))
        finally:
            cursor.execute('UNLOCK TABLES')
            cursor.close()
