"""Parser module

Inherits the Scanner module and parses the attached file's tokens as they are
encountered with the target grammar. Code is then generated and written to the
given destination file.

Author: RDDS TEAM

Classes:
    Parser: An implementation of a parser for the source language.
"""

from lib.errors import *
from lib.data_type import Identifier, Parameter, IdentifierTable

from lib.scanner import Scanner
from lib.ICG import CodeGenerator


class Parser(Scanner, CodeGenerator):
    """13"""
    def __init__(self, debug=False):
        super().__init__()

        # Public class attributes
        self.debug = debug

        # Define the previous, current, and future token holder
        self._previous = None
        self._current = None
        self._future = None

        # Define the identifier table to hold all var/program/procedure names
        self._ids = IdentifierTable()

        self._has_errors = False

        return

    def parse(self, src_path, dest_path):
        """14"""
        # Attach the source file for reading
        if not self.attach_source(src_path):
            return False

        # Attach the destination file for writing
        if not self.attach_destination(dest_path):
            return False

        # Advance the tokens twice to populate both current and future tokens
        self._advance_token()
        self._advance_token()

        # Add all runtime functions
        self._add_runtime()

        # Generate the compiled code header to handle runtime overhead
        self.generate_header()

        # Begin parsing the root <program> language structure
        try:
            self._parse_program()
        except ParserSyntaxError:
            return False

        # Generate the compiled code footer
        self.generate_footer()

        # Make sure there's no junk after the end of program
        if not self._check('eof'):
            self._warning('eof', '')

        # If errors were encountered, don't write code
        if self._has_errors:
            return False

        # Commit the code buffer to the output code file
        self.commit()

        return True

    def _add_runtime(self):
        """15"""
        # The runtime_functions list is defined in the CodeGenerator class
        for func_name in self.runtime_functions:
            # Get all parameters for these functions
            param_ids = []
            param_list = self.runtime_functions[func_name]
            for index, param in enumerate(param_list):
                # Build up each param, add it to the list
                id_obj = Identifier(name=param[0], type=param[1], size=None,
                                    params=None, mm_ptr=(index+1))
                p_obj = Parameter(id=id_obj, direction=param[2])
                param_ids.append(p_obj)

            # Build the function's identifier
            func_id = Identifier(name=func_name, type='function', size=None, 
                                 params=param_ids, mm_ptr=1)

            # Add the function to the global scope of the identifier table
            self._ids.add(func_id, is_global=True)

        return

    def _warning(self, msg, line, prefix='Warning'):
        """16"""
        print('%s: "%s", line %d' % (prefix, self._src_path, line))
        print('    %s' % msg)
        print('    %s' % self._get_line(line))

        return

    def _syntax_error(self, expected):
        """17"""
        token = self._current

        # Print the error message
        msg = ('Expected %s, encountered "%s" (%s)' %
               (expected, token.value, token.type))
        self._warning(msg, token.line, prefix='Error')

        self._has_errors = True
        raise ParserSyntaxError()

    def _name_error(self, msg, name, line):
        """18"""
        msg = '%s: %s' % (name, msg)
        self._warning(msg, line, prefix='Error')

        self._has_errors = True
        return

    def _type_error(self, expected, encountered, line):
        """19"""
        msg = 'Expected %s type, encountered %s' % (expected, encountered)
        self._warning(msg, line, prefix='Error')

        self._has_errors = True
        return

    def _runtime_error(self, msg, line):
        """20"""
        self._warning(msg, line, prefix='Error')

        self._has_errors = True
        return

    def _advance_token(self):
        """"""
        self._previous = self._current
        self._current = self._future

        if self._future is None or self._future.type != 'eof':
            self._future = self.next_token()
        return

    def _check(self, expected_type, expected_value=None, check_future=False):
        """22"""
        token = self._current

        if check_future:
            token = self._future

        return (token.type == expected_type and
               (token.value == expected_value or expected_value is None))

    def _accept(self, expected_type, expected_value=None):
        """23"""
        if self._check(expected_type, expected_value):
            self._advance_token()
            return True

        return False

    def _match(self, expected_type, expected_value=None):
        """24"""
        # Check the id_type, if we specified debug, print everything matched
        if self._accept(expected_type, expected_value):
            return self._previous

        # Something different than expected was encountered
        if expected_value is not None:
            self._syntax_error('"'+expected_value+'" ('+expected_type+')')
        else:
            self._syntax_error(expected_type)

    def _resync_at_token(self, token_type, token_value=None):
        """25"""
        while not self._check(token_type, token_value):
            self._advance_token()

        return

    def _parse_program(self):
        """26"""
        id_obj = self._parse_program_header()
        self._parse_program_body(id_obj)

        return

    def _parse_program_header(self):
        """27 """
        while not self._accept('keyword', 'the'):
            try:
                self._parse_statement()
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')
        self._match('keyword', 'program')

        id_name = self._current.value
        self._match('identifier')

        # Generate procedure label. This will be stored with the identifier
        # in place of the mm_ptr attribute since it will not be used
        label_id = self.get_label_id()

        # Add the new identifier to the global table
        id_obj = Identifier(id_name, 'program', None, None, label_id)
        self._ids.add(id_obj, is_global=True)

        self._match('keyword', 'is')

        # Generate the program entry point code
        self.generate_program_entry(id_obj.name, id_obj.mm_ptr, self.debug)

        # Push the scope to the program body level
        self._ids.push_scope(id_obj.name)

        # Add the program to the base scope so it can be resolved as owner
        self._ids.add(id_obj)

        return id_obj

    def _parse_program_body(self, program_id):
        """28"""
        local_var_size = 0
        while not self._accept('keyword', 'define'):
            try:
                self._parse_statement()
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')
        

        while not self._accept('keyword', 'body'):
            try:
                size = self._parse_declaration()

                if size is not None:
                    local_var_size += int(size)
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')

        # Label the entry point for the program
        self.generate('%s_%d_body:' % (program_id.name, program_id.mm_ptr))
        self.tab_push()

        if local_var_size != 0:
            self.comment('Allocating space for local variables', self.debug)
            self.generate('R[SP] = R[SP] - %d;' % local_var_size)

        while not self._accept('keyword', 'finish'):
            try:
                self._parse_statement()
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')

        self._match('keyword', 'program')

        # Pop out of the program body scope
        self._ids.pop_scope()
        self.tab_pop()

        return

    def _parse_declaration(self):
        """29"""
        is_global = False

        id_obj = None
        size = None

        if self._accept('keyword', 'global'):
            is_global = True

        if self._first_procedure_declaration():
            self._parse_procedure_declaration(is_global=is_global)
        elif self._first_variable_declaration():
            id_obj = self._parse_variable_declaration(is_global=is_global)
        else:
            self._syntax_error('procedure or variable declaration')

        if id_obj is not None:
            size = id_obj.size if id_obj.size is not None else 1

        return size

    def _first_variable_declaration(self):
        """30"""
        return (self._check('keyword', 'int') or
                self._check('keyword', 'float') or
                self._check('keyword', 'bool') or
                self._check('keyword', 'str'))

    def _parse_variable_declaration(self, is_global=False, is_param=False):
        """31"""
        id_type = self._parse_type_mark()

        # Stores the array size of the variable
        var_size = None

        # Formally match the token to an identifier type
        var_token = self._match('identifier')

        if self._accept('symbol', '['):
            index_type = self._parse_number(generate_code=False)

            var_size = self._previous.value
            index_line = self._previous.line

            # Check the type to make sure this is an integer so that we can
            # allocate memory appropriately
            if  index_type != 'int':
                self._type_error('int', index_type, index_line)
                raise ParserTypeError()

            self._match('symbol', ']')

        # Get the memory space pointer for this variable.
        mm_ptr = self.get_mm(var_size, is_param=is_param)

        # The declaration was valid, add the identifier to the table
        id_obj = Identifier(var_token.value, id_type, var_size, None, mm_ptr)

        if not is_param:
            try:
                self._ids.add(id_obj, is_global=is_global)
            except ParserNameError as e:
                self._name_error(str(e),
                                 var_token.value, var_token.line)

        return id_obj

    def _parse_type_mark(self):
        """32"""
        id_type = None

        if self._accept('keyword', 'int'):
            id_type = 'int'
        elif self._accept('keyword', 'float'):
            id_type = 'float'
        elif self._accept('keyword', 'bool'):
            id_type = 'bool'
        elif self._accept('keyword', 'str'):
            id_type = 'str'
        else:
            self._syntax_error('variable type')

        return id_type

    def _first_procedure_declaration(self):
        """33"""
        return self._check('keyword', 'function')

    def _parse_procedure_declaration(self, is_global):
        """34"""
        id_obj = self._parse_procedure_header(is_global=is_global)
        self._parse_procedure_body(id_obj)

        return

    def _parse_procedure_header(self, is_global):
        """35"""
        self._match('keyword', 'function')

        id_name = self._current.value
        id_line = self._current.line

        self._match('identifier')
        self._match('symbol', '(')

        params = []

        if not self._check('symbol', ')'):
            params = self._parse_parameter_list(params)

        self._match('symbol', ')')
        self._match('keyword', 'is')

        # Generate procedure label. This will be stored with the identifier
        # in place of the mm_ptr attribute since it will not be used
        label_id = self.get_label_id()

        id_obj = Identifier(id_name, 'function', None, params, label_id)

        try:
            # Add the procedure identifier to the parent and its own table
            self._ids.add(id_obj, is_global=is_global)
            self._ids.push_scope(id_obj.name)
            self._ids.add(id_obj)
        except ParserNameError:
            self._name_error('name already declared at this scope', id_name,
                             id_line)

        # Attempt to add each encountered param at the procedure scope
        for param in params:
            try:
                self._ids.add(param.id, is_global=False)
            except ParserNameError:
                self._name_error('name already declared at global scope',
                                 param.id.name, id_line)

        # Define the entry point for the function w/ unique identifier
        self.generate('%s_%d:' % (id_obj.name, id_obj.mm_ptr))
        self.tab_push()

        # Define the beginning of the function body
        self.generate('goto %s_%d_body;' % (id_obj.name, id_obj.mm_ptr))
        self.generate('')

        return id_obj

    def _parse_procedure_body(self, procedure_id):
        """36"""
        local_var_size = 0

        # Reset the local pointer for the local variables.
        self.reset_local_ptr()
        self.reset_param_ptr()

        # Accept any declarations
        while not self._accept('keyword', 'body'):
            try:
                size = self._parse_declaration()

                # If this was a local var, allocate space for it
                if size is not None:
                    local_var_size += size
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')

        # Define the function begin point
        self.generate('%s_%d_body:' %
                      (procedure_id.name, procedure_id.mm_ptr))

        self.tab_push()

        if local_var_size != 0:
            self.comment('Allocating space for local variables', self.debug)
            self.generate('R[SP] = R[SP] - %d;' % local_var_size)

        # Accept any statements
        while not self._accept('keyword', 'finish'):
            try:
                self._parse_statement()
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')

        self._match('keyword', 'function')

        # Generate code to jump back to the caller scope
        self.generate_return(self.debug)
        self.generate('')

        self.tab_pop()
        self._ids.pop_scope()
        self.tab_pop()

        return

    def _parse_parameter_list(self, params):
        """37"""
        # Get one parameter
        param = self._parse_parameter()
        params.append(param)

        # Get all following parameters
        if self._accept('symbol', ','):
            params = self._parse_parameter_list(params)

        # All parameters found will be returned in the list
        return params

    def _parse_parameter(self):
        """38"""
        # Return the id object, but don't add it to the identifier table
        # yet or get a memory location for it. This will be done when the
        # procedure is called
        id_obj = self._parse_variable_declaration(is_param=True)

        direction = None

        if self._accept('keyword', 'in'):
            direction = 'in'
        elif self._accept('keyword', 'out'):
            direction = 'out'
        else:
            self._syntax_error('"in" or "out"')

        return Parameter(id_obj, direction)

    def _parse_statement(self):
        """39"""
        if self._accept('keyword', 'return'):
            # Go to the return label to exit the procedure/program
            self.generate_return(self.debug)
        elif self._first_if_statement():
            self._parse_if_statement()
        elif self._first_loop_statement():
            self._parse_loop_statement()
        elif self._first_procedure_call():
            self._parse_procedure_call()
        elif self._first_assignment_statement():
            self._parse_assignment_statement()
        else:
            self._syntax_error('statement')

        return

    def _first_assignment_statement(self):
        """40"""
        return self._check('identifier')

    def _parse_assignment_statement(self):
        """41"""
        id_name = self._current.value
        id_line = self._current.line

        dest_type = self._parse_destination()

        # Grab the last register used in case this variable is an array
        index_reg = self.get_reg(inc=False)

        # Check to make sure this is a valid identifier
        id_obj = self._ids.find(id_name)

        self._match('symbol', '=')

        expr_type = self._parse_expression()

        # Get the register used for the last expression
        expr_reg = self.get_reg(inc=False)

        if dest_type != expr_type:
            self._type_error(dest_type, expr_type, id_line)

        # Determine the location of the identifier in the stack
        id_location = self._ids.get_id_location(id_name)

        # Verify the direction of the id if it is a param
        if id_location == 'param':
            direction = self._ids.get_param_direction(id_name)
            if direction != 'out':
                self._type_error('\'out\' param',
                                 '\'%s\' param' % direction, id_line)
                raise ParserTypeError()

        # Generate all code associated with retrieving this value
        self.generate_assignment(id_obj, id_location, index_reg, expr_reg,
                self.debug)

        return

    def _first_if_statement(self):
        """42"""
        return self._check('keyword', 'if')

    def _parse_if_statement(self):
        """43"""
        self._match('keyword', 'if')
        self._match('symbol', '(')
        self._parse_expression()
        self._match('symbol', ')')
        self._match('keyword', 'then')

        label_id = self.get_label_id()
        expr_reg = self.get_reg(inc=False)

        self.generate('if (!R[%d]) goto else_%d;' % (expr_reg, label_id))
        self.tab_push()

        while True:
            try:
                self._parse_statement()
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')

            if self._check('keyword', 'else') or self._check('keyword', 'finish'):
                break

        self.generate('goto endif_%d;' % label_id)

        self.tab_pop()
        self.generate('else_%d:' % label_id)
        self.tab_push()

        if self._accept('keyword', 'else'):
            while True:
                try:
                    self._parse_statement()
                except ParserError:
                    self._resync_at_token('symbol', ';')

                self._match('symbol', ';')

                if self._check('keyword', 'finish'):
                    break

        self._match('keyword', 'finish')
        self._match('keyword', 'if')

        self.tab_pop()
        self.generate('endif_%d:' % label_id)

        return

    def _first_loop_statement(self):
        """44"""
        return self._check('keyword', 'for')

    def _parse_loop_statement(self):
        """45"""
        self._match('keyword', 'for')
        self._match('symbol', '(')

        label_id = self.get_label_id()
        self.generate('loop_%d:' % label_id)
        self.tab_push()

        try:
            self._parse_assignment_statement()
        except ParserError:
            self._resync_at_token('symbol', ';')

        self._match('symbol', ';')

        self._parse_expression()
        self._match('symbol', ')')

        expr_reg = self.get_reg(inc=False)
        self.generate('if (!R[%d]) goto endloop_%d;' % (expr_reg, label_id))

        while not self._accept('keyword', 'finish'):
            try:
                self._parse_statement()
            except ParserError:
                self._resync_at_token('symbol', ';')

            self._match('symbol', ';')

        self._match('keyword', 'for')

        self.generate('goto loop_%d;' % label_id)
        self.tab_pop()
        self.generate('endloop_%d:' % label_id)

        return

    def _first_procedure_call(self):
        """46"""
        return self._check('symbol', '(', check_future=True)

    def _parse_procedure_call(self):
        """47"""
        # Match an identifier, check to make sure the identifier is procedure
        id_name = self._current.value
        id_line = self._current.line

        self._match('identifier')

        try:
            id_obj = self._ids.find(id_name)
        except ParserNameError as e:
            self._name_error('procedure has not been declared', id_name,
                             id_line)
            raise e

        if id_obj.type != 'function':
            self._type_error('function', id_obj.type, id_line)
            raise ParserTypeError()

        self._match('symbol', '(')

        out_names = []

        if not self._check('symbol', ')'):
            num_args, out_names = self._parse_argument_list(
                id_obj.params,
                out_names,
                index=0)

            # Make sure that too few arguments are not used
            if num_args < len(id_obj.params):
                self._runtime_error(
                    'procedure call accepts %d argument(s), %d given' %
                    (len(id_obj.params), num_args), id_line)

                raise ParserRuntimeError()

        self._match('symbol', ')')

        # Generate all procedure call code
        self.generate_procedure_call(id_obj.name, id_obj.mm_ptr, self.debug)

        # Pop parameters off the stack
        for index, param in enumerate(id_obj.params):
            out_name = out_names[index]

            self.generate_param_pop(param.id.name, self.debug)

            # If this is an outbound parameter, we must write it to its
            # memory location
            if param.direction == 'out':
                # Get the identifier object of the destination
                out_id = self._ids.find(out_name)

                # Determine where on the stack this identifier exists
                out_location = self._ids.get_id_location(out_name)

                # Store the parameter in the appropriate location
                self.generate_param_store(out_id, out_location, self.debug)

        # Finish the procedure call
        self.generate_procedure_call_end(self.debug)

        return

    def _parse_argument_list(self, params, out_names, index=0):
        """48"""
        arg_line = self._current.line
        arg_type = None

        # Make sure that too many arguments are not used
        if index > len(params) - 1:
            self._runtime_error('procedure call accepts only %d argument(s)' %
                                len(params), arg_line)
            raise ParserRuntimeError()

        # Get the parameter information for this position in the arg list
        param = params[index]

        if param.direction == 'out':
            # We may only parse a single identifier if the direction is 'out'
            arg_name = self._current.value
            arg_type = self._parse_name()

            out_names.append(arg_name)
        elif param.direction == 'in':
            # This is a 'in' parameter with only one element (not array)
            arg_type = self._parse_expression()

            out_names.append(None)

        # Get the last reg assignment in the expr. This is argument's register
        expr_reg = self.get_reg(inc=False)

        if arg_type != param.id.type:
            self._type_error(param.id.type, arg_type, arg_line)

        index += 1

        if self._accept('symbol', ','):
            index, out_names = self._parse_argument_list(
                params,
                out_names,
                index=index)

        # Push the parameters onto the stack in reverse order. The last param
        # will reach this point first
        self.generate_param_push(expr_reg, self.debug)

        return index, out_names

    def _parse_destination(self):
        """49"""
        id_name = self._current.value
        id_line = self._current.line

        self._match('identifier')

        # Make sure that identifier is valid for the scope
        try:
            id_obj = self._ids.find(id_name)
        except ParserNameError as e:
            self._name_error('not declared in this scope', id_name, id_line)
            raise e

        # Check type to make sure it's a variable
        if not id_obj.type in ['int', 'float', 'bool', 'str']:
            self._type_error('variable', id_obj.type, id_line)
            raise ParserTypeError()

        id_type = id_obj.type

        if self._accept('symbol', '['):
            expr_line = self._current.line
            expr_type = self._parse_expression()

            if expr_type != 'int':
                self._type_error('int', expr_type, expr_line)

            self._accept('symbol', ']')
        elif id_obj.size is not None:
            self._runtime_error('%s: array requires index' % id_name, id_line)

        return id_type

    def _parse_expression(self):
        """50"""
        self.comment('Parsing expression', self.debug)

        negate = False

        if self._accept('keyword', 'not'):
            negate = True

        line = self._current.line
        id_type = self._parse_arith_op()

        if negate and id_type not in ['int', 'bool']:
            self._type_error('int or bool', id_type, line)
            raise ParserTypeError()

        while True:
            operand1 = self.get_reg(inc=False)

            if self._accept('symbol', '&'):
                operation = '&'
            elif self._accept('symbol', '|'):
                operation = '|'
            else:
                break

            if id_type not in ['int', 'bool']:
                self._type_error('int or bool', id_type, line)
                raise ParserTypeError()

            next_type = self._parse_arith_op()

            operand2 = self.get_reg(inc=False)

            if next_type not in ['int', 'bool']:
                self._type_error('int or bool', next_type, line)
                raise ParserTypeError()

            result = self.generate_operation(operand1, id_type, operand2,
                                             next_type, operation)

            if negate:
                self.generate('R[%d] = ~R[%d];' % (result, result))

        return id_type

    def _parse_arith_op(self):
        """51"""
        line = self._current.line
        id_type = self._parse_relation()

        while True:
            operand1 = self.get_reg(inc=False)

            if self._accept('symbol', '+'):
                operation = '+'
            elif self._accept('symbol', '-'):
                operation = '-'
            else:
                break

            if id_type not in ['int', 'float']:
                self._type_error('int or float', id_type, line)
                raise ParserTypeError()

            next_type = self._parse_relation()

            operand2 = self.get_reg(inc=False)
            
            if next_type not in ['int', 'float']:
                self._type_error('int or float', next_type, line)
                raise ParserTypeError()

            self.generate_operation(operand1, id_type, operand2, next_type,
                                    operation)

        return id_type

    def _parse_relation(self):
        """52 """
        line = self._current.line
        id_type = self._parse_term()

        # Check for relational operators. Note that relational operators
        # are only valid for integer or boolean tokens
        while True:
            operand1 = self.get_reg(inc=False)

            if self._accept('symbol', '<'):
                operation = '<'
            elif self._accept('symbol', '>'):
                operation = '>'
            elif self._accept('symbol', '<='):
                operation = '<='
            elif self._accept('symbol', '>='):
                operation = '>='
            elif self._accept('symbol', '=='):
                operation = '=='
            elif self._accept('symbol', '!='):
                operation = '!='
            else:
                break

            if id_type not in ['int', 'bool']:
                self._type_error('int or bool', id_type, line)
                raise ParserTypeError()

            next_type = self._parse_term()

            operand2 = self.get_reg(inc=False)

            if next_type not in ['int', 'bool']:
                self._type_error('int or bool', next_type, line)
                raise ParserTypeError()

            self.generate_operation(operand1, id_type, operand2, next_type,
                                    operation)

        return id_type

    def _parse_term(self):
        """53"""
        line = self._current.line
        id_type = self._parse_factor()

        # Check for multiplication or division operators. Note that these
        # operators are only valid for integer or float values
        while True:
            operand1 = self.get_reg(inc=False)

            if self._accept('symbol', '*'):
                operation = '*'
            elif self._accept('symbol', '/'):
                operation = '/'
            else:
                break

            if id_type not in ['int', 'float']:
                self._type_error('int or float', id_type, line)
                raise ParserTypeError()

            line = self._current.line
            next_type = self._parse_factor()

            operand2 = self.get_reg(inc=False)

            if next_type not in ['int', 'float']:
                self._type_error('int or float', next_type, line)
                raise ParserTypeError()

            self.generate_operation(operand1, id_type, operand2, next_type,
                                    operation)

        return id_type

    def _parse_factor(self):
        """54"""
        id_type = None

        if self._accept('symbol', '('):
            id_type = self._parse_expression()
            self._match('symbol', ')')
        elif self._accept('str'):
            id_type = 'str'
            str_val = self._previous.value

            self.generate('R[%d] = (int)"%s";' % (self.get_reg(), str_val))
        elif self._accept('keyword', 'true'):
            id_type = 'bool'

            self.generate('R[%d] = 1;' % (self.get_reg()))
        elif self._accept('keyword', 'false'):
            id_type = 'bool'

            self.generate('R[%d] = 0;' % (self.get_reg()))
        elif self._accept('symbol', '-'):
            if self._first_name():
                id_type = self._parse_name()
            elif self._check('int') or self._check('float'):
                id_type = self._parse_number(negate=True)
            else:
                self._syntax_error('variable name, int, or float')
        elif self._first_name():
            id_type = self._parse_name()
        elif self._check('int') or self._check('float'):
            id_type = self._parse_number(negate=False)
        else:
            self._syntax_error('factor')

        return id_type

    def _first_name(self):
        """55"""
        return self._check('identifier')

    def _parse_name(self):
        """56"""
        id_name = self._current.value
        id_line = self._current.line

        self._match('identifier')

        # Make sure that identifier is valid for the scope
        try:
            id_obj = self._ids.find(id_name)
            id_type = id_obj.type
        except ParserNameError as e:
            self._name_error('not declared in this scope', id_name, id_line)
            raise e

        # Check type to make sure it's a variable
        if not id_type in ['int', 'float', 'bool', 'str']:
            self._type_error('variable', id_type, id_line)
            raise ParserTypeError()

        if self._accept('symbol', '['):
            index_type = self._parse_expression()

            if not index_type == 'int':
                self._type_error('int', index_type, id_line)
                raise ParserTypeError()

            self._match('symbol', ']')
        elif id_obj.size is not None:
            self._runtime_error('%s: array requires index' % id_name, id_line)

        # Get the last register allocated. The index will be here if it's used
        index_reg = self.get_reg(inc=False)

        # Determine the location of the identifier in the stack
        id_location = self._ids.get_id_location(id_name)

        # Verify the direction of the id if it is a param
        if id_location == 'param':
            direction = self._ids.get_param_direction(id_name)
            if direction != 'in':
                self._type_error('\'in\' param',
                                 '\'%s\' param' % direction, id_line)
                raise ParserTypeError()

        # Generate all code associated with retrieving this value
        self.generate_name(id_obj, id_location, index_reg, self.debug)

        return id_type

    def _parse_number(self, negate=False, generate_code=True):
        """57"""
        number = self._current.value
        id_type = self._current.type

        # Parse the number (either float or integer type)
        if not self._accept('int') and not self._accept('float'):
            self._syntax_error('number')

        # Generate the code for this number if desired
        if generate_code:
            self.generate_number(number, id_type, negate)

        return id_type
