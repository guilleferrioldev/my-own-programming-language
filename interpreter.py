from constants import * 
from error import RunTimeError
import os, math

###########################################
# RUNTIME result
###########################################

class RuntimeResult:
	def __init__(self):
		self.reset()
		
	def reset(self):
		self.value = None
		self.error = None
		self.func_return_value = None
		self.loop_should_continue = False
		self.loop_should_break = False
		
	def register(self, res):
		self.error = res.error
		self.func_return_value = res.func_return_value
		self.loop_should_continue = res.loop_should_continue
		self.loop_should_break = res.loop_should_break
		return res.value

	def register(self, response):
		self.error = response.error
		return response.value

	def success(self, value):
		self.value = value
		return self
		
	def success_return(self, value):
		self.reset()
		self.func_return_value = value
		return self
		
	def success_continue(self):
		self.reset()
		self.loop_should_continue = True
		return self
	
	def success_break(self):
		self.reset()
		self.loop_should_break = True
		return self
	
	def failure(self, error):
		self.reset()
		self.error = error
		return self
	
	def should_return(self):
		# Note: this will allow you to continue and break outside the current function
		return (self.error or self.func_return_value or self.loop_should_continue or self.loop_should_break )


###########################################
# VALUES
###########################################

class Value:
	def __init__(self):
		self.set_position()
		self.set_context()

	def set_position(self, position_start=None, position_end=None):
		self.position_start = position_start
		self.position_end = position_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		return None, self.illegal_operation(other)

	def subbed_by(self, other):
		return None, self.illegal_operation(other)

	def multed_by(self, other):
		return None, self.illegal_operation(other)

	def dived_by(self, other):
		return None, self.illegal_operation(other)

	def powed_by(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_eq(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_ne(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lte(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gte(self, other):
		return None, self.illegal_operation(other)

	def anded_by(self, other):
		return None, self.illegal_operation(other)

	def ored_by(self, other):
		return None, self.illegal_operation(other)

	def notted(self):
		return None, self.illegal_operation(other)

	def execute(self, arguments):
		return RuntimeResult().failure(self.illegal_operation())

	def copy(self):
		raise Exception('No copy method defined')

	def is_true(self):
		return False

	def illegal_operation(self, other=None):
		if not other: other = self
		return RunTimeError(
			self.position_start, other.position_end,
			'Illegal operation',
			self.context
		)

class Number(Value):
	def __init__(self, value):
		Value.__init__(self)
		self.value = value
		self.error = None

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RunTimeError(other.position_start, other.position_end,'Division by zero',self.context)

			return Number(self.value / other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_eq(self, other):
		if isinstance(other, Number):
			return Number(self.value == other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_ne(self, other):
		if isinstance(other, Number):
			return Number(self.value != other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lt(self, other):
		if isinstance(other, Number):
			return Number(self.value < other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gt(self, other):
		if isinstance(other, Number):
			return Number(self.value > other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lte(self, other):
		if isinstance(other, Number):
			return Number(self.value <= other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gte(self, other):
		if isinstance(other, Number):
			return Number(self.value >= other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def anded_by(self, other):
		if isinstance(other, Number):
			return Number(self.value and other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def ored_by(self, other):
		if isinstance(other, Number):
			return Number(self.value or other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def notted(self):
		return Number(1 if self.value == 0 else 0).set_context(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.set_position(self.position_start, self.position_end)
		copy.set_context(self.context)
		return copy

	def is_true(self):
		return self.value != 0
	
	def __repr__(self):
		return str(self.value)

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_pi = Number(math.pi)

class String(Value):
	def __init__(self, value):
		Value.__init__(self)  
		self.value = value
		self.error = None

	def added_to(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).set_context(self.context), None
		else:
			None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).set_context(self.context), None
		else:
			None, Value.illegal_operation(self, other)

	def is_true(self):
		return len(self.value) > 0

	def copy(self):
		copy = String(self.value)
		copy.set_position(self.position_start, self.position_end)
		copy.set_context(self.context)
		return copy

	def __repr__(self):
		return f'"{self.value}"'

class List(Value):
	def __init__(self, elements):
		Value.__init__(self)
		self.elements = elements

	def added_to(self, other):
		if isinstance(other, List):
			new_list = self.copy()
			new_list.elements.extend(other.elements)
			return new_list, None
		else:
			None, Value.illegal_operation(self, other)

	def get_comparison_lte(self, other):
		new_list = self.copy()
		new_list.elements.append(other)
		return new_list, None

	def subbed_by(self, other):
		if isinstance(other, Number):
			new_list = self.copy()
			try:
				new_list.elements.pop(other)
				return new_list, None
			except:
				return None , RunTimeError(other.position_start, other.position_end, 
											"Element at this index could not be removed from list because index is out of bounds", self.context)
		else:
			None, Value.illegal_operation(self, other)

	def dived_by(self, other):
		if isinstance(other, Number):
			try:
				return self.elements[other.value], None
			except:
				return None , RunTimeError(other.position_start, other.position_end, 
											"Element at this index could not be retrieved from list because index is out of bounds", self.context)
		else:
			None, Value.illegal_operation(self, other)

	def copy(self):
		copy = List(self.elements)
		copy.set_context(self.context)
		copy.set_position(self.position_start, self.position_end)
		return copy

	def __repr__(self):
		return f"[{','.join([str(x) for x in self.elements])}]"

class BaseFunction(Value):
	def __init__(self, name, error=None):
		Value.__init__(self)
		self.name = name or "<anonymous>"

	def generate_new_context(self):
		new_context = Context(self.name, self.context, self.position_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
		return new_context

	def check_arguments(self, argument_names, arguments):
		response = RuntimeResult()

		if len(arguments) > len(argument_names):
			return response.failure(RunTimeError(self.position_start, self.position_end,
												f"{len(arguments) - len(argument_names)} too many arguments passed into '{self.name}'",self.context))
		
		if len(arguments) < len(argument_names):
			return response.failure(RunTimeError(self.position_start, self.position_end, 
												f"{len(argument_names) - len(arguments)} too few arguments passed into '{self.name}'", self.context))

		return response.success(None)

	def populate_arguments(self, argument_names, arguments, execution_context):
		for i in range(len(arguments)):
			argument_name = argument_names[i]
			argument_value = arguments[i]
			argument_value.set_context(execution_context)
			execution_context.symbol_table.set(argument_name, argument_value)

	def check_and_populate_arguments(self, argument_names, arguments, execution_context):
		response = RuntimeResult()

		response.register(self.check_arguments(argument_names, arguments))
		if response.should_return():
			 return response

		self.populate_arguments(argument_names, arguments, execution_context)
		return response.success(None)

class Function(BaseFunction):
	def __init__(self, name, body_node, argument_names, should_auto_return):
		BaseFunction.__init__(self, name)
		self.body_node = body_node
		self.argument_names = argument_names
		self.should_auto_return = should_auto_return

	def execute(self, arguments):
		response = RuntimeResult()
		interpreter = Interpreter()
		execution_context = self.generate_new_context()

		response.register(self.check_and_populate_arguments(self.argument_names, arguments, execution_context))
		if response.should_return():
			 return response
		
		value = response.register(interpreter.visit(self.body_node, execution_context))
		if response.should_return() and response.func_return_value == None: 
			return response
		
		return_value = (value if self.should_auto_return else None) or response.func_return_value or Number.null
		
		return response.success(return_value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.argument_names, self.should_auto_return)
		copy.set_context(self.context)
		copy.set_position(self.position_start, self.position_end)
		return copy

	def __repr__(self):
		return f"<function {self.name}>"          

class BuiltInFunction(BaseFunction):
	def __init__(self, name):
		BaseFunction.__init__(self, name)

	def execute(self, arguments):
		response = RuntimeResult()
		execution_context = self.generate_new_context()

		method_name = f"execute_{self.name}"
		method = getattr(self, method_name, self.no_visit_method)

		response.register(self.check_and_populate_arguments(method.argument_names, arguments, execution_context))
		if response.should_return(): 
			return response

		return_value = response.register(method(execution_context))
		if response.should_return(): 
			return response
		return return_value

	def no_visit_method(self, node, context):
		raise Exception(f'No execute_{type(node).__name__} method defined')

	def copy(self):
		copy = BuiltInFunction(self.name)
		copy.set_context(self.context)
		copy.set_position(self.position_start, self.position_end)
		return copy

	def __repr__(self):
		return f"<built-in function {self.name}>"  
   
    ############################################## 
	def execute_print(self, execute_context):
		return RuntimeResult().success(String(execute_context.symbol_table.get("value")))
	execute_print.argument_names = ["value"]

	def execute_input(self, execute_context):
		while True:
			text = input()
			try:
				number = int(text)
				return RuntimeResult().success(Number(number))
			except ValueError:
				return RuntimeResult().success(String(text))
	execute_input.argument_names = []

	def execute_clear(self, execute_context):
		os.system('cls' if os.name == 'nt' else 'clear')
		return  RuntimeResult().success(Number.null)
	execute_clear.argument_names = []

	def execute_is_number(self, execute_context):
		is_number = isinstance(execute_context.symbol_table.get("value"), Number)
		return RuntimeResult().success(Number.true if is_number else Number.false)
	execute_is_number.argument_names = ["value"]

	def execute_is_string(self, execute_context):
		is_string = isinstance(execute_context.symbol_table.get("value"), String)
		return RuntimeResult().success(Number.true if is_string else Number.false)
	execute_is_string.argument_names = ["value"]

	def execute_is_list(self, execute_context):
		is_list = isinstance(execute_context.symbol_table.get("value"), List)
		return RuntimeResult().success(Number.true if is_list else Number.false)
	execute_is_list.argument_names = ["value"]

	def execute_is_function(self, execute_context):
		is_function = isinstance(execute_context.symbol_table.get("value"), BaseFunction)
		return RuntimeResult().success(Number.true if is_function else Number.false)
	execute_is_function.argument_names = ["value"]

	def execute_append(self, execute_context):
		list_ = execute_context.symbol_table.get('list')
		value = execute_context.symbol_table.get('value')

		if not isinstance(list_, List):
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end, "First argument must be a list", execute_context))

		list_.elements.append(value) 
		return RuntimeResult().success(Number.null)
	execute_append.argument_names = ["list", "value"]

	def execute_pop(self, execute_context):
		list_ = execute_context.symbol_table.get('list')
		index = execute_context.symbol_table.get('index')

		if not isinstance(list_, List):
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end, "First argument must be a list", execute_context))
		
		if not isinstance(index, Number):
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end, "First argument must be a number", execute_context))

		try:
			element = list_.elements.pop(index.value)
		except:
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end, 
											"Elements at this index could not be removed from list because index is out of range", execute_context))
		
		return RuntimeResult().success(element)
	execute_pop.argument_names = ["list", "index"]
	
	def execute_len(self, execute_context):
		list_ = execute_context.symbol_table.get("list")
		
		if not isinstance(list_, List):
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end,"Argument must be list",execute_context))
			
		return RuntimeResult().success(Number(len(list_.elements)))
	execute_len.arg_names = ["list"]
	
	def execute_run(self, execute_context):
		fn = execute_context.symbol_table.get("fn")
		
		if not isinstance(fn, String):
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end,"Second argument must be string",execute_context))
			
		fn = fn.value
		try:
			with open(fn, "r") as f:
				script = f.read()
		except Exception as e:
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end,f"Failed to load script \"{fn}\"\n" + str(e),execute_context))
			
		_, error = run(fn, script)
		
		if error:
			return RuntimeResult().failure(RunTimeError(self.position_start, self.position_end,f"Failed to finish executing script \"{fn}\"\n" + error.as_string(), execute_context))
			
		return RuntimeResult().success(Number.null)
	execute_run.arg_names = ["fn"]

BuiltInFunction.print            =  BuiltInFunction("print")
BuiltInFunction.input            =  BuiltInFunction("input")
BuiltInFunction.clear            =  BuiltInFunction("clear")
BuiltInFunction.is_number        =  BuiltInFunction("is_number")
BuiltInFunction.is_string        =  BuiltInFunction("is_string")
BuiltInFunction.is_list          =  BuiltInFunction("is_list")
BuiltInFunction.is_function      =  BuiltInFunction("is_function")
BuiltInFunction.append           =  BuiltInFunction("append")
BuiltInFunction.pop              =  BuiltInFunction("pop")

###########################################
# CONTEXT
###########################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_position=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_position = parent_entry_position
		self.symbol_table = None


###########################################
# SYMBOL TABLE
###########################################

class SymbolTable:
	def __init__(self, parent=None):
		self.symbols = {}
		self.parent = parent

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]


###########################################
# INTERPRETER
###########################################

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	###################################

	def visit_NumberNode(self, node, context):
		return RuntimeResult().success(Number(node.token.value).set_context(context).set_position(node.position_start, node.position_end))
	
	def visit_StringNode(self, node, context):
		return RuntimeResult().success(String(node.token.value).set_context(context).set_position(node.position_start, node.position_end))

	def visit_ListNode(self, node, context):
		response = RuntimeResult()
		elements = []

		for element_node in node.element_nodes:
			elements.append(response.register(self.visit(element_node, context)))
			if response.should_return():
			 	return response
		
		return response.success(List(elements).set_context(context).set_position(node.position_start, node.position_end))

	def visit_VarAccessNode(self, node, context):
		response = RuntimeResult()
		variable_name = node.variable_name_token.value
		value = context.symbol_table.get(variable_name)

		if not value:
			return response.failure(RunTimeError(node.position_start, node.position_end,f"'{variable_name}' is not defined", context))

		value = value.copy().set_position(node.position_start, node.position_end).set_context(context)
		return response.success(value)

	def visit_VariableAssignamentNode(self, node, context):
		response = RuntimeResult()
		variable_name = node.variable_name_token.value
		value = response.register(self.visit(node.value_node, context))
		if response.should_return(): 
			return response

		context.symbol_table.set(variable_name, value)
		return response.success(value)

	def visit_BinaryOperationNode(self, node, context):
		response = RuntimeResult()
		left = response.register(self.visit(node.left_node, context))
		if response.should_return():
			 return response
		right = response.register(self.visit(node.right_node, context))
		if response.should_return(): 
			return response

		if node.operation_token.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.operation_token.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.operation_token.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.operation_token.type == TT_DIV:
			result, error = left.dived_by(right)
		elif node.operation_token.type == TT_POW:
			result, error = left.powed_by(right)
		elif node.operation_token.type == TT_EE:
			result, error = left.get_comparison_eq(right)
		elif node.operation_token.type == TT_NE:
			result, error = left.get_comparison_ne(right)
		elif node.operation_token.type == TT_LT:
			result, error = left.get_comparison_lt(right)
		elif node.operation_token.type == TT_GT:
			result, error = left.get_comparison_gt(right)
		elif node.operation_token.type == TT_LTE:
			result, error = left.get_comparison_lte(right)
		elif node.operation_token.type == TT_GTE:
			result, error = left.get_comparison_gte(right)
		elif node.operation_token.matches(TT_KEYWORD, 'and'):
			result, error = left.anded_by(right)
		elif node.operation_token.matches(TT_KEYWORD, 'or'):
			result, error = left.ored_by(right)

		if error:
			return response.failure(error)
		else:
			return response.success(result.set_position(node.position_start, node.position_end))

	def visit_UnaryOperationNode(self, node, context):
		response = RuntimeResult()
		number = response.register(self.visit(node.node, context))
		if response.should_return():
			 return response

		error = None

		if node.operation_token.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))
		elif node.operation_token.matches(TT_KEYWORD, 'not'):
			number, error = number.notted()

		if error:
			return response.failure(error)
		else:
			return response.success(number.set_position(node.position_start, node.position_end))

	def visit_IfNode(self, node, context):
		response = RuntimeResult()

		for condition, expression, should_return_null in node.cases:
			condition_value = response.register(self.visit(condition, context))
			if response.should_return(): 
				return response

			if condition_value.is_true():
				expression_value = response.register(self.visit(expression, context))
				if response.should_return():
					 return response
				return response.success(Number.null if should_return_null else expression_value)

		if node.else_case:
			expression, should_return_null = node.else_case
			else_value = response.register(self.visit(expression, context))
			if response.should_return(): 
				return response
			return response.success(Number.null if should_return_null else else_value)

		return response.success(Number.null)

	def visit_ForNode(self, node, context):
		response = RuntimeResult()
		elements = []

		start_value = response.register(self.visit(node.start_value_node, context))
		if response.should_return():
			 return response

		end_value = response.register(self.visit(node.end_value_node, context))
		if response.should_return(): 
			return response

		if node.step_value_node:
			step_value = response.register(self.visit(node.step_value_node, context))
			if response.should_return(): 
				return response
		else:
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value
		else:
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.variable_name_token.value, Number(i))
			i += step_value.value

			value = response.register(self.visit(node.body_node, context))
			if response.should_return() and response.loop_should_continue == False and response.loop_should_break == False: 
				return response

			if response.loop_should_continue:
				continue

			if response.loop_should_break:
				break

			elements.append(value)

		return response.success(Number.null if node.should_return_null else elements[-1])
								# List(elements).set_context(context).set_position(node.position_start, node.position_end))

	def visit_WhileNode(self, node, context):
		response = RuntimeResult()
		elements = []

		while True:
			condition = response.register(self.visit(node.condition_node, context))
			if response.should_return(): 
				return response

			if not condition.is_true(): break

			value = response.register(self.visit(node.body_node, context))
			if response.should_return() and response.loop_should_continue == False and response.loop_should_break == False: 
				return response

			if response.loop_should_continue:
				continue

			if response.loop_should_break:
				break

			elements.append(value)

		return response.success(Number.null if node.should_return_null else elements[-1])
								#List(elements).set_context(context).set_position(node.position_start, node.position_end))

	def visit_FunctionNode(self, node, context):
		response = RuntimeResult()

		func_name = node.variable_name_token.value if node.variable_name_token else None
		body_node = node.body_node
		argument_names = [argument_name.value for argument_name in node.argument_name_tokens]
		func_value = Function(func_name, body_node, argument_names, node.should_auto_return).set_context(context).set_position(node.position_start, node.position_end)
		
		if node.variable_name_token:
			context.symbol_table.set(func_name, func_value)

		return response.success(func_value)

	def visit_CallNode(self, node, context):
		response = RuntimeResult()
		arguments = []

		value_to_call = response.register(self.visit(node.node_to_call, context))
		if response.should_return(): 
			return response
		value_to_call = value_to_call.copy().set_position(node.position_start, node.position_end)

		for arg_node in node.argument_nodes:
			arguments.append(response.register(self.visit(arg_node, context)))
			if response.should_return(): 
				return response

		return_value = response.register(value_to_call.execute(arguments))
		if response.should_return():
			 return response
		
		return response.success(return_value)

	def visit_ReturnNode(self, node, context):
		response = RuntimeResult()
		
		if node.node_to_return:
			value = response.register(self.visit(node.node_to_return, context))
			if response.should_return(): 
				return response
		else:
			value = Number.null 
		
		return response.success_return(value)
		
	def visit_ContinueNode(self, node, context):
		return RuntimeResult().success_continue()
		
	def visit_BreakNode(self, node, context):
		return RuntimeResult().success_break()