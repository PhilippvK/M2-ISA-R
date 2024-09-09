# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

import argparse
import logging
import pathlib
import pickle
from collections import defaultdict

from ...metamodel import M2_METAMODEL_VERSION, M2Model, arch, behav

logger = logging.getLogger("collect_outline_tasks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel file containing the models to generate.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--inplace", "-i", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper()))

    top_level = pathlib.Path(args.top_level)

    with open(top_level, "rb") as f:
        model_obj: M2Model = pickle.load(f)

    if model_obj.model_version != M2_METAMODEL_VERSION:
        logger.warning("Loaded model version mismatch")


    outline_tasks = defaultdict(list)

    def common_helper(set_def):
        ret = []
        for func_name, func_def in set_def.functions.items():
            attributes = func_def.attributes
            # TODO: add as M2-ISA-R attribute
            if "instr" in attributes:
                attr_val = attributes["instr"]
                assert isinstance(attr_val, list)
                assert len(attr_val) == 1
                attr_val = attr_val[0]
                assert isinstance(attr_val, behav.StringLiteral)
                attr_val = attr_val.value
                if "::" in attr_val:
                    instr_name, outp_name = attr_val.split("::", 1)
                else:
                    instr_name = attr_val
                    outp_name = "rd"  # TODO: use!
                ret.append(instr_name)
        return ret

    # for core_name, core_def in model_obj.cores.items():
    #     tasks = common_helper(core_def)
    #     if tasks:
    #         outline_tasks[core_name].extend(tasks)

    for set_name, set_def in model_obj.sets.items():
        tasks = common_helper(set_def)
        if tasks:
            outline_tasks[set_name].extend(tasks)

    if outline_tasks:
        assert len(outline_tasks) == 1
        for top_set_name, tasks in outline_tasks.items():
            remaining = list(set(tasks))
            found = {}
            for set_name, set_def in model_obj.sets.items():
                print("set_name", set_name)
                # if set_name == top_set_name:
                #     continue
                for instr_enc, instr_def in set_def.instructions.items():
                    instr_name = instr_def.name
                    print("instr_name", instr_name)
                    if instr_name in remaining:
                        instr_def.attributes["outline"] = []
                        found[instr_enc] = instr_def
                        remaining.remove(instr_name)
            print("remaining", remaining)
            assert len(remaining) == 0
            top_set_def = model_obj.sets[top_set_name]
            top_set_def.instructions.update(found)
            model_obj.sets = {top_set_name: top_set_def}

    if args.output is None:
        assert args.inplace
        out_path = top_level
    else:
        assert not args.inplace
        out_path = pathlib.Path(args.output)

    logger.info("dumping model")
    with open(out_path, "wb") as f:
        pickle.dump(model_obj, f)


if __name__ == "__main__":
    main()
