
from Policy.policy import Policy
from Clock.clock import Clock
from Thread.thread import Thread


class PreFetchTwoLevel(Policy):
    def __init__(self, num_l_one_threads: int, num_l_two_threads: int, num_prefetch_threads: int, clock: Clock,
                 soe_penalty: int, pre_fetch_cycles: int):
        super().__init__(clock)
        self.soe_penalty = soe_penalty
        self.pre_fetch_cycles = pre_fetch_cycles
        self.num_l_one_threads = num_l_one_threads
        self.num_l_two_threads = num_l_two_threads
        self.num_prefetch_threads = num_prefetch_threads
        self.prefetch_list = []
        self.l_one_list = [i for i in range(num_l_one_threads)]
        self.l_two_list = [i+num_l_one_threads for i in range(num_l_two_threads)]
        self.prefetch_countdown = [0 for _ in range(num_prefetch_threads)]

    def get_threads_by_priority(self, threads=None):
        """
        return a list with one thread index to run
        :return:
        """
        for i, thread_index in enumerate(self.l_two_list):
            if len(self.prefetch_list) == self.num_prefetch_threads:
                break
            if threads[thread_index].prefetch(self.pre_fetch_cycles) and not threads[thread_index].check_if_done():
                did_prefetch = self.prefetch()
                if did_prefetch:
                    self.prefetch_list.append(self.l_two_list.pop(i))

        for i, thread_index in enumerate(self.l_one_list):
            if not threads[thread_index].ready() or threads[thread_index].check_if_done():
                self.l_two_list.append(self.l_one_list.pop(i))
                added_new_thread = False
                for j, thread_jindex in enumerate(self.prefetch_list):
                    self.l_one_list.append(self.prefetch_list.pop(j))
                    threads[thread_jindex].sleep_on_soe_enter_l_one(self.soe_penalty - self.pre_fetch_cycles)
                    added_new_thread = True
                    break
                if not added_new_thread:
                    for j, thread_jindex in enumerate(self.l_two_list):
                        if threads[thread_jindex].ready() and not threads[thread_jindex].check_if_done():
                            self.l_one_list.append(self.l_two_list.pop(j))
                            threads[thread_jindex].sleep_on_soe_enter_l_one(self.soe_penalty)
                            break

        for i in range(self.num_l_one_threads - len(self.l_one_list)):
            for j, thread_jindex in enumerate(self.prefetch_list):
                self.l_one_list.append(self.prefetch_list.pop(j))
                threads[thread_jindex].sleep_on_soe_enter_l_one(self.soe_penalty - self.pre_fetch_cycles)
                break

        for i in range(self.num_l_one_threads - len(self.l_one_list)):
            for j, thread_jindex in enumerate(self.l_two_list):
                if threads[thread_jindex].ready() and not threads[thread_jindex].check_if_done():
                    self.l_one_list.append(self.l_two_list.pop(j))
                    threads[thread_jindex].sleep_on_soe_enter_l_one(self.soe_penalty)
                    break

        return self.l_one_list

    def prefetch(self):
        if 0 in self.prefetch_countdown:
            self.prefetch_countdown.remove(0)
            self.prefetch_countdown.append(self.pre_fetch_cycles)
            return True
        return False

    def step(self):
        self.prefetch_countdown = [i - 1 if i > 0 else i for i in self.prefetch_countdown]
