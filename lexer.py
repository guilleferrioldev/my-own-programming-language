from error import Error, IllegalCharError, ExpectedCharError
from constants import *
from typing import Self

###########################################
# TOKENS
###########################################

class Token:
	def __init__(self, type_, value=None, position_start=None, position_end=None):
		self.type = type_
		self.value = value

		if position_start:
			self.position_start = position_start.copy()
			self.position_end = position_start.copy()
			self.position_end.advance()

		if position_end:
			self.position_end = position_end.copy()

	def matches(self, type_, value):
		return self.type == type_ and self.value == value
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'


###########################################
# POSITION
###########################################

class Position:
	def __init__(self, index, line_number, column, file_name, file_text):
		self.index = index
		self.line_number = line_number
		self.column = column
		self.file_name = file_name
		self.file_text = file_text

	def advance(self, current_character=None):
		self.index += 1
		self.column += 1

		if current_character == '\n':
			self.line_number += 1
			self.column = 0

		return self

	def copy(self):
		return Position(self.index, self.line_number, self.column, self.file_name, self.file_text)


###########################################
# LEXER
###########################################

class Lexer:
	def __init__(self, file_name, text):
		self.file_name = file_name
		self.text = text
		self.position = Position(-1, 0, -1, file_name, text)
		self.current_character = None
		self.advance()
	
	def advance(self):
		self.position.advance(self.current_character)
		self.current_character = self.text[self.position.index] if self.position.index < len(self.text) else None

	def make_tokens(self):
		tokens = []

		while self.current_character != None:
			if self.current_character in ' \t':
				self.advance()
			elif self.current_character == '#':
				self.skip_comment()
			elif self.current_character in ';\n':
				tokens.append(Token(TT_NEWLINE, position_start=self.position))
				self.advance()
			elif self.current_character in DIGITS:
				tokens.append(self.make_number())
			elif self.current_character in LETTERS:
				tokens.append(self.make_identifier())
			elif self.current_character == '"':
				tokens.append(self.make_string())
			elif self.current_character == '+':
				tokens.append(Token(TT_PLUS, position_start=self.position))
				self.advance()
			elif self.current_character == '-':
				tokens.append(self.make_minus_or_arrow())
			elif self.current_character == '*':
				tokens.append(Token(TT_MUL, position_start=self.position))
				self.advance()
			elif self.current_character == '/':
				tokens.append(Token(TT_DIV, position_start=self.position))
				self.advance()
			elif self.current_character == '^':
				tokens.append(Token(TT_POW, position_start=self.position))
				self.advance()
			elif self.current_character == '(':
				tokens.append(Token(TT_LPAREN, position_start=self.position))
				self.advance()
			elif self.current_character == ')':
				tokens.append(Token(TT_RPAREN, position_start=self.position))
				self.advance()
			elif self.current_character == '[':
				tokens.append(Token(TT_LSQUARE, position_start=self.position))
				self.advance()
			elif self.current_character == ']':
				tokens.append(Token(TT_RSQUARE, position_start=self.position))
				self.advance()
			elif self.current_character == '!':
				token, error = self.make_not_equals()
				if error: return [], error
				tokens.append(token)
			elif self.current_character == '=':
				tokens.append(self.make_equals())
			elif self.current_character == '<':
				tokens.append(self.make_less_than())
			elif self.current_character == '>':
				tokens.append(self.make_greater_than())
			elif self.current_character == ',':
				tokens.append(Token(TT_COMMA, position_start=self.position))
				self.advance()
			else:
				position_start = self.position.copy()
				char = self.current_character
				self.advance()
				return [], IllegalCharError(position_start, self.position, "'" + char + "'")

		tokens.append(Token(TT_EOF, position_start=self.position))
		return tokens, None

	def make_number(self):
		num_str = ''
		dot_count = 0
		position_start = self.position.copy()

		while self.current_character != None and self.current_character in DIGITS + '.':
			if self.current_character == '.':
				if dot_count == 1: 
					break
				dot_count += 1
			num_str += self.current_character
			self.advance()

		if dot_count == 0:
			return Token(TT_INT, int(num_str), position_start, self.position)
		else:
			return Token(TT_FLOAT, float(num_str), position_start, self.position)

	def make_identifier(self):
		id_str = ''
		position_start = self.position.copy()

		while self.current_character != None and self.current_character in LETTERS_DIGITS + '_':
			id_str += self.current_character
			self.advance()

		token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
		return Token(token_type, id_str, position_start, self.position)

	def make_minus_or_arrow(self):
		token_type = TT_MINUS
		position_start = self.position.copy()
		self.advance()

		if self.current_character == '>':
			self.advance()
			token_type = TT_ARROW

		return Token(token_type, position_start=position_start, position_end=self.position)

	def make_not_equals(self):
		position_start = self.position.copy()
		self.advance()

		if self.current_character == '=':
			self.advance()
			return Token(TT_NE, position_start=position_start, position_end=self.position), None

		self.advance()
		return None, ExpectedCharError(position_start, self.position, "'=' (after '!')")
	
	def make_equals(self):
		token_type = TT_EQ
		position_start = self.position.copy()
		self.advance()

		if self.current_character == '=':
			self.advance()
			token_type = TT_EE

		return Token(token_type, position_start=position_start, position_end=self.position)

	def make_less_than(self):
		token_type = TT_LT
		position_start = self.position.copy()
		self.advance()

		if self.current_character == '=':
			self.advance()
			token_type = TT_LTE

		return Token(token_type, position_start=position_start, position_end=self.position)

	def make_greater_than(self):
		token_type = TT_GT
		position_start = self.position.copy()
		self.advance()

		if self.current_character == '=':
			self.advance()
			token_type = TT_GTE

		return Token(token_type, position_start=position_start, position_end=self.position)

	def make_string(self):
		string = ""
		position_start = self.position.copy()
		escape_character = False
		self.advance()

		escape_characters = {
			'n': '\n',
			't': '\t'
			}

		while self.current_character != None and (self.current_character != '"' or escape_character):
			if escape_character:
				string += escape_characters.get(self.current_char, self.current_char)
			else:
				if self.current_character == "\\":
					escape_character = True 
				else:
					string += self.current_character
			self.advance()
			escape_character = False
	
		self.advance()
		return Token(TT_STRING, string, position_start, self.position)
		
	def skip_comment(self):
		self.advance()
		
		while self.current_char != '\n':
			self.advance()
		
		self.advance()





