"""
This module will create Objects on import which are used to generate Opcodes for custom instructions
In Python an Imports will only create the import Object once, so they act like a singleton

Currently this only includes Greenfield instructions and
only uses the major opcodes Custom[0-3] as specified by the RISC-V standard

This could be changed in the future by adding a function which adds unused opcodes to the list
"""

from typing import Dict, List, Union, Optional, Tuple

from ...metamodel import arch
from .operands import Operand, get_immediates_with_name, get_register_names


unused_opcodes = [0b000_1011, 0b010_1011, 0b101_1011, 0b111_1011]
"""
only using the major op-codes custom-[0,3] as specified in table 19.1 in "Volume I: RISC-V User-Level ISA V2.2"
bits 1:0 are always 11; 00, 01 and 10 are used by the compressed instructions
bits 4:2 = 111 could be used if we decide to limit the usage to 32 bit instrucions/rv32
If the opcodes dont need to be standard compatible,
this list could be extended at runtime with the opcodes of the unused extensions
"""


class OpcodeGenerator:
    """Class to store and get the next free opcode and funct3
    This should never be used outside of this module, and only be instantiated once"""

    def __init__(self):
        self.opcode: Optional[int] = None
        self.funct3: int = 0

    def get(self) -> Tuple[int, int]:
        """
        Get a new opcode as a tuple of (minor, major) opcode,
        Returns (funct3, opcode)
        """
        # checking if there are minor opcodes left or the major opcode is unset
        if self.funct3 > 0b111 or self.opcode is None:
            try:
                self.opcode = unused_opcodes.pop()
                self.funct3 = 0
            except IndexError as e:
                raise RuntimeError("No Major opcode left!") from e

        funct3 = self.funct3
        self.funct3 += 1
        return (funct3, self.opcode)


class FunctNOpcodeGenerator:
    """Class to generate opcodes with an additional funct field, like the standard R-Format
    gets a reference to a basic opcode generator"""

    def __init__(self, opcode_gen: OpcodeGenerator, funct_size: int):
        self.opcode_generator = opcode_gen
        self.opcode: int = 0
        self.funct3: Optional[int] = None
        self.n: int = funct_size
        self.funct_n: int = 0

    def get(self) -> Tuple[int, int, int]:
        """returns (functN, funct3, opcode)"""
        if self.funct3 is None or self.funct_n >= 2**self.n:
            self.funct3, self.opcode = self.opcode_generator.get()
            self.funct_n = 0
        funct_n = self.funct_n
        self.funct_n += 1
        return (funct_n, self.funct3, self.opcode)


i_opcodes = OpcodeGenerator()
"""I-Format: imm   | rs1 | func3 | rd | opcode
		  	 31:20 |19:15| 14:12 |11:7| 6:0"""

r_opcodes = FunctNOpcodeGenerator(opcode_gen=i_opcodes, funct_size=7)
"""R-Format: funct7 | rs2 | rs1 | funct3 | rd | opcode
		   	  31:25 |24:20|19:15| 14:12  |11:7| 6:0"""

f2_opcodes = FunctNOpcodeGenerator(opcode_gen=i_opcodes, funct_size=2)
"""Simmilar to the std R-Format, but with 2 instead of 7 additional funct bits.
Allows for 3 registers and a 5 bit immediate.
Used by e.g. Core-V cv.addN"""


def _reset_enc_generators():
    """
    This function should only be used in the unit tests!
    It resets the encoding generators, so tests can run independently or in succession
    """
    global unused_opcodes
    global i_opcodes
    global r_opcodes
    global f2_opcodes

    unused_opcodes = [0b000_1011, 0b010_1011, 0b101_1011, 0b111_1011]
    i_opcodes = OpcodeGenerator()
    r_opcodes = FunctNOpcodeGenerator(opcode_gen=i_opcodes, funct_size=7)
    f2_opcodes = FunctNOpcodeGenerator(opcode_gen=i_opcodes, funct_size=2)


def get_mm_encoding(in_operands: Dict[str, Operand], out_operands) -> List[Union[arch.BitField, arch.BitVal]]:
    """
    Finds the next available Opcode and creates the encoding for use with the m2isar metamodel
    """
    # figure out the format
    # print("operands", in_operands)
    immediates = get_immediates_with_name(in_operands)
    in_register_names = get_register_names(in_operands)
    # print("out_operands", out_operands)
    out_register_names = list(out_operands.keys())
    # print("in_register_names", in_register_names)
    # print("out_register_names", out_register_names)
    imm_count = len(immediates)
    # print("imm_count", imm_count)
    in_reg_count = len(in_operands) - imm_count
    # print("in_reg_count", in_reg_count)
    out_reg_count = len(out_register_names)
    # print("out_reg_count", out_reg_count)
    # input("!!!")

    if imm_count > 3:
        raise NotImplementedError("Currently instructions with more than three immediates are not supported!")
    if in_reg_count > 3:
        raise NotImplementedError("No format available with more than 3 Register sources!")
    # if len(out_register_names) > 1:
    #     raise NotImplementedError("Multiple output registers not supported!")
    # assert len(in_register_names) + len(out_register_names) == reg_count

    # print("immediates", immediates)
    # print("imm_count", imm_count)
    # print("reg_count", reg_count)

    # TODO: clean up the if statements to find the correct format
    if out_reg_count == 0:
        # raise NotImplementedError("Zero output registers not supported!")
        if imm_count == 0:
            if in_reg_count == 2:
                funct7, funct3, opcode = r_opcodes.get()
                # ?-Format: funct7 | rs2 | rs1 | funct3 | 00000 | opcode
                return [
                    arch.BitVal(7, funct7),
                    reg_bitfield(in_register_names[1]),
                    reg_bitfield(in_register_names[0]),
                    arch.BitVal(3, funct3),
                    arch.BitVal(5, 0),  # TODO: make use of this!!
                    arch.BitVal(7, opcode),
                ]
        elif imm_count == 1:
            imm_name, immediate = immediates[0]
            if in_reg_count == 2:
                # S-Format: imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode
                raise NotImplementedError("Branch RR")
            elif in_reg_count == 1:
                if immediate.width <= 5:
                    update_imm_width(immediate, 5)
                elif immediate.width <= 12:
                    update_imm_width(immediate, 12)
                elif immediate.width <= 17:
                    update_imm_width(immediate, 17)
                    funct3, opcode = i_opcodes.get()  # TODO: is this fine?
                    imm_sign = arch.DataType.S if immediate.sign == "s" else arch.DataType.U
                    return [
                        arch.BitField(imm_name, arch.RangeSpec(16, 5), imm_sign),
                        reg_bitfield(in_register_names[0]),
                        arch.BitVal(3, funct3),
                        arch.BitField(imm_name, arch.RangeSpec(4, 0), imm_sign),
                        arch.BitVal(7, opcode),
                    ]

        elif imm_count == 2:
            immediates = sorted(immediates, key=lambda x: x[1].width)
            smaller_imm_name, smaller_immediate = immediates[0]
            print("smaller_imm_name", smaller_imm_name)
            larger_imm_name, larger_immediate = immediates[1]
            print("larger_imm_name", larger_imm_name)
            if larger_immediate.width <= 5:
                raise NotImplementedError("Branch RII <=5 <=5")
            elif larger_immediate.width <= 12:
                print("1!")
                update_imm_width(larger_immediate, 12)
                if in_reg_count == 1 and smaller_immediate.width <= 5:
                    print("2!")
                    funct3, opcode = i_opcodes.get()  # TODO: is this fine?
                    update_imm_width(smaller_immediate, 5)
                    # ?-Format: imm[11:5] | imm5 | rs1 | funct3 | imm[4:0] | opcode
                    larger_imm_sign = arch.DataType.S if larger_immediate.sign == "s" else arch.DataType.U
                    smaller_imm_sign = arch.DataType.S if smaller_immediate.sign == "s" else arch.DataType.U
                    return [
                        arch.BitField(larger_imm_name, arch.RangeSpec(11, 5), larger_imm_sign),
                        arch.BitField(smaller_imm_name, arch.RangeSpec(4, 0), smaller_imm_sign),
                        reg_bitfield(in_register_names[0]),
                        arch.BitVal(3, funct3),
                        arch.BitField(larger_imm_name, arch.RangeSpec(4, 0), larger_imm_sign),
                        arch.BitVal(7, opcode),
                    ]
    elif out_reg_count == 1:

        if in_reg_count == 3:
            funct2, funct3, major = f2_opcodes.get()
            # R-Format: funct2 | rs3 | rs2 | rs1 | funct3 | rd | opcode
            return [
                arch.BitVal(2, funct2),
                reg_bitfield(in_register_names[2]),
                reg_bitfield(in_register_names[1]),
                reg_bitfield(in_register_names[0]),
                arch.BitVal(3, funct3),
                reg_bitfield(out_register_names[0]),
                arch.BitVal(7, major),
            ]
        if in_reg_count == 2:
            if imm_count == 1:
                imm_name, immediate = immediates[0]
                if immediate.width <= 5:
                    funct2, funct3, opcode = f2_opcodes.get()
                    update_imm_width(immediate, 5)
                    imm_sign = arch.DataType.S if immediate.sign == "s" else arch.DataType.U
                    # Format: funct2 | imm5 | rs2 | rs1 | funct3 | rD | opcode
                    return [
                        arch.BitVal(2, funct2),
                        arch.BitField(imm_name, arch.RangeSpec(4, 0), imm_sign),
                        reg_bitfield(in_register_names[1]),
                        reg_bitfield(in_register_names[0]),
                        arch.BitVal(3, funct3),
                        reg_bitfield(out_register_names[0]),
                        arch.BitVal(7, opcode),
                    ]
            elif imm_count == 0:
                # no imm's and only 2 regs
                funct7, funct3, major = r_opcodes.get()
                # R-Format: funct7 | rs2 | rs1 | funct3 | rd | opcode
                return [
                    arch.BitVal(7, funct7),
                    reg_bitfield(in_register_names[1]),
                    reg_bitfield(in_register_names[0]),
                    arch.BitVal(3, funct3),
                    reg_bitfield(out_register_names[0]),
                    arch.BitVal(7, major),
                ]
        if in_reg_count == 1:
            if imm_count == 2:
                immediates = sorted(immediates, key=lambda x: x[1].width)
                smaller_imm_name, smaller_immediate = immediates[0]
                larger_imm_name, larger_immediate = immediates[1]
                if smaller_immediate.width <= 5 and larger_immediate.width <= 5:
                    update_imm_width(smaller_immediate, 5)
                    update_imm_width(larger_immediate, 5)
                    funct2, funct3, major = f2_opcodes.get()
                    larger_imm_sign = arch.DataType.S if larger_immediate.sign == "s" else arch.DataType.U
                    smaller_imm_sign = arch.DataType.S if smaller_immediate.sign == "s" else arch.DataType.U
                    # F2-Format: funct2 | imm5 | imm5_2 | rs1 | funct3 | rd | opcode
                    return [
                        arch.BitVal(2, funct2),
                        arch.BitField(larger_imm_name, arch.RangeSpec(4, 0), larger_imm_sign),
                        arch.BitField(smaller_imm_name, arch.RangeSpec(4, 0), smaller_imm_sign),
                        reg_bitfield(in_register_names[0]),
                        arch.BitVal(3, funct3),
                        reg_bitfield(out_register_names[0]),
                        arch.BitVal(7, major),
                    ]
            elif imm_count == 1:
                imm_name, immediate = immediates[0]
                if immediate.width > 12:
                    raise ValueError(f"Bitwidth(={immediate.width}) of the immediate is too large!")

                # If its 5 bits or smaller we can use the R-Format and
                # use rs2 to encode the immediate to save encoding space
                # This is the encoding for e.g. cv.clip
                if immediate.width <= 5:
                    funct7, funct3, opcode = r_opcodes.get()
                    update_imm_width(immediate, 5)
                    imm_sign = arch.DataType.S if immediate.sign == "s" else arch.DataType.U
                    # R-Format: funct7 | imm5 | rs1 | funct3 | rd | opcode
                    return [
                        arch.BitVal(7, funct7),
                        arch.BitField(imm_name, arch.RangeSpec(4, 0), imm_sign),
                        reg_bitfield(in_register_names[0]),
                        arch.BitVal(3, funct3),
                        reg_bitfield(out_register_names[0]),
                        arch.BitVal(7, opcode),
                    ]
                elif immediate.width <= 12:
                    # otherwise we just use the I-Format
                    funct3, major = i_opcodes.get()
                    update_imm_width(immediate, 12)
                    imm_sign = arch.DataType.S if immediate.sign == "s" else arch.DataType.U
                    # I-Format: imm12 | rs1 | funct3 | rd | opcode
                    return [
                        arch.BitField(imm_name, arch.RangeSpec(11, 0), imm_sign),
                        reg_bitfield(in_register_names[0]),
                        arch.BitVal(3, funct3),
                        reg_bitfield(out_register_names[0]),
                        arch.BitVal(7, major),
                    ]

            elif imm_count == 0:
                # 3 register and an immediate => max bitwidth = 5; e.g. cv.addN
                # no imm's and only 1 regs, e.g. cv.abs -> just set rs2 to 0
                funct7, funct3, major = r_opcodes.get()
                # R-Format: funct7 | 00000 | rs1 | funct3 | rd | opcode
                return [
                    arch.BitVal(7, funct7),
                    arch.BitVal(5, 0),  # TODO: make use of this!!
                    reg_bitfield(in_register_names[0]),
                    arch.BitVal(3, funct3),
                    reg_bitfield(out_register_names[0]),
                    arch.BitVal(7, major),
                ]
        if in_reg_count == 0:
            if imm_count == 1:
                pass
            elif imm_count == 2:
                immediates = sorted(immediates, key=lambda x: x[1].width)
                smaller_imm_name, smaller_immediate = immediates[0]
                larger_imm_name, larger_immediate = immediates[1]
                if smaller_immediate.width == 1 and larger_immediate.width == 16:
                    funct3, major = i_opcodes.get()
                    # LI16-Format: n | imm16 | funct3 | rd | opcode
                    return [
                        arch.BitField(smaller_imm_name, arch.RangeSpec(0, 0), arch.DataType.U),
                        arch.BitField(larger_imm_name, arch.RangeSpec(15, 0), arch.DataType.U),
                        arch.BitVal(3, funct3),
                        reg_bitfield(out_register_names[0]),
                        arch.BitVal(7, major),
                    ]
                elif smaller_immediate.width == larger_immediate.width:
                    if larger_immediate.width <= 5:
                        update_imm_width(smaller_immediate, 5)
                        update_imm_width(larger_immediate, 5)
                        smaller_imm_sign = arch.DataType.S if smaller_immediate.sign == "s" else arch.DataType.U
                        larger_imm_sign = arch.DataType.S if larger_immediate.sign == "s" else arch.DataType.U
                        funct7, funct3, opcode = r_opcodes.get()
                        # R-Format: funct7 | imm5 | imm5_2 | funct3 | rd | opcode
                        return [
                            arch.BitVal(7, funct7),
                            arch.BitField(larger_imm_name, arch.RangeSpec(4, 0), larger_imm_sign),
                            arch.BitField(smaller_imm_name, arch.RangeSpec(4, 0), smaller_imm_sign),
                            arch.BitVal(3, funct3),
                            reg_bitfield(out_register_names[0]),
                            arch.BitVal(7, opcode),
                        ]
            elif imm_count == 3:
                immediates = sorted(immediates, key=lambda x: x[1].width)
                smaller_imm_name, smaller_immediate = immediates[0]
                larger_imm_name, larger_immediate = immediates[1]
                largest_imm_name, largest_immediate = immediates[2]
                if smaller_immediate.width <= 5 and larger_immediate.width <= 5 and largest_immediate.width <= 5:
                    update_imm_width(smaller_immediate, 5)
                    update_imm_width(larger_immediate, 5)
                    update_imm_width(largest_immediate, 5)
                    funct2, funct3, major = f2_opcodes.get()
                    largest_imm_sign = arch.DataType.S if largest_immediate.sign == "s" else arch.DataType.U
                    larger_imm_sign = arch.DataType.S if larger_immediate.sign == "s" else arch.DataType.U
                    smaller_imm_sign = arch.DataType.S if smaller_immediate.sign == "s" else arch.DataType.U
                    # F2-Format: funct2 | imm5 | imm5_2 | imm_3 | funct3 | rd | opcode
                    return [
                        arch.BitVal(2, funct2),
                        arch.BitField(largest_imm_name, arch.RangeSpec(4, 0), largest_imm_sign),
                        arch.BitField(larger_imm_name, arch.RangeSpec(4, 0), larger_imm_sign),
                        arch.BitField(smaller_imm_name, arch.RangeSpec(4, 0), smaller_imm_sign),
                        arch.BitVal(3, funct3),
                        reg_bitfield(out_register_names[0]),
                        arch.BitVal(7, major),
                    ]
    elif out_reg_count > 1:
        if in_reg_count == 2:
            # 2 bits left
            if imm_count == 0:
                funct2, funct3, major = f2_opcodes.get()
                # ?-Format: funct2 | rs2 | rs1 | rd2 | funct3 | rd | opcode
                return [
                    arch.BitVal(2, funct2),
                    reg_bitfield(in_register_names[1]),
                    reg_bitfield(in_register_names[0]),
                    reg_bitfield(out_register_names[1]),
                    arch.BitVal(3, funct3),
                    reg_bitfield(out_register_names[0]),
                    arch.BitVal(7, major),
                ]
        elif in_reg_count == 1:
            # 7 bits left
            if imm_count == 0:
                funct7, funct3, opcode = r_opcodes.get()
                # ?-Format: funct7 | rs1 | rd2 | funct3 | rd | opcode
                return [
                    arch.BitVal(7, funct7),
                    reg_bitfield(in_register_names[0]),
                    reg_bitfield(out_register_names[1]),
                    arch.BitVal(3, funct3),
                    reg_bitfield(out_register_names[0]),
                    arch.BitVal(7, opcode),
                ]
        elif in_reg_count == 0:
            # 12 bits left
            if imm_count == 0:
                funct7, funct3, opcode = r_opcodes.get()
                # ?-Format: funct7 | 00000 | rd2 | funct3 | rd | opcode
                return [
                    arch.BitVal(7, funct7),
                    arch.BitVal(5, 0),  # TODO: make use of this!!
                    reg_bitfield(out_register_names[1]),
                    arch.BitVal(3, funct3),
                    reg_bitfield(out_register_names[0]),
                    arch.BitVal(7, opcode),
                ]

    raise NotImplementedError("Unknown instruction format!")


def get_cdsl_encoding(operands: Dict[str, Operand]) -> str:
    """Generate an encoding for the given operands\n
    Actual encoding gets generated by "get_mm_encoding()" and just performes string formating to emmit CoreDSL"""
    mm_encoding = get_mm_encoding(operands)
    cdsl_encoding = ""

    for field in mm_encoding:
        if isinstance(field, arch.BitVal):
            snippet = f"{field.length}'" + bin(field.value)[1:]
        else:
            snippet = f"{field.name}[{field.range.upper_base}:{field.range.lower_base}]"
        cdsl_encoding += snippet + " :: "

    # remove trailing " :: "
    cdsl_encoding = cdsl_encoding[:-4]

    return cdsl_encoding


def reg_bitfield(name: str) -> arch.BitField:
    """
    Helper funtion to reduce boilerplate code
    Returns a BitField Object with the specified name"""
    return arch.BitField(name, arch.RangeSpec(4, 0), arch.DataType.U)


def update_imm_width(immediate: Operand, width: int) -> None:
    """Adjust the width of an immediate to fit the encoding"""
    if not immediate.immediate:
        raise ValueError("This functions should only be called on immediate operands!")

    if immediate.width != width:
        # I should propably use a logger for this
        print(f"Increasing Operand width from {immediate.width} to {width} to fit encoding.")
        immediate.width = width
