# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

from m2isar.metamodel import behav, arch

# pylint: disable=unused-argument


def operation(self: behav.Operation, context):
    
    # Despite the names of the keys e.g. rs1_val are the same, but dict  treats keys as distinct keys
    def eliminate_duplicates(d: dict) -> None:
        seen_names = set()
        keys_to_remove = []

        # Identify keys to remove
        for key in d:
            if key.name in seen_names:
                keys_to_remove.append(key)  # Mark key for removal
            else:
                seen_names.add(key.name)

        # Remove the duplicate keys
        for key in keys_to_remove:
            del d[key]

    def write_scalars(d: dict, e: dict) -> None:
        """
        This function inserts assignment statements into the behavior section for each register.
        """
        # Loop through the dictionary and create assignments for each target and expression
        for i, (target, expr) in enumerate(d.items()):
            # Create a new assignment for each register
            assignment_def = behav.Assignment(
                target=behav.ScalarDefinition(target),  # Define scalar target (e.g., rs1_val, rs2_val)
                expr=behav.IndexedReference(            # Define expression (e.g., X[rs1], X[rs2])
                    reference=expr.reference,
                    index=expr.index
                )
            )
            # Insert the assignment into the behavior section, ensuring no duplicate insertions
            print(assignment_def)
            self.statements.insert(i, assignment_def)

        for target, expr in e.items():
            assignment_def = behav.Assignment(
                target=behav.IndexedReference(
                    reference=expr.reference,
                    index=expr.index
                    ),
                expr=behav.NamedReference(target)
            )
            self.statements.insert(len(self.statements), assignment_def)


     # Created control flow, because def operation is being called twice 
     # not the most elegant solution, but it will do for now
    def insert_io(context):
        if not context.registers_printed:
            eliminate_duplicates(context.registers_in)
            eliminate_duplicates(context.registers_out)
            write_scalars(context.registers_in, context.registers_out)
            context.registers_printed = True
    
    insert_io(context)
    
    statements = []
    for stmt in self.statements:
        temp = stmt.generate(context)
        if isinstance(temp, list):
            statements.extend(temp)
        else:
            statements.append(temp)

    self.statements = statements
    return self


def binary_operation(self: behav.BinaryOperation, context):
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def slice_operation(self: behav.SliceOperation, context):
    self.expr = self.expr.generate(context)
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def concat_operation(self: behav.ConcatOperation, context):
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def number_literal(self: behav.IntLiteral, context):
    return self


def int_literal(self: behav.IntLiteral, context):
    return self


def scalar_definition(self: behav.ScalarDefinition, context):

    return self


def break_(self: behav.Break, context):
    return self


def assignment(self: behav.Assignment, context):
    self.target = self.target.generate(context)
    self.expr = self.expr.generate(context)

    return self


def conditional(self: behav.Conditional, context):
    # print("conditional")
    self.conds = [x.generate(context) for x in self.conds]
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def loop(self: behav.Loop, context):
    self.cond = self.cond.generate(context)
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def ternary(self: behav.Ternary, context):
    self.cond = self.cond.generate(context)
    self.then_expr = self.then_expr.generate(context)
    self.else_expr = self.else_expr.generate(context)

    return self


def return_(self: behav.Return, context):
    if self.expr is not None:
        self.expr = self.expr.generate(context)

    return self


def unary_operation(self: behav.UnaryOperation, context):
    self.right = self.right.generate(context)

    return self


def named_reference(self: behav.NamedReference, context):
    return self


def indexed_reference(self: behav.IndexedReference, context):
    self.index = self.index.generate(context)

    return self


def type_conv(self: behav.TypeConv, context):
    self.expr = self.expr.generate(context)

    return self


def callable_(self: behav.Callable, context):
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def group(self: behav.Group, context):
    self.expr = self.expr.generate(context)

    return self


def procedure_call(self: behav.ProcedureCall, context):
    return self

