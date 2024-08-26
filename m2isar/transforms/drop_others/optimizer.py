# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R metamodel by removing unused constants/...."""

import sys
import argparse
import logging
import pathlib
import pickle

from ...metamodel import M2_METAMODEL_VERSION, M2Model

logger = logging.getLogger("drop_others")


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--inplace", "-i", action="store_true")
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    with open(top_level, "rb") as f:
        model_obj: M2Model = pickle.load(f)

    logger.info("loading models")

    # load models
    if model_obj.model_version != M2_METAMODEL_VERSION:
        logger.warning("Loaded model version mismatch")


    for core_name, core_def in model_obj.cores.items():
        raise NotImplementedError

    sets_to_keep = {}
    for set_name, set_def in model_obj.sets.items():
        keep = {}
        for instr_enc, instr_def in set_def.instructions.items():
            if "fuse" in instr_def.attributes or "outline" in instr_def.attributes:
                keep[instr_enc] = instr_def
        if len(keep) > 0:
            set_def.instructions = keep
            sets_to_keep[set_name] = set_def
    model_obj.sets = sets_to_keep

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
