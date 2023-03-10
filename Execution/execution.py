from constants import InstructionType, InstructionError
from random import random


class Execution(object):
    def __init__(self,
                 alus_units,
                 fp_alus_units,
                 ldsts_units,
                 branch_units,
                 alu_time,
                 br_time,
                 ldsts_time,
                 br_miss_rate,
                 br_penalty,
                 cache_miss_rate,
                 mem_penalty):
        """
        This is the execution unit
        """
        self.alus = [0 for _ in range(alus_units)]
        self.fp_alus = [0 for _ in range(fp_alus_units)]
        self.ldsts = [0 for _ in range(ldsts_units)]
        self.branches = [0 for _ in range(branch_units)]
        self.total_units = float(alus_units + fp_alus_units + ldsts_units + branch_units)
        self.alu_time = alu_time
        self.br_time = br_time
        self.ldsts_time = ldsts_time
        self.br_miss_rate = br_miss_rate
        self.br_penalty = br_penalty
        self.cache_miss_rate = cache_miss_rate
        self.mem_penalty = mem_penalty
        self.used_percentage_sum = 0

    def execute_instruction(self, instruction_type: int):
        """
        try to execute instruction of type
        :return: cycles to run command, -1 if no units are free
        """
        executed = -1
        cache_miss = False
        if instruction_type == InstructionType.ALU:
            if self.execute_for_unit(self.alus, self.alu_time):
                executed = self.alu_time
        elif instruction_type == InstructionType.FP_ALU:
            if self.execute_for_unit(self.fp_alus, self.alu_time):
                executed = self.alu_time
        elif instruction_type == InstructionType.LDST:
            miss = random() < self.cache_miss_rate
            unit_time = self.ldsts_time if not miss else self.ldsts_time + self.mem_penalty
            cache_miss = miss
            if self.execute_for_unit(self.ldsts, self.ldsts_time):
                # TODO: how much time to does the unit stop for?
                executed = unit_time
        elif instruction_type == InstructionType.BRANCH:
            miss = random() < self.br_miss_rate
            if self.execute_for_unit(self.branches, self.br_time):
                executed = self.br_time if not miss else self.br_time + self.br_penalty
        else:
            raise InstructionError("bad instruction type!")
        return executed, cache_miss

    @staticmethod
    def execute_for_unit(unit: list, latency: int):
        if 0 in unit:
            unit.remove(0)
            unit.append(latency)
            return True
        return False

    def step(self):
        """
        run one cycle
        :return:
        """
        units_used = sum(x > 0 for x in self.alus) + sum(x > 0 for x in self.fp_alus) + sum(
            x > 0 for x in self.ldsts) + sum(x > 0 for x in self.branches)
        self.used_percentage_sum += (units_used / self.total_units)

        # print((units_used / self.total_units))

        self.alus = [i-1 if i > 0 else i for i in self.alus]
        self.fp_alus = [i-1 if i > 0 else i for i in self.fp_alus]
        self.ldsts = [i-1 if i > 0 else i for i in self.ldsts]
        self.branches = [i-1 if i > 0 else i for i in self.branches]
