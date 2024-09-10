# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""

from m2isar.metamodel import behav, arch

# pylint: disable=unused-argument


def operation(self: behav.Operation, context):
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

    register_names = [f"rs{i}" for i in range(1, 32)]
    register_names.append('rd')

    if isinstance(self.target, behav.IndexedReference):
            if isinstance(self.target.index, behav.NamedReference):
                index_ref = self.target.index.reference
                # if index_ref.name == 'rd':
                    # Replace X[rd] with rd_val
                out_val = arch.Scalar(
                    name=index_ref.name + '_val',
                    value=None,
                    static=False,
                    # size=index_ref.size,
                    size=64,
                    data_type=index_ref.data_type
                )
                # rd_val_ref = behav.NamedReference(reference=rd_val)    
                context.registers_out[out_val] = self.target
                self.target = behav.ScalarDefinition(scalar=out_val)
    
    # Define a recursive function to handle nested expressions
    def traverse_expression(expr, context):
        if isinstance(expr, behav.IndexedReference):
            if isinstance(expr.index, behav.NamedReference):
                if expr.index.reference.name in register_names:
                    # Replace X[rsX] with rsX_val
                    rsx_val = arch.Scalar(
                        name=expr.index.reference.name + '_val',
                        value=None,
                        static=False,
                        # size=expr.index.reference.size,
                        size=64,
                        data_type=expr.index.reference.data_type
                    )
                    rsx_val_ref = behav.NamedReference(reference=rsx_val)
                    context.registers_in[rsx_val] = expr
                    return rsx_val_ref
                
        # If the expression is a function call, traverse its arguments
        if isinstance(expr, behav.FunctionCall):
            new_args = []
            for arg in expr.args:
                # Recursively traverse each argument
                new_arg = traverse_expression(arg, context)
                new_args.append(new_arg)
            # Update the function call with the new arguments
            expr.args = new_args
            return expr
        
        # If it's a group or other complex expression, traverse deeper
        if hasattr(expr, 'expr'):
            expr.expr = traverse_expression(expr.expr, context)

        # Return the (possibly modified) expression
        return expr

    # Start the recursive traversal from the main expression
    self.expr = traverse_expression(self.expr, context)

    # Continue with the normal expression generation

    # self.target = self.expr.generate(context)
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

