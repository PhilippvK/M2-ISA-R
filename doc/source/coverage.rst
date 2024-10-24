CoreDSL 2 Code Coverage
=======================

Generating coverage data
------------------------

M2-ISA-R includes a feature to generate coverage traces for CoreDSL 2 files. It is currently implemented for the ETISS backend. To use, multiple flags and settings must be enabled:

1. Line information is added to the M2-ISA-R ISA model automatically when parsing CoreDSL 2 files
2. When generating an ETISS architecture plugin with ``etiss_writer``, add the flag ``--coverage``
3. ETISS must then be compiled with the option ``ETISS_USE_COREDSL_COVERAGE=on``
4. ETISS will output coverage data to the file ``coverage.csv`` in its current directory. To change the output path, set the ETISS configuration variable ``vp.coredsl_coverage_path`` accordingly.

Analyzing coverage data
-----------------------

To analyze one or more ``coverage.csv`` files, use the ``m2isar2lcov`` M2-ISA-R backend. It converts the data gathered into ``coverage.csv`` files into the ``.info`` format supported by the popular code coverage analysis tool LCOV.

.. code-block::

	$ m2isar2lcov -h
	usage: m2isar2lcov [-h] [--log {critical,error,warning,info,debug}] [--legacy] -o OUTFILE [-a TARGET_ARCH] [-j PARALLEL] top_level line_data [line_data ...]

	positional arguments:
	top_level             A .m2isar file containing model.
	line_data             The CSV line data files matching the model.

	options:
	-h, --help            show this help message and exit
	--log {critical,error,warning,info,debug}
	--legacy              Generate data for LOCV version < 2.0
	-o OUTFILE, --outfile OUTFILE
	-a TARGET_ARCH, --target-arch TARGET_ARCH
	-j PARALLEL, --parallel PARALLEL

Supply the M2-ISA-R model and all ``coverage.csv`` files as positional arguments, specify the output with the ``-o`` flag. Use the ``--legacy`` flag to generate output data compatible with LCOV version < 2.

See below for a complete example from ``coverage.csv`` files to LCOV HTML report:

.. code-block::

	$ m2isar2lcov -o rv_par.info --legacy ../etiss_arch_riscv/top.core_desc ../etiss_riscv_tests/results*/coverage/*.csv
	$ lcov --rc lcov_branch_coverage=1 -a RV32IMACFD.rv_par.info -a RV64IMACFD.rv_par.info -o RV.info
	$ genhtml -o rv_par --branch-coverage RV.info

This example takes all ``coverage.csv`` results from a run of ``etiss_riscv_tests`` and generates two LCOV ``.info`` files from them. These two files are concatenated, and then an HTML report generated from them.
