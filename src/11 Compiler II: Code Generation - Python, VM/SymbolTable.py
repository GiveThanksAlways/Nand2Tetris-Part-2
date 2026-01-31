"""
Symbol Table module for the Jack compiler.

This module provides data structures for managing symbol tables during
compilation, tracking variables, their types, kinds, and scope.
"""

from typing import Any, Dict, Optional


class Node:
    """A node in the linked list containing a symbol table entry."""

    def __init__(self, hash_table: Dict[str, Any], next_node: 'Node' = None):
        """
        Initialize a node with a hash table entry.

        Args:
            hash_table: Dictionary containing symbol information.
            next_node: Reference to the next node in the list.
        """
        self.hash_table = hash_table
        self.next_node = next_node

    def set_next(self, next_node: 'Node') -> None:
        """Set the reference to the next node."""
        self.next_node = next_node

    def get_next(self) -> Optional['Node']:
        """Get the reference to the next node."""
        return self.next_node

    def get_hash_table(self) -> Dict[str, Any]:
        """Get the hash table stored in this node."""
        return self.hash_table


class LinkedList:
    """A linked list for storing symbol table entries."""

    def __init__(self):
        """Initialize an empty linked list."""
        self.first_node: Optional[Node] = None

    def insert(self, hash_table: Dict[str, Any]) -> None:
        """Insert a new entry at the beginning of the list."""
        inserted_node = Node(hash_table)
        inserted_node.set_next(self.first_node)
        self.first_node = inserted_node

    def reset_method_table(self) -> None:
        """Clear the linked list."""
        self.first_node = None

    def view_table(self) -> None:
        """Print all entries in the linked list for debugging."""
        current = self.first_node
        while current is not None:
            print(current.get_hash_table())
            current = current.get_next()

    def traverse(self, key: str, identifier: str) -> Optional[Any]:
        """
        Search for a value by identifier name.

        Args:
            key: The key to retrieve from the matching entry.
            identifier: The name to search for.

        Returns:
            The value for the key if found, None otherwise.
        """
        current = self.first_node
        while current is not None:
            if current.get_hash_table()['name'] == identifier:
                if key in current.get_hash_table():
                    return current.get_hash_table()[key]
            current = current.get_next()
        return None

    def traverse_two_inputs(self, key: str, identifier: str,
                            lookup_class_name: str) -> Optional[Any]:
        """
        Search for a value by identifier and class name.

        Args:
            key: The key to retrieve from the matching entry.
            identifier: The name to search for.
            lookup_class_name: The class name to match against kind.

        Returns:
            The value for the key if found, None otherwise.
        """
        current = self.first_node
        while current is not None:
            entry = current.get_hash_table()
            if entry['name'] == identifier and entry['kind'] == lookup_class_name:
                if key in entry:
                    return entry[key]
            current = current.get_next()
        return None


class SymbolTable:
    """
    Symbol table for managing variable and subroutine symbols.

    Maintains separate tables for class-level and method-level symbols.
    """

    def __init__(self):
        """Initialize the symbol table with empty tables and counters."""
        self.class_symbol_table = LinkedList()
        self.method_symbol_table = LinkedList()
        self.static_count = 0
        self.field_count = 0
        self.argument_count = 0
        self.total_var_count = 0

    def start_subroutine(self) -> None:
        """Clear the method symbol table for a new subroutine."""
        self.method_symbol_table.reset_method_table()
        self.argument_count = 0
        self.total_var_count = 0

    def var_count(self, kind: str) -> int:
        """Get the count of variables of a given kind."""
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

    def add_id(self, name: str, var_type: str, kind: str) -> Any:
        """
        Allocate an index for a new symbol.

        Args:
            name: The symbol name.
            var_type: The type of the symbol.
            kind: The kind (var, argument, static, field, OS).

        Returns:
            The allocated index for the symbol.
        """
        if kind == 'var':
            self.total_var_count += 1
            return self.total_var_count - 1
        elif var_type == 'method':
            return self.argument_count
        elif kind == 'argument':
            self.argument_count += 1
            return self.argument_count - 1
        elif kind == 'static':
            self.static_count += 1
            return self.static_count - 1
        elif kind == 'field':
            self.field_count += 1
            return self.field_count - 1
        elif kind == 'OS':
            return str(var_type)
        return None

    def define_subroutine_tracker(self, name: str, var_type: str,
                                   kind: str, is_void: bool) -> None:
        """Track a subroutine definition in the class symbol table."""
        self.class_symbol_table.insert({
            'name': name,
            'type': var_type,
            'kind': kind,
            '#': self.add_id(name, var_type, kind),
            'void': is_void
        })

    def define(self, name: str, var_type: str, kind: str) -> None:
        """Define a class-level symbol (field or static)."""
        self.class_symbol_table.insert({
            'name': name,
            'type': var_type,
            'kind': kind,
            '#': self.add_id(name, var_type, kind)
        })

    def define_method(self, name: str, var_type: str, kind: str) -> None:
        """Define a method-level symbol (argument or local var)."""
        self.method_symbol_table.insert({
            'name': name,
            'type': var_type,
            'kind': kind,
            '#': self.add_id(name, var_type, kind)
        })

    def view_table_cst(self) -> None:
        """Print the class symbol table for debugging."""
        print('\n    ----------class  symbol table----------')
        self.class_symbol_table.view_table()

    def view_table_mst(self) -> None:
        """Print the method symbol table for debugging."""
        print('\n    ----------method symbol table----------')
        self.method_symbol_table.view_table()

    def look_at_each_row(self) -> None:
        """Traverse both tables (for debugging)."""
        self.class_symbol_table.traverse('x', '')
        self.method_symbol_table.traverse('x', '')

    def get_kind(self, identifier: str) -> Optional[str]:
        """
        Get the segment kind for an identifier.

        Returns:
            The VM segment: 'local', 'argument', 'static', 'this', or None.
        """
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
        """Get the index of an identifier in its segment."""
        result = self.method_symbol_table.traverse('#', identifier)
        if result is not None:
            return result
        return self.class_symbol_table.traverse('#', identifier)

    def get_id_of_class(self, identifier: str,
                        lookup_class_name: str) -> Optional[int]:
        """Get the index for an identifier within a specific class."""
        return self.class_symbol_table.traverse_two_inputs(
            '#', identifier, lookup_class_name)

    def get_void(self, identifier: str,
                 lookup_class_name: str) -> Optional[bool]:
        """Check if a subroutine returns void."""
        result = self.method_symbol_table.traverse_two_inputs(
            'void', identifier, lookup_class_name)
        if result is not None:
            return result
        return self.class_symbol_table.traverse_two_inputs(
            'void', identifier, lookup_class_name)

    def get_type(self, identifier: str) -> Optional[str]:
        """Get the type of an identifier."""
        result = self.method_symbol_table.traverse('type', identifier)
        if result is not None:
            return result
        return self.class_symbol_table.traverse('type', identifier)

    def get_type_from_class(self, identifier: str,
                            lookup_class_name: str) -> Optional[str]:
        """Get the type of an identifier within a specific class."""
        result = self.method_symbol_table.traverse_two_inputs(
            'type', identifier, lookup_class_name)
        if result is not None:
            return result
        return self.class_symbol_table.traverse_two_inputs(
            'type', identifier, lookup_class_name)

    # Backwards compatibility aliases
    startSubroutine = start_subroutine
    classStart = class_start
    varCount = var_count
    addID = add_id
    defineSubroutineTracker = define_subroutine_tracker
    defineMethod = define_method
    viewTableCST = view_table_cst
    viewTableMST = view_table_mst
    lookAtEachRow = look_at_each_row
    getKind = get_kind
    getID = get_id
    getIDofClass = get_id_of_class
    getVoid = get_void
    getType = get_type
    getTypeFromClass = get_type_from_class
