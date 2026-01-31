"""
Symbol Table - Manages identifier scopes for the Jack compiler.

Stores and retrieves symbol information during compilation.
Part of the Nand2Tetris course (Project 11).
"""

from typing import Any, Dict, Optional


class Node:
    """A node in the linked list that holds a symbol entry."""

    def __init__(self, hash_table: Dict[str, Any], next_node: 'Node' = None) -> None:
        """Initialize a node with a hash table entry."""
        self.hash_table = hash_table
        self.next_node = next_node

    def set_next(self, next_node: 'Node') -> None:
        """Set the next node pointer."""
        self.next_node = next_node

    def get_next(self) -> Optional['Node']:
        """Get the next node."""
        return self.next_node

    def get_hash_table(self) -> Dict[str, Any]:
        """Get the hash table for this node."""
        return self.hash_table

    # Backward compatibility aliases
    def setNext(self, next_node: 'Node') -> None:
        self.set_next(next_node)

    def getNext(self) -> Optional['Node']:
        return self.get_next()

    def getHashTable(self) -> Dict[str, Any]:
        return self.get_hash_table()


class LinkedList:
    """A linked list for storing symbol table entries."""

    def __init__(self) -> None:
        """Initialize an empty linked list."""
        self.first_node = None

    def insert(self, hash_table: Dict[str, Any]) -> None:
        """Insert a new entry at the front of the list."""
        inserted_node = Node(hash_table)
        inserted_node.set_next(self.first_node)
        self.first_node = inserted_node

    def reset_method_table(self) -> None:
        """Clear the linked list."""
        self.first_node = None

    def view_table(self) -> None:
        """Print all entries in the linked list."""
        current = self.first_node
        while current is not None:
            print(current.get_hash_table())
            current = current.get_next()

    def traverse(self, key: str, identifier: str) -> Optional[Any]:
        """Search for an identifier and return the value of the specified key."""
        current = self.first_node
        while current is not None:
            entry = current.get_hash_table()
            if entry['name'] == identifier:
                if key in entry:
                    return entry[key]
            current = current.get_next()
        return None

    def traverse_two_inputs(self, key: str, identifier: str, lookup_class_name: str) -> Optional[Any]:
        """Search for an identifier within a specific class and return the key value."""
        current = self.first_node
        while current is not None:
            entry = current.get_hash_table()
            if entry['name'] == identifier and entry['kind'] == lookup_class_name:
                if key in entry:
                    return entry[key]
            current = current.get_next()
        return None

    # Backward compatibility aliases
    def resetMethodTable(self) -> None:
        self.reset_method_table()

    def viewTable(self) -> None:
        self.view_table()

    def transverse(self, key: str, identifier: str) -> Optional[Any]:
        return self.traverse(key, identifier)

    def transverseTwoInputs(self, key: str, identifier: str, lookup_class_name: str) -> Optional[Any]:
        return self.traverse_two_inputs(key, identifier, lookup_class_name)


class SymbolTable:
    """Symbol table for managing class and method scopes."""

    def __init__(self) -> None:
        """Initialize the symbol table."""
        self.class_symbol_table = LinkedList()
        self.method_symbol_table = LinkedList()
        self.static_count = 0
        self.field_count = 0
        self.argument_count = 0
        self.total_var_count = 0

        # Backward compatibility aliases
        self.classSymbolTable = self.class_symbol_table
        self.methodSymbolTable = self.method_symbol_table
        self.staticCount = 0
        self.fieldCount = 0
        self.argumentCount = 0
        self.totalvarCount = 0

    def start_subroutine(self) -> None:
        """Reset the subroutine-level symbol table for a new subroutine."""
        self.method_symbol_table.reset_method_table()
        self.argument_count = 0
        self.total_var_count = 0
        self.argumentCount = 0
        self.totalvarCount = 0

    def var_count(self, kind: str) -> int:
        """Return the count of variables of the given kind."""
        if kind == 'var':
            return self.total_var_count
        elif kind == 'argument':
            return self.argument_count - 1
        elif kind == 'field':
            return self.field_count
        elif kind == 'static':
            return self.static_count
        return 0

    def class_start(self) -> None:
        """Reset class-level counters for a new class."""
        self.field_count = 0
        self.static_count = 0
        self.fieldCount = 0
        self.staticCount = 0

    def _add_id(self, name: str, symbol_type: str, kind: str) -> Any:
        """Assign and return the running index for a new identifier."""
        if kind == 'var':
            self.total_var_count += 1
            self.totalvarCount = self.total_var_count
            return self.total_var_count - 1
        elif symbol_type == 'method':
            return self.argument_count
        elif kind == 'argument':
            self.argument_count += 1
            self.argumentCount = self.argument_count
            return self.argument_count - 1
        elif kind == 'static':
            self.static_count += 1
            self.staticCount = self.static_count
            return self.static_count - 1
        elif kind == 'field':
            self.field_count += 1
            self.fieldCount = self.field_count
            return self.field_count - 1
        elif kind == 'OS':
            return str(symbol_type)
        return None

    def define_subroutine_tracker(self, name: str, symbol_type: str, kind: str, is_void: bool) -> None:
        """Track subroutine information for later use."""
        self.class_symbol_table.insert({
            'name': name,
            'type': symbol_type,
            'kind': kind,
            '#': self._add_id(name, symbol_type, kind),
            'void': is_void
        })

    def define(self, name: str, symbol_type: str, kind: str) -> None:
        """Define a new class-level identifier."""
        self.class_symbol_table.insert({
            'name': name,
            'type': symbol_type,
            'kind': kind,
            '#': self._add_id(name, symbol_type, kind)
        })

    def define_method(self, name: str, symbol_type: str, kind: str) -> None:
        """Define a new method-level identifier."""
        self.method_symbol_table.insert({
            'name': name,
            'type': symbol_type,
            'kind': kind,
            '#': self._add_id(name, symbol_type, kind)
        })

    def view_table_cst(self) -> None:
        """Print the class symbol table."""
        print('\n    ----------class  symbol table----------')
        self.class_symbol_table.view_table()

    def view_table_mst(self) -> None:
        """Print the method symbol table."""
        print('\n    ----------method symbol table----------')
        self.method_symbol_table.view_table()

    def get_kind(self, identifier: str) -> Optional[str]:
        """Get the kind of an identifier, translating to VM segments."""
        result = self.method_symbol_table.traverse('kind', identifier)
        if result is not None:
            if result == 'var':
                return 'local'
            elif result == 'argument':
                return 'argument'
        else:
            static_or_field = self.class_symbol_table.traverse('kind', identifier)
            if static_or_field == 'static':
                return 'static'
            elif static_or_field == 'field':
                return 'this'
        return None

    def get_id(self, identifier: str) -> Optional[int]:
        """Get the index of an identifier."""
        result = self.method_symbol_table.traverse('#', identifier)
        if result is not None:
            return result
        return self.class_symbol_table.traverse('#', identifier)

    def get_id_of_class(self, identifier: str, lookup_class_name: str) -> Optional[int]:
        """Get the index of an identifier within a specific class."""
        return self.class_symbol_table.traverse_two_inputs('#', identifier, lookup_class_name)

    def get_void(self, identifier: str, lookup_class_name: str) -> Optional[bool]:
        """Check if a subroutine returns void."""
        result = self.method_symbol_table.traverse_two_inputs('void', identifier, lookup_class_name)
        if result is not None:
            return result
        return self.class_symbol_table.traverse_two_inputs('void', identifier, lookup_class_name)

    def get_type(self, identifier: str) -> Optional[str]:
        """Get the type of an identifier."""
        result = self.method_symbol_table.traverse('type', identifier)
        if result is not None:
            return result
        return self.class_symbol_table.traverse('type', identifier)

    def get_type_from_class(self, identifier: str, lookup_class_name: str) -> Optional[str]:
        """Get the type of an identifier within a specific class."""
        result = self.method_symbol_table.traverse_two_inputs('type', identifier, lookup_class_name)
        if result is not None:
            return result
        return self.class_symbol_table.traverse_two_inputs('type', identifier, lookup_class_name)

    # Backward compatibility aliases
    def startSubroutine(self) -> None:
        self.start_subroutine()

    def varCount(self, kind: str) -> int:
        return self.var_count(kind)

    def classStart(self) -> None:
        self.class_start()

    def addID(self, name: str, symbol_type: str, kind: str) -> Any:
        return self._add_id(name, symbol_type, kind)

    def defineSubroutineTracker(self, name: str, symbol_type: str, kind: str, is_void: bool) -> None:
        self.define_subroutine_tracker(name, symbol_type, kind, is_void)

    def defineMethod(self, name: str, symbol_type: str, kind: str) -> None:
        self.define_method(name, symbol_type, kind)

    def viewTableCST(self) -> None:
        self.view_table_cst()

    def viewTableMST(self) -> None:
        self.view_table_mst()

    def lookAtEachRow(self) -> None:
        self.class_symbol_table.traverse('x', '')
        self.method_symbol_table.traverse('x', '')

    def getKind(self, identifier: str) -> Optional[str]:
        return self.get_kind(identifier)

    def getID(self, identifier: str) -> Optional[int]:
        return self.get_id(identifier)

    def getIDofClass(self, identifier: str, lookup_class_name: str) -> Optional[int]:
        return self.get_id_of_class(identifier, lookup_class_name)

    def getVoid(self, identifier: str, lookup_class_name: str) -> Optional[bool]:
        return self.get_void(identifier, lookup_class_name)

    def getType(self, identifier: str) -> Optional[str]:
        return self.get_type(identifier)

    def getTypeFromClass(self, identifier: str, lookup_class_name: str) -> Optional[str]:
        return self.get_type_from_class(identifier, lookup_class_name)
