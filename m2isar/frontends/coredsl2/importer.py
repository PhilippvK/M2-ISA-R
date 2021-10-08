from .parser_gen import CoreDSL2Listener, CoreDSL2Parser, CoreDSL2Visitor
from .utils import make_parser


class Importer(CoreDSL2Listener):
	def __init__(self, search_path) -> None:
		super().__init__()
		self.imported = set()
		self.new_children = []
		self.new_defs = []
		self.got_new = True
		self.search_path = search_path

	def enterImport_file(self, ctx: CoreDSL2Parser.Import_fileContext):
		filename = ctx.RULE_STRING().getText().replace('"', '')
		if filename not in self.imported:
			print(f"importing file {filename}")
			self.got_new = True
			self.imported.add(filename)

			parser = make_parser(self.search_path/filename)

			tree = parser.description_content()

			self.new_children.extend(tree.children)
			self.new_defs.extend(tree.definitions)
		pass

def recursive_import(tree, search_path):
	importer = VisitImporter(search_path)

	while importer.got_new:
		importer.new_imports.clear()
		importer.new_defs.clear()
		importer.new_children.clear()
		importer.got_new = False

		importer.visit(tree)

		tree.imports = importer.new_imports + tree.imports
		tree.definitions = importer.new_defs + tree.definitions
		tree.children = importer.new_children + [x for x in tree.children if not isinstance(x, CoreDSL2Parser.Import_fileContext)]


class VisitImporter(CoreDSL2Visitor):
	def __init__(self, search_path) -> None:
		super().__init__()
		self.imported = set()
		self.new_children = []
		self.new_imports = []
		self.new_defs = []
		self.got_new = True
		self.search_path = search_path

	def visitDescription_content(self, ctx: CoreDSL2Parser.Description_contentContext):
		for i in ctx.imports:
			self.visit(i)

	def visitImport_file(self, ctx: CoreDSL2Parser.Import_fileContext):
		filename = ctx.uri.text.replace('"', '')
		if filename not in self.imported:
			print(f"importing file {filename}")
			self.got_new = True
			self.imported.add(filename)

			parser = make_parser(self.search_path/filename)

			tree = parser.description_content()

			self.new_children.extend(tree.children)
			self.new_imports.extend(tree.imports)
			self.new_defs.extend(tree.definitions)
