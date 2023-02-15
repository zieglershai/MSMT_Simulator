from enum import Enum


class InstructionType(Enum):
    ALU = 1
    LDST = 2
    BRANCH = 3
    MISC = 4
    FP_ALU = 5


class PolicyType(Enum):
    RR = 1
    PRR = 2
    TWOLEVEL = 3
    PREFETCHTWOLEVEL = 4


class InstructionError(Exception):
    pass


class PolicyTypeError(Exception):
    pass


INSTRUCTION_TYPE = "INSTRUCTION_TYPE"
ROW_ID = "ROW_ID"
FINISH_CYCLE = "FINISH_CYCLE"
READ_REG_A = "READ_REG_A"
READ_REG_B = "READ_REG_B"
WRITE_REG = "WRITE_REG"

SINGLE_THREAD_STRING = "thread {0} finished after {1} cycles\n"
TOTAL_CYCLES_STRING = "total number of cycles: {0}\n"
IPC_STRING = "IPC: {0}\n"
CPI_STRING = "CPI: {0}\n"
UTILIZATION_STRING = "utilization: {0}\n"
TOTAL_TIME_STRING = "total time: {0} minutes\n"
