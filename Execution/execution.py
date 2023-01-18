from constants import InstructionType, InstructionError
from random import random


class Execution(object):
    def __init__(self,
                 alus_units,
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
        self.ldsts = [0 for _ in range(ldsts_units)]
        self.branches = [0 for _ in range(branch_units)]
        self.alu_time = alu_time
        self.br_time = br_time
        self.ldsts_time = ldsts_time
        self.br_miss_rate = br_miss_rate
        self.br_penalty = br_penalty
        self.cache_miss_rate = cache_miss_rate
        self.mem_penalty = mem_penalty

    def execute_instruction(self, instruction_type: int):
        """
        try to execute instruction of type
        :return: cycles to run command, -1 if no units are free
        """
        executed = -1
        if instruction_type == InstructionType.ALU:
            if self.execute_for_unit(self.alus, self.alu_time):
                executed = self.alu_time
        elif instruction_type == InstructionType.LDST:
            miss = random() < self.cache_miss_rate
            unit_time = self.ldsts_time if not miss else self.ldsts + self.mem_penalty
            if self.execute_for_unit(self.ldsts, self.ldsts_time):
                # TODO: how much time to does the unit stop for?
                executed = unit_time
        elif instruction_type == InstructionType.BRANCH:
            miss = random() < self.br_miss_rate
            if self.execute_for_unit(self.br_miss_rate, self.br_time):
                executed = self.br_time if not miss else self.br_time + self.br_penalty
        else:
            raise InstructionError("bad instruction type!")
        return executed

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
        self.alus = [i-1 for i in self.alus if i > 0]
        self.ldsts = [i-1 for i in self.ldsts if i > 0]
        self.branches = [i-1 for i in self.branches if i > 0]
