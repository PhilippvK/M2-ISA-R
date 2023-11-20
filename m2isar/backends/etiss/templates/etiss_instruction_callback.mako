	[] (BitArray & ba,etiss::CodeSet & cs,InstructionContext & ic)
	{

// -----------------------------------------------------------------------------
${'\n'.join(misc_code)}
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
${fields_code}
// -----------------------------------------------------------------------------

	% for name, part in operation.generate().items():
	{
		CodePart & cp = cs.append(CodePart::${name});

		cp.code() = std::string("//${instr_name}\n");

// -----------------------------------------------------------------------------
${part}
// -----------------------------------------------------------------------------
		% if name == "INITIALREQUIRED":
		% for reg in sorted(reg_dependencies):
		cp.getRegisterDependencies().add(reg_name[${reg}], ${core_default_width});
		% endfor
		% for reg in sorted(reg_affected):
		cp.code() += "printf(\"X[%d]=%x \", ";
		cp.code() += std::to_string(${reg});
		cp.code() += ", ";
		cp.code() += "*((RV32IMACFD*)cpu)->X[";
		cp.code() += std::to_string(${reg});
		cp.code() += "]);\n";
		cp.getAffectedRegisters().add(reg_name[${reg}], ${core_default_width});
		% endfor
		cp.code() += "printf(\"\\n\");\n";
		cp.getAffectedRegisters().add("instructionPointer", 32);
		% endif
	}
	%endfor

		return true;
	}
