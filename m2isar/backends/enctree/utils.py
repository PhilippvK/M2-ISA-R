from anytree import Node, RenderTree
from typing import Optional, Dict, Tuple
from pathlib import Path

from .plot import plot_space


# class VisitorContext:
#
#   def __init__(self):
#       self.data = {}
#       self.stack = []
#
#   def visit(self, node):
#       print("visit", node)
#       if node.is_selection:
#           # selected = node.selected
#           # self.selected = selected
#           pass
#       elif node.is_instruction:
#           pass
#       else:
#           if self.selected:
#               val = (node.match & node.parent.selected_mask) >> node.parent.selected[1]
#       for c in node.children:
#           self.visit(c)

class EncodingNode:
  def __init__(self, mask: Optional[int] = None, match: Optional[int] = None, selected: Optional[Tuple[int, int]] = None, size: Optional[int] = None, parent = None):
    self._size = size
    self._mask = mask
    self._match = match
    self._selected = selected
    self.parent = parent
    self.children = []
    self.is_instruction = False
    self.mappings = {}

  def __repr__(self):
    return self.bitstr

  @property
  def num_instrs(self):
      return sum(c.num_instrs for c in self.children)

  @property
  def is_selection(self):
      return self.selected_bits > 0

  def to_tree(self, parent=None):
    x = Node(str(self), parent=parent, ref=self)
    for c in self.children:
      c.to_tree(parent=x)
    return x

  @property
  def max_self(self):
      if self.parent:
          return self.space_size / self.parent.space_size
      return 1.0

  @property
  def sum_self(self):
      return sum(c.space_size for c in self.children) / self.space_size

  @property
  def sum_total(self):
      return sum(c.space_size for c in self.children) / (2**self.size)

  @property
  def used_self(self):
      return self.used / self.space_size

  @property
  def used_total(self):
      return self.used / (2**self.size)

  @property
  def used(self):
      return sum(c.used for c in self.children)

  @property
  def max_total(self):
      return self.space_size / (2**self.size)

  def render(self):
    for pre, fill, node in RenderTree(self.to_tree()):
      ref = node.ref
      temp = []
      temp.append(f"num_instrs={ref.num_instrs}")
      temp.append(f"fixed={ref.fixed_bits}")
      temp.append(f"variable={ref.variable_bits}")
      temp.append(f"space={ref.space_size}")
      temp.append(f"max_self={ref.max_self}")
      temp.append(f"max_total={ref.max_total}")
      temp.append(f"sum_self={ref.sum_self}")
      temp.append(f"sum_total={ref.sum_total}")
      temp.append(f"used_self={ref.used_self}")
      temp.append(f"used_total={ref.used_total}")
      suffix = ",".join(temp)
      print("%s%s [%s]" % (pre, node.name, suffix))

  # def plot_all(self, outpath, fmt="png"):
  def plot_all(self, outpath, fmt="pdf"):
    pass
    # TODO: traverse only (no render)
    # visitor = VisitorContext()
    # visitor.visit(self)
    # plot_data_map = visitor.data
    # print("plot_data_map", plot_data_map)
    # for pre, fill, node in RenderTree(self.to_tree()):
    #   ref = node.ref
    #   if ref.is_instruction:
    #       print("skip")
    #       continue
    #   if not ref.is_selection:
    #       print("skip2")
    #       continue
    #   fname = Path(outpath) / f"{node.name}.{fmt}"
    #   print("fname", fname)
    #   plot_data = []
    #   assert len(ref.children) > 0
    #   bits = ref.variable_bits
    #   print("bits", bits)
    #   field = ref.selected
    #   print("field", field)
    #   field_str = f"{field[0]}:{field[1]}"
    #   print("field_str", field_str)
    #   num = 2**(ref.selected_bits)
    #   print("num")
    #   values = list(range(num))
    #   print("values", values)
    #   values_str = [hex(x) for x in values]
    #   print("values_str", values_str)
    #   used_values = [((c.match & ref.selected_mask) >> field[1]) for c in ref.children]
    #   print("used_values", used_values)
    #   is_instrs = [c.is_instruction for c in ref.children]
    #   print("is_instrs", is_instrs)
    #   mappings = ref.mappings
    #   print("mappings", mappings)
    #   tmp = []
    #   # tmp = ref.parent
    #   # while tmp is not None:
    #   # plot_data = [
    #   #   (32, "1:0", [
    #   #       (25, 0, "0b00\n(compressed-0)", False),
    #   #       (25, 0, "0b01\n(compressed-1)", False),
    #   #       (25, 0, "0b10\n(compressed-2)", False),
    #   #       (25, 12.5, "11\n(uncompressed)", True)
    #   #   ]),
    #   #   (30, "6:2", [
    #   #       (3.125, 1.953125, "0x00\n(LOAD)", True),
    #   #       (3.125, 0, "0x01\n(LOAD-FP)", False),
    #   #       (3.125, 0, "0x02\n(custom-0)", False),
    #   #       (3.125, 0.390625, "0x03\n(MISC-MEM)", False),
    #   #       (3.125, 0, "0x04\n(OP-IMM)", False),
    #   #       (3.125, 0, "0x05\n(AUIPC)", False),
    #   #       (3.125, 0, "0x06\n(OP-IMM-32)", False),
    #   #       (3.125, 0, "0x07\n(48b)", False),
    #   #       (3.125, 0, "0x08\n(STORE)", False),
    #   #       (3.125, 0, "0x09\n(STORE-FP)", False),
    #   #       (3.125, 0, "0x0a\n(custom-1)", False),
    #   #       (3.125, 0, "0x0b\n(AMO)", False),
    #   #       (3.125, 0, "0x0c\n(OP)", False),
    #   #       (3.125, 0, "0x0d\n(LUI)", False),
    #   #       (3.125, 0, "0x0e\n(OP-32)", False),
    #   #       (3.125, 0, "0x0f\n(64b)", False),
    #   #       (3.125, 0, "0x10\n(MADD)", False),
    #   #       (3.125, 0, "0x11\n(MSUB)", False),
    #   #       (3.125, 0, "0x12\n(NMSUB)", False),
    #   #       (3.125, 0, "0x13\n(NMADD)", False),
    #   #       (3.125, 0, "0x14\n(OP-FP)", False),
    #   #       (3.125, 0, "0x15\n(OP-V)", False),
    #   #       (3.125, 0, "0x16\n(custom-2)", False),
    #   #       (3.125, 0, "0x17\n(48b)", False),
    #   #       (3.125, 0, "0x18\n(BRANCH)", False),
    #   #       (3.125, 0, "0x19\n(JALR)", False),
    #   #       (3.125, 0, "0x1a\n(reserved)", False),
    #   #       (3.125, 0, "0x1b\n(JAL)", False),
    #   #       (3.125, 0, "0x1c\n(SYSTEM)", False),
    #   #       (3.125, 0, "0x1d\n(reserved)", False),
    #   #       (3.125, 0, "0x1e\n(custom-3)", False),
    #   #       (3.125, 0, "0x1f\n(>=80b)", False),
    #   #   ]),
    #   #   (27, "15:12", [
    #   #       (12.5, 12.5, "0b000\n(lb)", False),
    #   #       (12.5, 12.5, "0b001\n(lh)", False),
    #   #       (12.5, 12.5, "0b010\n(lw)", False),
    #   #       (12.5, 0, "0b011", False),
    #   #       (12.5, 12.5, "0b100\n(lbu)", False),
    #   #       (12.5, 12.5, "0b101\n(lhu)", False),
    #   #       (12.5, 0, "0b110", False),
    #   #       (12.5, 0, "0b111", False),
    #   #   ]),
    #   # ]
    #   plot_space(fname, plot_data)
    #   input("123")

  @property
  def maskstr(self):
    return f"{self.mask:b}".zfill(self.size)

  @property
  def selectedstr(self):
    return f"{self.selected_mask:b}".zfill(self.size)

  @property
  def fixed_bits(self):
    return self.maskstr.count("1")

  @property
  def variable_bits(self):
    return self.maskstr.count("0")

  @property
  def selected_bits(self):
    if self.selected:
      return self.selected[0] - self.selected[1] + 1
    return 0

  @property
  def space_size(self):
    return 2**self.variable_bits

  @property
  def matchstr(self):
    return f"{self.match:b}".zfill(self.size)

  @property
  def bitstr(self):
    assert len(self.maskstr) == len(self.matchstr)
    temp = "".join(["-" if self.selectedstr[i] == "1" else (x if self.maskstr[i] == "1" else "?") for i, x in enumerate(self.matchstr)])
    return temp

  @property
  def mask(self):
    if self._mask is not None:
      return self._mask
    if self.parent:
      assert self.parent.mask is not None
      return self.parent.mask
    assert False

  @property
  def match(self):
    if self._match is not None:
      return self._match
    if self.parent:
      assert self.parent.match is not None
      return self.parent.match
    assert False

  @property
  def selected(self):
    if self._selected is not None:
      return self._selected
    # if self.parent:
    #   assert self.parent.selected is not None
    #   return self.parent.selected
    # assert False
    return None

  @property
  def selected_mask(self):
    if self.selected_bits == 0:
      return 0
    field = self.selected
    upper, lower = field
    assert upper >= lower
    length = upper - lower + 1
    temp = (2**length)-1
    temp <<= lower
    assert temp & self.mask == 0
    return temp

  @property
  def size(self):
    if self._size is not None:
      return self._size
    if self.parent:
      assert self.parent.size is not None
      return self.parent.size
    assert False

  def select(self, field: Tuple[int, int]):
    assert self.selected_bits == 0
    assert len(field) == 2
    new = EncodingNode(mask=self.mask, match=self.match, selected=field, size=self.size, parent=self)
    new.mapping = {**self.mappings}
    self.children.append(new)
    return new

  def choose(self, value: int):
    _, lower = self.selected
    length = self.selected_bits
    assert length > 0
    assert value < (2**length)
    temp = value << lower
    new = EncodingNode(mask=self.mask | self.selected_mask, match=self.match | temp, selected=None, size=self.size, parent=self)
    new.mappings = {**self.mappings, self.selected: value}
    self.children.append(new)
    return new

  def instruction(self, name: str):
    assert self.selected_bits == 0
    new = InstructionNode(name, mask=self.mask, match=self.match, size=self.size, parent=self)
    self.children.append(new)
    return new


class RootNode(EncodingNode):
  def __init__(self, size: int):
    super().__init__(size=size, mask=0, match=0, selected=None, parent=None)

class InstructionNode(EncodingNode):
  def __init__(self, name: str, mask: int, match: int, size: Optional[int] = None, parent: Optional[EncodingNode] = None):
    super().__init__(size=size, mask=mask, match=match, selected=None, parent=parent)
    self.name = name
    self.is_instruction = True

  @property
  def num_instrs(self):
      return 1

  @property
  def max_self(self):
      assert self.parent
      return self.parent.max_self

  @property
  def used(self):
      return self.space_size

  def __repr__(self):
    return f"{self.name}({self.bitstr})"


class EncondingTree:
  def __init__(self, root: EncodingNode):
    self.root = root
