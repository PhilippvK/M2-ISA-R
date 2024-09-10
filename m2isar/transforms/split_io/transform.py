# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""Split input and output. 
    Replace X[rs...] with rs..._val. X[rd] with rd_val. Add assignment at the end.
    Add declaration and initialization of inputs at the beginning of behavior section."""

import sys
import argparse
import logging
import pathlib
import pickle
from typing import Union

from ...metamodel import M2_METAMODEL_VERSION, M2Model, arch, behav, patch_model

from . import split_io, insert_io

logger = logging.getLogger("split and insert io")

class RegisterCollector():

    def __init__(self) -> None:
        self.registers_in = {}
        self.registers_out = {}
        self.registers_printed = False


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--inplace", "-i", action="store_true")
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    with open(top_level, "rb") as f:
        model_obj: M2Model = pickle.load(f)

    if model_obj.model_version != M2_METAMODEL_VERSION:
        logger.warning("Loaded model version mismatch")

    for core_name, core_def in model_obj.cores.items():
        logger.debug("Splitting IO for core %s", core_def.name)
        patch_model(split_io)

    for set_name, set_def in model_obj.sets.items():
        logger.debug("Splitting IO for set %s", set_def.name)
        patch_model(split_io)
        for instr_name, instr_def in set_def.instructions.items():
            logger.debug("Splitting IO for instr %s", instr_def.name)
            if "fuse" in instr_def.attributes:
                context = RegisterCollector()
                patch_model(split_io)
                instr_def.operation.generate(context)
                patch_model(insert_io)
                print(instr_def.name)
                instr_def.operation.generate(context)

    if args.output is None:
        assert args.inplace
        out_path = top_level
    else:
        assert not args.inplace
        out_path = pathlib.Path(args.output)

    logger.info("dumping model")
    with open(out_path, "wb") as f:
        pickle.dump(model_obj, f)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

