grammar CoreDSL2;

description_content
	: imports+=import_file* definitions+=isa+
	;

import_file
	: 'import' uri=STRING
	;

isa
	: instruction_set
	| core_def
	;

instruction_set
	: 'InstructionSet' name=IDENTIFIER ('extends' extension+=IDENTIFIER (',' extension+=IDENTIFIER)*)? '{' sections+ '}'
	;

core_def
	: 'Core' name=IDENTIFIER ('provides' contributing_types+=IDENTIFIER (',' contributing_types+=IDENTIFIER)*)? '{' sections* '}'
	;

sections
	: section_arch_state
	| section_functions
	| section_instructions
	;

section_arch_state
	: 'architectural_state' '{' declarations+=decl_or_expr+ '}'
	;

decl_or_expr
	: declaration
	| expression ';'
	;

section_functions
	: 'functions' '{' functions+=function_definition+ '}'
	;

section_instructions
	: 'instructions' attributes+=attribute* '{' instructions+=instruction+ '}'
	;

instruction
	: name=IDENTIFIER attributes+=attribute* '{'
	'encoding' ':' encoding=rule_encoding';'
	('args_disass' ':' disass=STRING ';')?
	'behavior' ':' behavior=statement
	'}'
	;

rule_encoding
	: fields+=field ('::' fields+=field)*
	;

field
	: bit_value
	| bit_field
	;

bit_value
	: value=INTEGER
	;

bit_field
	: name=IDENTIFIER LEFT_BR left=integer_constant ':' right=integer_constant RIGHT_BR
	;

function_definition
	: 'extern' type_=type_specifier name=IDENTIFIER '(' parameter_list? ')' ';' # extern_function_definition
	| type_=type_specifier name=IDENTIFIER '(' parameter_list? ')' attributes+=attribute* behavior=block # intern_function_definition
	;

parameter_list
	: params+=parameter_declaration (',' params+=parameter_declaration)*
	;

parameter_declaration
	: type_=type_specifier declarator=direct_or_abstract_declarator?
	;

direct_or_abstract_declarator
	: direct_declarator
	| direct_abstract_declarator
	;

statement
	: block
	| type_='if' '(' cond=expression ')' then_stmt=statement ('else' else_stmt=statement)?
	| type_='for' '(' for_condition ')' stmt=statement
	| type_='while' '(' cond=expression ')' stmt=statement
	| type_='do' stmt=statement 'while' '(' cond=expression ')' ';'
	| type_='switch' '(' cond=expression ')' '{' items+=switch_block_statement_group* switch_label* '}'
	| type_='return' expr=expression? ';'
	| type_='break' ';'
	| type_='continue' ';'
	| type_='spawn' stmt=statement
	| expr=expression ';'
	;

switch_block_statement_group
	: labels+=switch_label+ statements+=statement+
	;

switch_label
	: 'case' const_expr=expression ':'
	| 'default' ':'
	;

block
	: '{' items+=block_item* '}'
	;

block_item
	: statement
	| declaration
	;

for_condition
	: (start_decl=declaration | start_expr=expression? ';')
	  end_expr=expression? ';'
	  (loop_exprs+=expression (',' loop_exprs+=expression)*)?
	;

declaration
	: (storage+=storage_class_specifier | qualifiers+=type_qualifier | attributes+=attribute)*
	  type_=type_specifier ptr=('*' | '&')?
	  (init+=init_declarator (',' init+=init_declarator)*)? ';'
	;

declarationSpecifier
	: storage_class_specifier
	| type_qualifier
	| attribute
	;

attribute
	: double_left_bracket type_=attribute_name ('=' value=expression)? double_right_bracket
	;

type_specifier
	: primitive_type
	| composite_type
	| enum_type
	;

primitive_type
	: data_type=data_types+ bit_size=bit_size_specifier?
	;

bit_size_specifier
	: '<' size+=primary_expression (',' size+=primary_expression ',' size+=primary_expression ',' size+=primary_expression)? '>'
	;

enum_type
	: 'enum' name=IDENTIFIER? '{' enumerator_list ','? '}'
	| 'enum' name=IDENTIFIER
	;

enumerator_list
	: enumerators+=enumerator (',' enumerators+=enumerator)*
	;

enumerator
	: name=IDENTIFIER
	| name=IDENTIFIER '=' expression
	;

composite_type
	: type_=struct_or_union name=IDENTIFIER? '{' declarations+=struct_declaration* '}'
	| type_=struct_or_union name=IDENTIFIER
	;

struct_declaration
	: specifier=struct_declaration_specifier declarators+=direct_declarator(',' declarators+=direct_declarator)* ';'
	;

struct_declaration_specifier
	: type_=type_specifier
	| qualifiers+=type_qualifier
	;

init_declarator
	: declarator=direct_declarator attributes=attribute* ('=' init=initializer)?
	;

direct_declarator
	: name=IDENTIFIER (':' index=integer_constant)?
	  ((LEFT_BR size+=expression RIGHT_BR)+ | '(' parameter_list ')')?
	;

initializer
	: expr=expression
	| '{' initializerList ','? '}'
	;

initializerList
	: init+=designated_or_not (',' init+=designated_or_not)*
	;

designated_or_not
	: designated_initializer
	| initializer
	;

designated_initializer
	: designators+=designator+ '=' init=initializer
	;

designator
	: LEFT_BR idx=expression RIGHT_BR
	| '.' prop=IDENTIFIER
	;

direct_abstract_declarator
	: '(' (decl=direct_abstract_declarator? | parameter_list) ')'
	| LEFT_BR expr=expression? RIGHT_BR
	;

expression_list
	: expressions+=expression (',' expressions+=expression)*
	;

expression
	: primary_expression #primary
	| bop=('.' | '->') ref=IDENTIFIER #deref_expression
	| expression bop='[' expression (':' expression)? ']' #slice_expression
	| ref=IDENTIFIER '(' (args+=expression (',' args+=expression)*)? ')' 		#method_call
	| expression postfix=('++' | '--') #postfix_expression
    | prefix=('&'|'*'|'+'|'-'|'++'|'--') expression #prefix_expression
    | prefix=('~'|'!') expression #prefix_expression
	| '('type_=type_specifier ')' expression 								#cast_expression
    | expression bop=('*'|'/'|'%') expression #binary_expression
    | expression bop=('+'|'-') expression #binary_expression
    | expression bop=('<<' | '>>') expression #binary_expression
    | expression bop=('<=' | '>=' | '>' | '<') expression #binary_expression
    | expression bop=('==' | '!=') expression #binary_expression
    | expression bop='&' expression #binary_expression
    | expression bop='^' expression #binary_expression
    | expression bop='|' expression #binary_expression
    | expression bop='&&' expression #binary_expression
    | expression bop='||' expression #binary_expression
	| expression bop='::' expression #binary_expression
    | <assoc=right> expression bop='?' expression ':' expression #conditional_expression
	| <assoc=right> expression bop=('=' | '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '^=' | '>>=' | '>>>=' | '<<=' | '%=') expression #assignment_expression
	;


primary_expression
	: ref=IDENTIFIER
	| const_expr=constant
	| literal+=string_literal+
	| '(' expression ')'
	;

string_literal
	: ENCSTRINGCONST
	| STRING
	;

constant
	: integer_constant
	| floating_constant
	| character_constant
	| bool_constant
	;

integer_constant
	: value=INTEGER
	;

floating_constant
	: value=FLOAT
	;

bool_constant
	: value=BOOLEAN
	;

character_constant
	: value=CHARCONST
	;

double_left_bracket
	: LEFT_BR LEFT_BR
	;

double_right_bracket
	: RIGHT_BR RIGHT_BR
	;

data_types
	: 'bool'
	| 'char'
	| 'short'
	| 'int'
	| 'long'
	| 'signed'
	| 'unsigned'
	| 'float'
	| 'double'
	| 'void'
	| 'alias'
	;

type_qualifier
	: 'const'
	| 'volatile'
	;

storage_class_specifier
	: 'extern'
	| 'static'
	| 'register'
	;

attribute_name
	: 'NONE'
	| 'is_pc'
	| 'is_interlock_for'
	| 'do_not_synthesize'
	| 'enable'
	| 'no_cont'
	| 'cond'
	| 'flush'
	;

struct_or_union
	: 'struct'
	| 'union'
	;

LEFT_BR: '[';
RIGHT_BR: ']';

BOOLEAN: ('true'|'false');
FLOAT: ('0'..'9')+ '.' ('0'..'9')* (('e'|'E') ('+'|'-')? ('0'..'9')+)? ('f'|'F'|'l'|'L')?;
INTEGER: (BINARYINT|HEXADECIMALINT|OCTALINT|DECIMALINT|VLOGINT) ('u'|'U')? (('l'|'L') ('l'|'L')?)?;

fragment BINARYINT: ('0b'|'0B') '0'..'1' ('_'? '0'..'1')*;
fragment OCTALINT: '0' '_'? '0'..'7' ('_'? '0'..'7')*;
fragment DECIMALINT: ('0'|'1'..'9' ('_'? '0'..'9')*);
fragment HEXADECIMALINT: ('0x'|'0X') ('0'..'9'|'a'..'f'|'A'..'F') ('_'? ('0'..'9'|'a'..'f'|'A'..'F'))*;
fragment VLOGINT: ('0'..'9')+ '\'' ('b' ('0'..'1')+|'o' ('0'..'7')+|'d' ('0'..'9')+|'h' ('0'..'9'|'a'..'f'|'A'..'F')+);

IDENTIFIER: '^'? ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;

CHARCONST: ('u'|'U'|'L')? '\'' ('\\' .|~('\\'|'\''))* '\'';
ENCSTRINGCONST: ('u8'|'u'|'U'|'L') '"' ('\\' .|~('\\'|'"'))* '"';
STRING: ('"' ('\\' .|~('\\'|'"'))* '"'|'\'' ('\\' .|~('\\'|'\''))* '\'');

ML_COMMENT: '/*' .*?'*/' -> skip;
SL_COMMENT: '//' ~('\n'|'\r')* ('\r'? '\n')? -> skip;
WS: (' '|'\t'|'\r'|'\n')+ -> skip;
