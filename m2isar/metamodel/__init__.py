# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""This module contains the M2-ISA-R metamodel classes to build an ISA from. The M2-ISA-R
metamodel is split into two submodules, one for architectural description, one for the behavioral
description.

Also included are preprocessing functions, mostly to simplify a model and to extract information
about scalar and function staticness as well as exceptions.

Any model traversal should use the :func:`patch_model` function and a module including the needed
transformations. :func:`patch_model` monkey patches transformation functions into the classes of the
behavior model, therefore separating model code from transformation code. For examples on how
these transformation functions look like, see either the modules in :mod:`m2isar.metamodel.utils`
or the main code generation module :mod:`m2isar.backends.etiss.instruction_transform`. For a description
of the monkey patching, see :func:`patch_model`.

Usually a M2-ISA-R behavioral model is traversed from top to bottom. Necessary contextual
information is passed to lower levels by a user-defined `context` object. Each object should then
generate a piece of output (e.g. c-code for ETISS) and return it to its parent. Value passing between
generation functions is completely user-defined, :mod:`m2isar.backends.etiss.instruction_transform`
uses complex objects in lower levels of translation and switches to strings for the two highest levels of
the hierarchy.
"""

import inspect
import logging
from dataclasses import dataclass, field

from . import arch, behav


def patch_model(module):
	"""Monkey patch transformation functions inside `module`
	into :mod:`m2isar.metamodel.behav` classes

	Transformation functions must have a specific signature for this to work:

	`def transform(self: <behav Class>, context: Any)`

	where `<behav Class>` is the class in :mod:`m2isar.metamodel.behav` which this
	transformation is associated with. Context can be any user-defined object to keep track
	of additional contextual information, if needed.
	"""

	logger = logging.getLogger("patch_model")

	for _, fn in inspect.getmembers(module, inspect.isfunction):
		sig = inspect.signature(fn)
		param = sig.parameters.get("self")
		if not param:
			continue
		if not param.annotation:
			raise ValueError(f"self parameter not annotated correctly for {fn}")
		if not issubclass(param.annotation, behav.BaseNode):
			raise TypeError(f"self parameter for {fn} has wrong subclass")

		logger.debug("patching %s with fn %s", param.annotation, fn)
		param.annotation.generate = fn

intrinsic_defs = [
	arch.Intrinsic("__encoding_size", 16, arch.DataType.U)
]

intrinsics = {x.name: x for x in intrinsic_defs}

#@property
#def intrinsics():
#	return {x.name: x for x in intrinsic_defs}

@dataclass
class LineInfo:
	id: int = field(init=False)
	file_path: str
	start_chr: int
	stop_chr: int
	start_line_no: int
	stop_line_no: int

	__id_counter = 0
	database = {}

	def __post_init__(self):
		self.id = LineInfo.__id_counter
		LineInfo.__id_counter += 1
		LineInfo.database[self.id] = self

	def __hash__(self) -> int:
		return hash(self.id)

	def line_eq(self, other: "LineInfo"):
		if isinstance(other, LineInfo):
			return self.file_path == other.file_path and \
				self.start_line_no == other.start_line_no and \
				self.stop_line_no == other.stop_line_no
		return NotImplemented

	def line_hash(self):
		return hash((self.file_path, self.start_line_no, self.stop_line_no))
