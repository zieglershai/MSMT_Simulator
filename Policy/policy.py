from Clock.clock import Clock


class Policy(object):
    def __init__(self, clock: Clock = None):
        """
        the main policy type
        """
        self.clock = clock

    def get_threads_by_priority(self):
        """
        return a list of indexes of threads ordered by priority
        :return:
        """
        pass

    def step(self):
        pass
