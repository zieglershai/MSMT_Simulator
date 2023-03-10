import json
import time

from Execution.execution import Execution
from Thread.thread import Thread
import os
from constants import PolicyType, PolicyTypeError, InstructionType, INSTRUCTION_TYPE, ROW_ID, FINISH_CYCLE, \
    SINGLE_THREAD_STRING, \
    TOTAL_CYCLES_STRING, IPC_STRING, CPI_STRING, UTILIZATION_STRING, TOTAL_TIME_STRING
from Policy.RoundRobbin.roundRobbin import RoundRobbin
from Policy.TwoLevel.twoLevel import TwoLevel
from Policy.PreFetchTwoLevel.preFetchTwoLevel import PreFetchTwoLevel
import pandas as pd
from Clock.clock import Clock


class Scheduler(object):
    def __init__(self, config_file_path: str):
        """
        This is the main class that will run the simulation
        """
        self.config = None
        self.execution_unit = None
        self.threads = []
        self.thread_count = None
        self.policy = None
        self.priority_thread_indexes = []
        self.clock = Clock()
        self.clock.reset()

        self.parse_input(config_file_path)
        self.create_threads()
        self.create_execution_unit()
        self.create_policy()

    def create_policy(self):
        """
        create a policy object with the policy in the configuration
        :return:
        """
        policy_string = self.config["policy"]
        if policy_string == PolicyType.RR.name:
            self.policy = RoundRobbin(self.thread_count, self.config["policy_params"]["quanta"], self.clock)
        elif policy_string == PolicyType.TWOLEVEL.name:
            self.policy = TwoLevel(self.config["policy_params"]["num_l_one_threads"],
                                   self.config["policy_params"]["num_l_two_threads"],
                                   self.clock,
                                   self.config["policy_params"]["soe_penalty"])
        elif policy_string == PolicyType.PREFETCHTWOLEVEL.name:
            self.policy = PreFetchTwoLevel(self.config["policy_params"]["num_l_one_threads"],
                                           self.config["policy_params"]["num_l_two_threads"],
                                           self.config["policy_params"]["prefetch_threads"],
                                           self.clock,
                                           self.config["policy_params"]["soe_penalty"],
                                           self.config["policy_params"]["prefetch_cycles"])
        elif policy_string == PolicyType.PRR.name:
            pass
        else:
            raise PolicyTypeError("requested policy doesn't exist")

    def parse_input(self, config_file_path: str):
        """
        Parse the config:
            set:
                1. window_ooo size
                2. penalties
                3. execution units - number and latency
                4. miss rate
                5. scheduling policy
        :param config_file_path:
        :return:
        """
        with open(config_file_path, "r") as f:
            self.config = json.load(f)

    def create_execution_unit(self):
        self.execution_unit = Execution(alus_units=self.config["alu"]["count"],
                                        fp_alus_units=self.config["fp_alu"]["count"],
                                        ldsts_units=self.config["ldst"]["count"],
                                        branch_units=self.config["branch"]["count"],
                                        alu_time=self.config["alu"]["time"],
                                        br_time=self.config["branch"]["time"],
                                        ldsts_time=self.config["ldst"]["time"],
                                        br_miss_rate=self.config["branch_miss"],
                                        br_penalty=self.config["branch_penalty"],
                                        cache_miss_rate=self.config["cache_miss"],
                                        mem_penalty=self.config["mem_penalty"])

    def create_threads(self):
        """
        after configuration set, create thread objects
        :return:
        """
        trace_folder = os.path.expanduser(self.config["trace_folder_path"])
        priority_threads = list(self.config["priority_thread"])

        counter = 0
        for thread_type in self.config["threads"]:
            for j in range(self.config["threads"][thread_type]):
                trace = os.path.join(trace_folder, thread_type + ".pkl")
                if thread_type in priority_threads:
                    thread = Thread(trace, self.config["priority_window_size"], self.clock)
                    self.threads.append(thread)
                    priority_threads.remove(thread_type)
                    self.priority_thread_indexes.append(counter)
                else:
                    thread = Thread(trace, self.config["window_size"], self.clock)
                    self.threads.append(thread)
                counter += 1
        self.thread_count = counter

    def step(self):
        """
        this function adds a cycle to all the elements of the simulator
        :return:
        """
        self.clock.step()
        self.execution_unit.step()

        # these currently pass
        for thread in self.threads:
            if not thread.check_if_done():
                thread.step()
        self.policy.step()

    def get_threads_by_priority(self):
        """
        This function returns a list of the threads index
        ordered by the current priority to get instructions from
        :return:
        """
        threads_priority_list = self.policy.get_threads_by_priority(self.threads)
        return threads_priority_list

    def check_if_all_threads_are_done(self):
        """
        Checks if all the threads are finished running
        :return:
        """
        return all(map(lambda thread: thread.check_if_done(), self.threads))

    def run(self):
        """
        Main run loop
        :return:
        """
        start = time.time()
        while not self.check_if_all_threads_are_done():
            threads_for_cycle = self.get_threads_by_priority()
            for thread_index in threads_for_cycle:
                instructions = self.get_unexecuted_instruction_window_from_thread(thread_index)
                for i, row in instructions.iterrows():
                    # -1 if not executed
                    num_cycles, cache_miss = self.execute_instruction(row[INSTRUCTION_TYPE])
                    instruction_id = row[ROW_ID]
                    if num_cycles != -1:
                        self.set_instruction_ran_on_thread(thread_index, instruction_id, num_cycles)
                        if cache_miss:  # if there was a miss switch on event is required
                            self.threads[thread_index].set_cache_miss(num_cycles)
                            break
                    else:
                        break
            self.step()
            if self.clock.get_cycle() % 1000 == 0:
                print(f"clock is at cycle {self.clock.get_cycle()}")
                total_inst_so_far = 0
                for i in range(self.thread_count):
                    print(f"thread {i} progress: {self.threads[i].get_progress():.2f}")
                    total_inst_so_far += self.threads[i].instruction
                print(f"IPC: {total_inst_so_far / self.clock.get_cycle():.4f}")
                print(f"CPI: {self.clock.get_cycle() / total_inst_so_far:.4f}")
                print(f"utilization: {100 * (self.execution_unit.used_percentage_sum / self.clock.get_cycle()):.4f}")
                print(f"total time: {(time.time() - start) / 60:.2f} minutes")
                print("")

        total_inst_so_far = 0
        FINAL_STRING = ""
        for i, thread in enumerate(self.threads):
            total_inst_so_far += self.threads[i].instruction
            print(f"thread {i} finished after {thread.final_cycle} cycles")
            FINAL_STRING += SINGLE_THREAD_STRING.format(i, thread.final_cycle)
        print(f"total number of cycles: {self.clock.get_cycle()}")
        FINAL_STRING += TOTAL_CYCLES_STRING.format(self.clock.get_cycle())
        print(f"IPC: {total_inst_so_far / self.clock.get_cycle():.4f}")
        FINAL_STRING += IPC_STRING.format(total_inst_so_far / self.clock.get_cycle())
        print(f"CPI: {self.clock.get_cycle() / total_inst_so_far:.4f}")
        FINAL_STRING += CPI_STRING.format(self.clock.get_cycle() / total_inst_so_far)
        print(f"utilization: {100 * (self.execution_unit.used_percentage_sum / self.clock.get_cycle()):.4f}")
        FINAL_STRING += UTILIZATION_STRING.format(
            100 * (self.execution_unit.used_percentage_sum / self.clock.get_cycle()))
        print(f"total time: {(time.time() - start) / 60:.2f} minutes")
        FINAL_STRING += TOTAL_TIME_STRING.format((time.time() - start) / 60)

        return FINAL_STRING

    def get_unexecuted_instruction_window_from_thread(self, thread_index: int) -> pd.DataFrame:
        """
        get a window_ooo of of instructions that can be run
        :param thread_index: index of the thread
        :return: (int, enum)
        """
        current_thread = self.threads[thread_index]
        instructions = current_thread.get_unexecuted_instructions()
        return instructions

    def set_instruction_ran_on_thread(self, thread_index: int, instruction_id: int, num_cycles: int):
        """

        :return:
        """
        self.threads[thread_index].set_instruction_finish_cycle(instruction_id, num_cycles)

    def execute_instruction(self, instruction_type: str):
        """
        try to execute command
        :return: boolean of true or false
        """
        return self.execution_unit.execute_instruction(instruction_type)
