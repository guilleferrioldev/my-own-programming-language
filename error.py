from string_with_arrows import *

###########################################
# ERRORS
###########################################

class Error:
	def __init__(self, position_start, position_end, error_name, details):
		self.position_start = position_start
		self.position_end = position_end
		self.error_name = error_name
		self.details = details
	
	def as_string(self):
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.position_start.file_name}, line {self.position_start.line_number + 1}'
		result += '\n\n' + string_with_arrows(self.position_start.file_text, self.position_start, self.position_end)
		return result

class IllegalCharError(Error):
	def __init__(self, position_start, position_end, details):
		Error.__init__(self, position_start, position_end, 'Illegal Character', details)

class ExpectedCharError(Error):
	def __init__(self, position_start, position_end, details):
		Error.__init__(self, position_start, position_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, position_start, position_end, details=''):
		Error.__init__(self, position_start, position_end, 'Invalid Syntax', details)

class RunTimeError(Error):
	def __init__(self, position_start, position_end, details, context):
		Error.__init__(self, position_start, position_end, 'Runtime Error', details)
		self.context = context

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.position_start.file_text, self.position_start, self.position_end)
		return result

	def generate_traceback(self):
		result = ''
		position = self.position_start
		context = self.context

		while context:
			result = f'  File {position.file_name}, line {str(position.line_number + 1)}, in {context.display_name}\n' + result
			position = context.parent_entry_position
			context = context.parent

		return 'Traceback (most recent call last):\n' + result
