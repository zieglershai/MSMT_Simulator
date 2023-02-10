from Policy.policy import Policy
from Clock.clock import Clock
from Thread.thread import Thread


class TwoLevel(Policy):
    def __init__(self, num_l_one_threads: int, num_l_two_threads: int, clock: Clock, soe_penalty: int):
        super().__init__(clock)
        self.soe_penalty = soe_penalty
        self.num_l_one_threads = num_l_one_threads
        self.num_l_two_threads = num_l_two_threads
        self.l_one_list = [i for i in range(num_l_one_threads)]
        self.l_two_list = [i+num_l_one_threads for i in range(num_l_two_threads)]

    def get_threads_by_priority(self, threads=None):
        """
        return a list with one thread index to run
        :return:
        """

        for i, thread_index in enumerate(self.l_one_list):
            if not threads[thread_index].ready():
                self.l_two_list.append(self.l_one_list.pop(i))
                for j, thread_jindex in enumerate(self.l_two_list):
                    if threads[thread_jindex].ready():
                        self.l_one_list.append(self.l_two_list.pop(j))
                        threads[thread_jindex].sleep_on_soe_enter_l_one(self.soe_penalty)
                        break
        for i in range(self.num_l_one_threads - len(self.l_one_list)):
            for j, thread_jindex in enumerate(self.l_two_list):
                if threads[thread_jindex].ready():
                    self.l_one_list.append(self.l_two_list.pop(j))
                    threads[thread_jindex].sleep_on_soe_enter_l_one(self.soe_penalty)
                    break

        return self.l_one_list
