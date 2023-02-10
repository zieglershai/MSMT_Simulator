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

