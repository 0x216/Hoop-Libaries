class ServiceError(Exception):
    def __init__(self, service, task, message=None):
        if message:
            super(ServiceError, self).__init__('Service Error (%s/%s): %s' % (service, task, message))
        else:
            super(ServiceError, self).__init__('Service Error (%s/%s)' % (service, task))


class TimeoutError(Exception):
    def __init__(self, service, task):
        super(TimeoutError, self).__init__('Service Timeout (%s/%s)' % (service, task))


class NoSuchTaskError(Exception):
    def __init__(self, name):
        super(NoSuchTaskError, self).__init__('No such HulaAsyncProxy task was initialised (%s)' % (name))
