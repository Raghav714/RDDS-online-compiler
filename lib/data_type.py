"""Types module

Provides data structures necessary for identifier tracking and handling in the
compilation process as well as tokenizing.

Author: RDDS TEAM

Classes:
    Token: A named tuple object containing token information.
    Identifier: A named tuple object containing identifier information.
    Parameter: A named tuple object containing procedure param information.
    IdentifierTable: Extends the list type to provide ID table functionality.
"""

from lib.errors import ParserNameError
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line'])

Identifier = namedtuple('Identifier',
        ['name', 'type', 'size', 'params', 'mm_ptr'])

Parameter = namedtuple('Parameter', ['id', 'direction'])


class IdentifierTable(list):

    def __init__(self):
        super().__init__()

        # Create the global scope
        self.append({})

        # Create a list of scope parent names (the owner of the scope)
        self._owner_ids = ['global']

        return

    def push_scope(self, owner_id):

        # Create a brand new scope for the identifiers table
        self.append({})

        # Save the owner of this scope for future lookup
        self._owner_ids.append(owner_id)

        return

    def pop_scope(self):

        # Remove this entire scope from the identifiers table
        self.pop(-1)

        # Remove the identifier from the owner list
        self._owner_ids.pop()

        return

    def add(self, identifier, is_global=False):
        scope = -1 if not is_global else 0

        if is_global and len(self) > 2:
            raise ParserNameError('global name must be defined in program scope')

        if is_global and (identifier.name in self[0] or (len(self) > 1 and
                          identifier.name in self[1])):
            raise ParserNameError('name already declared at this scope')

        if not is_global and identifier.name in self[-1]:
            raise ParserNameError('name already declared at this scope')

        self[scope][identifier.name] = identifier

        return

    def find(self, name):

        if name in self[-1]:
            identifier = self[-1][name]
        elif name in self[0]:
            identifier = self[0][name]
        else:
            raise ParserNameError()

        return identifier

    def get_id_location(self, name):

        if self.is_global(name):
            return 'global'
        elif self.is_param(name):
            return 'param'

        return 'local'

    def is_global(self, name):
        return name in self[0]

    def is_param(self, name):
        owner = self.get_current_scope_owner()

        if owner == 'global' or not owner.params:
            return False

        for param in owner.params:
            if name == param.id.name:
                return True

        return False

    def get_param_direction(self, name):

        owner = self.get_current_scope_owner()
        
        if owner == 'global':
            return None

        for param in owner.params:
            if name == param.id.name:
                return param.direction

        return None

    def get_current_scope_owner(self):
        owner = self._owner_ids[-1]

        # If this is the global scope, return no owner
        return self[-1][self._owner_ids[-1]] if owner != 'global' else None
