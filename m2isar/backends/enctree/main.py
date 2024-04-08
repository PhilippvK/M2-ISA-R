# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Viewer tool to visualize an M2-ISA-R model hierarchy."""

import argparse
import logging
import pathlib
import pickle
import pandas as pd
import numpy as np
from functools import reduce
from collections import defaultdict

from .utils import RootNode
from ...metamodel import M2_METAMODEL_VERSION, M2Model, arch, patch_model
from ...metamodel.utils.expr_preprocessor import (process_attributes,
                                                  process_functions,
                                                  process_instructions)
logger = logging.getLogger("enctree")


def sort_instruction(entry: "tuple[tuple[int, int], arch.Instruction]"):
    """Instruction sort key function. Sorts most restrictive encoding first."""
    (code, mask), _ = entry
    return bin(mask).count("1"), code
    #return code, bin(mask).count("1")

def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('top_level', help="A .m2isarmodel file containing the models to generate.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    abs_top_level = top_level.resolve()
    search_path = abs_top_level.parent.parent
    model_fname = abs_top_level

    if abs_top_level.suffix == ".core_desc":
        logger.warning(".core_desc file passed as input. This is deprecated behavior, please change your scripts!")
        search_path = abs_top_level.parent
        model_path = search_path.joinpath('gen_model')

        if not model_path.exists():
            raise FileNotFoundError('Models not generated!')
        model_fname = model_path / (abs_top_level.stem + '.m2isarmodel')

    output_base_path = search_path.joinpath('gen_output')
    output_base_path.mkdir(exist_ok=True)

    logger.info("loading models")

    # load models
    with open(model_fname, 'rb') as f:
        model_obj: "M2Model" = pickle.load(f)

    if model_obj.model_version != M2_METAMODEL_VERSION:
        logger.warning("Loaded model version mismatch")

    models = model_obj.models

    # add each core to the treeview
    for core_name, core_def in models.items():
        logger.info("preprocessing model %s", core_name)

        # group instructions by size
        instrs_by_size = defaultdict(dict)

        for k, v in core_def.instructions.items():
            instrs_by_size[v.size][k] = v

        # sort instructions by encoding
        for k, v in instrs_by_size.items():
            instrs_by_size[k] = dict(sorted(v.items(), key=sort_instruction, reverse=True))


        # generate instruction size groups
        for size, instrs in sorted(instrs_by_size.items()):
            print("sz", size)
            if size != 32:
                continue
            df = pd.DataFrame()

            root = RootNode(size=size)

            # generate instructions
            for (code, mask), instr_def in instrs.items():
                print("---")
                opcode_str = "{code:0{width}x}:{mask:0{width}x}".format(code=code, mask=mask, width=int(instr_def.size/4))
                print("opc", opcode_str)
                print("name", instr_def.name)
                if instr_def.name in ["DII", "CNOP", "CLUI"]:
                    continue

                # generate encoding
                enc_str = []
                for enc in instr_def.encoding:
                    if isinstance(enc, arch.BitVal):
                        enc_str.append(f"{enc.value:0{enc.length}b}")
                    elif isinstance(enc, arch.BitField):
                        enc_str.append(f"{enc.name}[{enc.range.upper}:{enc.range.lower}]")
                vals = {}
                pos = 0
                for enc in reversed(instr_def.encoding):
                    if isinstance(enc, arch.BitVal):
                        lower = pos
                        upper = lower + enc.length - 1
                        key = (upper, lower)
                        vals[key] = enc.value
                        pos += enc.length
                    elif isinstance(enc, arch.BitField):
                        pos += enc.range.length

                print("enc", " ".join(enc_str))
                print("asm", instr_def.disass)
                print("vals", vals)
                df = pd.concat([df, pd.DataFrame({"Name": [instr_def.name], **{k: [v] for k, v in vals.items()}})], axis=0)
            df.reset_index(inplace=True)
            print("df")
            with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
                print(df)
            def helper(df, node=None, depth=1):
                candidates = list(df.columns[(~df.isna()).all()])[2:]
                # print(depth * "*", "candidates", candidates)
                if len(candidates) == 0:
                    # TODO
                    candidates = list(df.columns[2:])
                    def calc_size(x):
                        return x[0] - x[1] + 1
                    candidate_sizes = list(map(calc_size, candidates))
                    candidate_sizes = sorted(candidate_sizes, reverse=True)
                    # print("candidate_sizes", candidate_sizes)
                    candidates = sorted(candidates, reverse=True, key=calc_size)
                    # print("candidates", candidates)
                    candidates_lo = list(map(lambda x: x[1], candidates))
                    # print("candidates_lo", candidates_lo)
                    candidates_hi = list(map(lambda x: x[0], candidates))
                    # print("candidates_hi", candidates_hi)
                    def calc_mask(x):
                        return (2**(x[0]+1)-1) & ~(2**(x[1])-1)
                    # candidate_masks = list(map(lambda x: (2**(x[0])-1) & ~(2**(x[1])-1), list(df.columns[2:])))
                    # candidate_masks = list(map(lambda x: bin((2**(x[0])-1) & ~(2**(x[1])-1)), list(df.columns[2:])))
                    # print("candadte_masks", candidate_masks)
                    biggest = candidates[0]
                    biggest_size = candidate_sizes[0]
                    # print("biggest_size", biggest_size)
                    rest = candidates[1:]
                    rest = sorted(rest, key=lambda x: x[1])
                    # print("rest", rest)
                    rest_sizes = list(map(calc_size, rest))
                    # print("rest_sizes", rest_sizes)
                    first = rest[0]
                    assert first[1] == biggest[1]
                    # rest_lo = candidates_lo[1:]
                    # print("rest_lo", rest_lo)
                    # rest_hi = candidates_hi[1:]
                    # print("rest_hi", rest_hi)
                    assert biggest_size == sum(rest_sizes)
                    # print("q", bin(calc_mask(biggest)))
                    # print("w", bin(reduce(lambda x, y: x | y, map(calc_mask, rest))))
                    assert calc_mask(biggest) == reduce(lambda x, y: x | y, map(calc_mask, rest))
                    # print("df.biggest", df[biggest])
                    sh = 0
                    for r in rest:
                        # print("r", r)
                        hi, lo = r
                        # tmp = df[biggest].values.astype(int) & 0x1
                        tmp = df[biggest].apply(lambda x: x if pd.isna(x) else (int(x) & ((calc_mask(r) >> lo) << sh)))
                        # print("tmp", tmp)
                        df[r].fillna(tmp, inplace=True)
                        sh += (hi - lo + 1)
                        candidates
                    df.drop(columns=[biggest], inplace=True)
                    # print("df", df)
                    candidates = rest
                candidate = candidates[0]
                if node:
                    node = node.select(candidate)
                for group, group_df in df.groupby(candidate, dropna=False):
                    group = int(group)
                    print(depth * "*", candidate, "->", hex(int(group)))
                    node_ = None
                    if node:
                        node_ = node.choose(group)
                    group_df.drop(columns=[candidate], inplace=True)
                    group_df.dropna(axis=1, how='all', inplace=True)
                    # print("B", list(group_df.columns[(~group_df.isna()).all()])[2:])
                    if len(group_df) == 1:
                        print(depth * "*", "Instr:", group_df.Name.values[0])
                        if node_:
                            node_.instruction(group_df.Name.values[0])
                    elif len(group_df) > 1:
                        print(depth * "*", "group_df")
                        print(group_df)
                        helper(group_df, node=node_, depth=depth+1)
            helper(df, node=root)
            root.render()
            root.plot_all("/tmp/plotout/")
        break


if __name__ == "__main__":
    main()
