from constants import *
from error import InvalidSyntaxError
from typing import Self

###########################################
# NODES
###########################################

class NumberNode:
	def __init__(self, token):
		self.token = token

		self.position_start = self.token.position_start
		self.position_end = self.token.position_end

	def __repr__(self):
		return f'{self.token}'

class StringNode:
	def __init__(self, token):
		self.token = token

		self.position_start = self.token.position_start
		self.position_end = self.token.position_end

	def __repr__(self):
		return f'{self.token}'

class ListNode:
	def __init__(self, element_nodes, position_start, position_end):
		self.element_nodes = element_nodes

		self.position_start = position_start
		self.position_end = position_end

class VarAccessNode:
	def __init__(self, variable_name_token):
		self.variable_name_token = variable_name_token

		self.position_start = self.variable_name_token.position_start
		self.position_end = self.variable_name_token.position_end

class VariableAssignamentNode:
	def __init__(self, variable_name_token, value_node):
		self.variable_name_token = variable_name_token
		self.value_node = value_node

		self.position_start = self.variable_name_token.position_start
		self.position_end = self.value_node.position_end

class BinaryOperationNode:
	def __init__(self, left_node, operation_token, right_node):
		self.left_node = left_node
		self.operation_token = operation_token
		self.right_node = right_node

		self.position_start = self.left_node.position_start
		self.position_end = self.right_node.position_end

	def __repr__(self):
		return f'({self.left_node}, {self.operation_token}, {self.right_node})'

class UnaryOperationNode:
	def __init__(self, operation_token, node):
		self.operation_token = operation_token
		self.node = node

		self.position_start = self.operation_token.position_start
		self.position_end = node.position_end

	def __repr__(self):
		return f'({self.operation_token}, {self.node})'

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.position_start = self.cases[0][0].position_start
		self.position_end = (self.else_case or self.cases[len(self.cases) - 1])[0].position_end

class ForNode:
	def __init__(self, variable_name_token, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
		self.variable_name_token = variable_name_token
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.position_start = self.variable_name_token.position_start
		self.position_end = self.body_node.position_end

class WhileNode:
	def __init__(self, condition_node, body_node, should_return_null):
		self.condition_node = condition_node
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.position_start = self.condition_node.position_start
		self.position_end = self.body_node.position_end

class FunctionNode:
	def __init__(self, variable_name_token, argument_name_tokens, body_node, should_auto_return):
		self.variable_name_token = variable_name_token
		self.argument_name_tokens = argument_name_tokens
		self.body_node = body_node
		self.should_auto_return = should_auto_return

		if self.variable_name_token:
			self.position_start = self.variable_name_token.position_start
		elif len(self.argument_name_tokens) > 0:
			self.position_start = self.argument_name_tokens[0].position_start
		else:
			self.position_start = self.body_node.position_start

		self.position_end = self.body_node.position_end

class CallNode:
	def __init__(self, node_to_call, argument_nodes):
		self.node_to_call = node_to_call
		self.argument_nodes = argument_nodes

		self.position_start = self.node_to_call.position_start

		if len(self.argument_nodes) > 0:
			self.position_end = self.argument_nodes[len(self.argument_nodes) - 1].position_end
		else:
			self.position_end = self.node_to_call.position_end

class ReturnNode:
  def __init__(self, node_to_return, position_start, position_end):
    self.node_to_return = node_to_return

    self.position_start = position_start
    self.position_end = position_end

class ContinueNode:
  def __init__(self, position_start, position_end):
    self.position_start = position_start
    self.position_end = position_end

class BreakNode:
  def __init__(self, position_start, position_end):
    self.position_start = position_start
    self.position_end = position_end

###########################################
# PARSER RESULT
###########################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.last_registered_advance_count = 0
		self.advance_count = 0
		self.to_reverse_count = 0

	def register_advancement(self):
		self.last_registered_advance_count = 1
		self.advance_count += 1

	def register(self, response):
		self.last_registered_advance_count = response.advance_count
		self.advance_count += response.advance_count
		if response.error:
			 self.error = response.error
		return response.node

	def try_register(self, response):
		if response.error:
			self.to_reverse_count = response.advance_count
			return  None
		return self.register(response)

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.last_registered_advance_count == 0:
			self.error = error
		return self

###########################################
# PARSER
###########################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.token_index = -1
		self.advance()

	def advance(self):
		self.token_index += 1
		self.update_current_token()
		return self.current_token

	def reverse(self, amount=1):
		self.token_index -= amount
		self.update_current_token()
		return self.current_token
	
	def update_current_token(self):
		if self.token_index >= 0 and self.token_index < len(self.tokens):
			self.current_token = self.tokens[self.token_index]

	def parse(self):
		response = self.statements()
		if not response.error and self.current_token.type != TT_EOF:
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
														"Token cannot appear after previous tokens"))
		return response

	###################################
	
	def statements(self):
		response = ParseResult()
		statements = []
		position_start = self.current_token.position_start.copy()

		while self.current_token.type == TT_NEWLINE:
			response.register_advancement()
			self.advance()

		statement = response.register(self.statement())
		if response.error:
				 return response
		statements.append(statement)

		more_statements = True

		while True:
			newline_count = 0
			while self.current_token.type == TT_NEWLINE:
				response.register_advancement()
				self.advance()
				newline_count += 1
			if newline_count == 0:
				more_statements = False
		
			if not more_statements:
				break
			
			statement = response.try_register(self.statement())
			if not statement:
				self.reverse(response.to_reverse_count)
				more_statements = False  
				continue

			statements.append(statement)

		return response.success(ListNode(statements, position_start, self.current_token.position_end.copy()))

	def statement(self):
		response = ParseResult()
		position_start = self.current_token.position_start.copy()

		if self.current_token.matches(TT_KEYWORD, "return"):
			response.register_advancement()
			self.advance()

			expression = response.try_register(self.expression())
			if not expression:
				self.reverse(response.to_reverse_count)
			return response.success(ReturnNode(expression, position_start, self.current_token.position_end.copy()))

		if self.current_token.matches(TT_KEYWORD, "continue"):
			response.register_advancement()
			self.advance()
			return response.success(ContinueNode(position_start, self.current_token.position_end.copy()))

		if self.current_token.matches(TT_KEYWORD, "break"):
			response.register_advancement()
			self.advance()
			return response.success(BreakNode(position_start, self.current_token.position_end.copy()))

		expression = response.register(self.expression())
		if response.error:
				 return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
					"Expected 'return', 'continue', 'break', 'let', 'if', 'for', 'while', 'fn', int, float, identifier, '+', '-', '(', '[' or 'not'"))

		return response.success(expression)

	def expression(self):
		response = ParseResult()

		if self.current_token.matches(TT_KEYWORD, 'let'):
			response.register_advancement()
			self.advance()

			if self.current_token.type != TT_IDENTIFIER:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, "Expected identifier"))

			variable_name = self.current_token
			response.register_advancement()
			self.advance()

			if self.current_token.type != TT_EQ:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,"Expected '='"))

			response.register_advancement()
			self.advance()
			expression = response.register(self.expression())
			if response.error:
				 return response
			return response.success(VariableAssignamentNode(variable_name, expression))

		node = response.register(self.binary_operation(self.comparation_expression, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

		if response.error:
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
														"Expected 'let', 'if', 'for', 'while', 'fn', int, float, identifier, '+', '-', '(', '[' or 'not'"))

		return response.success(node)

	def comparation_expression(self):
		response = ParseResult()

		if self.current_token.matches(TT_KEYWORD, 'not'):
			operation_token = self.current_token
			response.register_advancement()
			self.advance()

			node = response.register(self.comparation_expression())
			if response.error: 
				return response
			return response.success(UnaryOperationNode(operation_token, node))
		
		node = response.register(self.binary_operation(self.arithmetic_expression, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
		
		if response.error:
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
														"Expected int, float, identifier, '+', '-', '(', '[' or 'not'"))

		return response.success(node)

	def arithmetic_expression(self):
		return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

	def term(self):
		return self.binary_operation(self.factor, (TT_MUL, TT_DIV))

	def factor(self):
		response = ParseResult()
		token = self.current_token

		if token.type in (TT_PLUS, TT_MINUS):
			response.register_advancement()
			self.advance()
			factor = response.register(self.factor())
			if response.error:
				 return response
			return response.success(UnaryOperationNode(token, factor))

		return self.power()

	def power(self):
		return self.binary_operation(self.call, (TT_POW, ), self.factor)

	def call(self):
		response = ParseResult()
		atom = response.register(self.atom())
		if response.error:
			 return response

		if self.current_token.type == TT_LPAREN:
			response.register_advancement()
			self.advance()
			argument_nodes = []

			if self.current_token.type == TT_RPAREN:
				response.register_advancement()
				self.advance()
			else:
				argument_nodes.append(response.register(self.expression()))
				if response.error:
					return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
											"Expected ')', 'let', 'if', 'for', 'while', 'fn', int, float, identifier, '+', '-', '(', '[' or 'not'"))

				while self.current_token.type == TT_COMMA:
					response.register_advancement()
					self.advance()

					argument_nodes.append(response.register(self.expression()))
					if response.error: 
						return response

				if self.current_token.type != TT_RPAREN:
					return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected ',' or ')'"))

				response.register_advancement()
				self.advance()
			
			return response.success(CallNode(atom, argument_nodes))
		return response.success(atom)

	def atom(self):
		response = ParseResult()
		token = self.current_token

		if token.type in (TT_INT, TT_FLOAT):
			response.register_advancement()
			self.advance()
			return response.success(NumberNode(token))
		
		elif token.type == TT_STRING:
			response.register_advancement()
			self.advance()
			return response.success(StringNode(token))

		elif token.type == TT_IDENTIFIER:
			response.register_advancement()
			self.advance()
			return response.success(VarAccessNode(token))

		elif token.type == TT_LPAREN:
			response.register_advancement()
			self.advance()
			expression = response.register(self.expression())
			if response.error: 
				return response
			if self.current_token.type == TT_RPAREN:
				response.register_advancement()
				self.advance()
				return response.success(expression)
			else:
				return response.failure(InvalidSyntaxError(
					self.current_token.position_start, self.current_token.position_end,
					"Expected ')'"
				))

		elif token.type == TT_LSQUARE:
			list_expression = response.register(self.list_expression())
			if response.error: 
				return response
			return response.success(list_expression)
		
		elif token.matches(TT_KEYWORD, 'if'):
			if_expression = response.register(self.if_expression())
			if response.error: 
				return response
			return response.success(if_expression)

		elif token.matches(TT_KEYWORD, 'for'):
			for_expression = response.register(self.for_expression())
			if response.error: 
				return response
			return response.success(for_expression)

		elif token.matches(TT_KEYWORD, 'while'):
			while_expression = response.register(self.while_expression())
			if response.error: 
				return response
			return response.success(while_expression)

		elif token.matches(TT_KEYWORD, 'fn'):
			function_definition = response.register(self.function_definition())
			if response.error: 
				return response
			return response.success(function_definition)

		return response.failure(InvalidSyntaxError(token.position_start, token.position_end,
								"Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'fn'"))

	def list_expression(self):
		response = ParseResult()
		element_nodes = []
		position_start = self.current_token.position_start.copy()

		if self.current_token.type != TT_LSQUARE:
			return response.failure(InvalidSyntaxError(token.position_start, token.position_end, "Expected '['"))

		response.register_advancement()
		self.advance()

		if self.current_token.type == TT_RSQUARE:
			response.register_advancement()
			self.advance()
		else:
			element_nodes.append(response.register(self.expression()))
			if response.error:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
						                "Expected ']', 'let', 'if', 'for', 'while', 'fn', int, float, identifier, '+', '-', '(', '[' or 'not'"))

			while self.current_token.type == TT_COMMA:
				response.register_advancement()
				self.advance()

				element_nodes.append(response.register(self.expression()))
				if response.error: 
					return response

			if self.current_token.type != TT_RSQUARE:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected ',' or ')'"))

			response.register_advancement()
			self.advance()

		return response.success(ListNode(element_nodes, position_start, self.current_token.position_end.copy()))
		
	
	def if_expression(self):
		response = ParseResult()
		all_cases = response.register(self.if_expression_cases('if'))
		if response.error: 
			return response
		cases, else_case = all_cases
		return response.success(IfNode(cases, else_case))
		
	def if_expression_b(self):
		return self.if_expression_cases('elif')
		
	def if_expression_c(self):
		response = ParseResult()
		else_case = None
		
		if self.current_token.matches(TT_KEYWORD, 'else'):
			response.register_advancement()
			self.advance()
			
			if self.current_token.type == TT_NEWLINE:
				response.register_advancement()
				self.advance()
			
				statements = response.register(self.statements())
				if response.error: 
					return response
				else_case = (statements, True)
			
				if self.current_token.matches(TT_KEYWORD, 'end'):
					response.register_advancement()
					self.advance()
				else:
					return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,"Expected 'end'"))
			else:
				expression = response.register(self.expression())
				if response.error: 
					return response
				else_case = (expression, False)
			
		return response.success(else_case)
	
	def if_expression_b_or_c(self):
		response = ParseResult()
		cases, else_case = [], None
		
		if self.current_token.matches(TT_KEYWORD, 'elif'):
			all_cases = response.register(self.if_expression_b())
			if response.error: 
				return response
			cases, else_case = all_cases
		else:
			else_case = response.register(self.if_expression_c())
			if response.error:
				 return response
				 
		return response.success((cases, else_case))
		
	def if_expression_cases(self, case_keyword):
		response = ParseResult()
		cases = []
		else_case = None
		
		if not self.current_token.matches(TT_KEYWORD, case_keyword):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected '{case_keyword}'"))
		response.register_advancement()
		self.advance()
		
		condition = response.register(self.expression())
		if response.error: 
			return response
		
		if not self.current_token.matches(TT_KEYWORD, 'then'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'then'"))
			
		response.register_advancement()
		self.advance()
		
		if self.current_token.type == TT_NEWLINE:
			response.register_advancement()
			self.advance()
			
			statements = response.register(self.statements())
			if response.error:
			 	return response
			cases.append((condition, statements, True))
			
			if self.current_token.matches(TT_KEYWORD, 'end'):
				response.register_advancement()
				self.advance()
			else:
				all_cases = response.register(self.if_expression_b_or_c())
				if response.error:
					 return response
				new_cases, else_case = all_cases
				cases.extend(new_cases)
		else:
			expression = response.register(self.statement())
			if response.error: 
				return response
			cases.append((condition, expression, False))
			
			all_cases = response.register(self.if_expression_b_or_c())
			if response.error: 
				return response
			new_cases, else_case = all_cases
			cases.extend(new_cases)
			
		return response.success((cases, else_case))

	def for_expression(self):
		response = ParseResult()

		if not self.current_token.matches(TT_KEYWORD, 'for'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, f"Expected 'for'"))

		response.register_advancement()
		self.advance()

		if self.current_token.type != TT_IDENTIFIER:
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, f"Expected identifier"))

		variable_name = self.current_token
		response.register_advancement()
		self.advance()

		if self.current_token.type != TT_EQ:
			return response.failure(InvalidSyntaxError( self.current_token.position_start, self.current_token.position_end, f"Expected '='"))
		
		response.register_advancement()
		self.advance()

		start_value = response.register(self.expression())
		if response.error: return response

		if not self.current_token.matches(TT_KEYWORD, 'to'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'to'"))
		
		response.register_advancement()
		self.advance()

		end_value = response.register(self.expression())
		if response.error: 
			return response

		if self.current_token.matches(TT_KEYWORD, 'step'):
			response.register_advancement()
			self.advance()

			step_value = response.register(self.expression())
			if response.error: 
				return response
		else:
			step_value = None

		if not self.current_token.matches(TT_KEYWORD, 'then'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, f"Expected 'then'"))

		response.register_advancement()
		self.advance()

		if self.current_token.type == TT_NEWLINE:
			response.register_advancement()
			self.advance()
			
			body = response.register(self.statements())
			if response.error:
				 return response
				 
			if not self.current_token.matches(TT_KEYWORD, 'end'):
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'end'"))

			response.register_advancement()
			self.advance()
			
			return response.success(ForNode(variable_name, start_value, end_value, step_value, body, True))

		body = response.register(self.statement())
		if response.error:
			 return response

		return response.success(ForNode(variable_name, start_value, end_value, step_value, body, False))

	def while_expression(self):
		response = ParseResult()

		if not self.current_token.matches(TT_KEYWORD, 'while'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'while'"))

		response.register_advancement()
		self.advance()

		condition = response.register(self.expression())
		if response.error: 
			return response

		if not self.current_token.matches(TT_KEYWORD, 'then'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'then'"))

		response.register_advancement()
		self.advance()

		if self.current_token.type == TT_NEWLINE:
			response.register_advancement()
			self.advance()
			
			body = response.register(self.statements())
			if response.error:
				 return response
				 
			if not self.current_token.matches(TT_KEYWORD, 'end'):
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'end'"))

			response.register_advancement()
			self.advance()
			
			return response.success(WhileNode(condition, body, True))

		body = response.register(self.statement())
		if response.error: 
			return response

		return response.success(WhileNode(condition, body, False))

	def function_definition(self):
		response = ParseResult()

		if not self.current_token.matches(TT_KEYWORD, 'fn'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'fn'"))

		response.register_advancement()
		self.advance()

		if self.current_token.type == TT_IDENTIFIER:
			variable_name_token = self.current_token
			response.register_advancement()
			self.advance()
			if self.current_token.type != TT_LPAREN:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected '('"))
		else:
			variable_name_token = None
			if self.current_token.type != TT_LPAREN:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected identifier or '('"))
		
		response.register_advancement()
		self.advance()
		argument_name_tokens = []

		if self.current_token.type == TT_IDENTIFIER:
			argument_name_tokens.append(self.current_token)
			response.register_advancement()
			self.advance()
			
			while self.current_token.type == TT_COMMA:
				response.register_advancement()
				self.advance()

				if self.current_token.type != TT_IDENTIFIER:
					return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected identifier"))

				argument_name_tokens.append(self.current_token)
				response.register_advancement()
				self.advance()
			
			if self.current_token.type != TT_RPAREN:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected ',' or ')'"))
		else:
			if self.current_token.type != TT_RPAREN:
				return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected identifier or ')'"))

		response.register_advancement()
		self.advance()

		if self.current_token.type == TT_ARROW:
			response.register_advancement()
			self.advance()

			body = response.register(self.expression())
			if response.error:
				return response

			return response.success(FunctionNode(variable_name_token, argument_name_tokens, body, True))

		if self.current_token.type != TT_NEWLINE:
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected '->' or NEWLINE"))
			
		response.register_advancement()
		self.advance()
		
		body = response.register(self.statements())
		if response.error: 
			return response
			
		if not self.current_token.matches(TT_KEYWORD, 'end'):
			return response.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,f"Expected 'end'"))
			
		response.register_advancement()
		self.advance()
		
		return response.success(FunctionNode(variable_name_token, argument_name_tokens, body, False))
	
	###################################

	def binary_operation(self, function_a, operations, function_b=None):
		if function_b == None:
			function_b = function_a
		
		response = ParseResult()
		left = response.register(function_a())
		if response.error: 
			return response

		while self.current_token.type in operations or (self.current_token.type, self.current_token.value) in operations:
			operation_token = self.current_token
			response.register_advancement()
			self.advance()
			
			right = response.register(function_b())
			if response.error: 
				return response
			
			left = BinaryOperationNode(left, operation_token, right)

		return response.success(left)