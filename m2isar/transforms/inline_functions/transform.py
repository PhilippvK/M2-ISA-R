# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""Remove (rd != 0) checks from M2-ISA-R metamodel."""

import sys
import argparse
import logging
import pathlib
import pickle

from ...metamodel import M2_METAMODEL_VERSION, M2Model, arch, behav, patch_model

from . import visitor

logger = logging.getLogger("inline_functions")


class InlineFunctionsContext:
    def __init__(self, functions: "dict[str, arch.Function]"):
        self.functions = functions


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
        logger.debug("inline functions for core %s", core_def.name)
        raise NotImplementedError

    for set_name, set_def in model_obj.sets.items():
        logger.debug("inline functions for set %s", set_def.name)
        patch_model(visitor)
        context = InlineFunctionsContext(set_def.functions)
        for instr_name, instr_def in set_def.instructions.items():
            logger.debug("inline_functions for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        set_def.functions = {func_name: func_def for func_name, func_def in set_def.functions.items() if "inline" not in func_def.attributes}

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


