"""
Symbol Table module for the Jack compiler.

This module provides symbol table functionality for tracking variable and
subroutine declarations during compilation, using a linked list structure.
"""

from typing import Any, Dict, Optional, Union


class Node:
    """A node in the linked list containing a hash table entry."""

    def __init__(self, hash_table: Dict[str, Any], next_node: Optional['Node'] = None) -> None:
        """
        Initialize a node with a hash table and optional next node pointer.

        Args:
            hash_table: Dictionary containing symbol information.
            next_node: Reference to the next node in the list.
        """
        self.hash_table = hash_table
        self.next_node = next_node

    def set_next(self, next_node: Optional['Node']) -> None:
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

    def __init__(self) -> None:
        """Initialize an empty linked list."""
        self.first_node: Optional[Node] = None

    def insert(self, hash_table: Dict[str, Any]) -> None:
        """
        Insert a new hash table entry at the beginning of the list.

        Args:
            hash_table: Dictionary containing symbol information.
        """
        inserted_node = Node(hash_table)
        inserted_node.set_next(self.first_node)
        self.first_node = inserted_node

    def reset_method_table(self) -> None:
        """Clear the linked list by removing all nodes."""
        self.first_node = None

    def view_table(self) -> None:
        """Print all entries in the linked list for debugging."""
        current = self.first_node
        while current is not None:
            print(current.get_hash_table())
            current = current.get_next()

    def traverse(self, key: str, identifier: str) -> Optional[Any]:
        """
        Search for a value by identifier and key in the linked list.

        Args:
            key: The key to retrieve from the matching entry.
            identifier: The name to search for.

        Returns:
            The value associated with the key if found, None otherwise.
        """
        current = self.first_node
        while current is not None:
            entry_name = current.get_hash_table().get('name')
            if identifier == entry_name:
                if key in current.get_hash_table():
                    return current.get_hash_table()[key]
            current = current.get_next()
        return None


class SymbolTable:
    """
    Symbol table for tracking class and method scope symbols.

    Maintains separate tables for class-level and method-level symbols,
    with counters for different variable kinds.
    """

    def __init__(self) -> None:
        """Initialize the symbol table with empty class and method tables."""
        self.class_symbol_table = LinkedList()
        self.method_symbol_table = LinkedList()
        self.static_count = 0
        self.field_count = 0
        self.argument_count = 0
        self.total_var_count = 0

    def start_subroutine(self) -> None:
        """Reset the method symbol table for a new subroutine."""
        self.method_symbol_table.reset_method_table()
        self.argument_count = 0
        self.total_var_count = 0

    def var_count(self, kind: str) -> int:
        """
        Get the count of variables of a specific kind.

        Args:
            kind: The variable kind ('var', 'argument', 'field', 'static').

        Returns:
            The count of variables of that kind.
        """
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
        """Reset field and static counters for a new class."""
        self.field_count = 0
        self.static_count = 0

    def add_id(self, name: str, symbol_type: str, kind: str) -> Optional[Union[int, str]]:
        """
        Add an identifier and return its index.

        Args:
            name: The symbol name.
            symbol_type: The symbol type.
            kind: The symbol kind.

        Returns:
            The index for the new symbol.
        """
        if kind == 'var':
            self.total_var_count += 1
            return self.total_var_count - 1
        elif kind == 'argument':
            self.argument_count += 1
            return self.argument_count - 1
        elif kind == 'static':
            self.static_count += 1
            return self.static_count - 1
        elif kind == 'field':
            self.field_count += 1
            return self.field_count - 1
        elif symbol_type == 'method':
            return self.argument_count
        elif kind == 'OS':
            return str(symbol_type)
        return None

    def define_subroutine_tracker(
        self, name: str, symbol_type: str, kind: str, is_void: bool
    ) -> None:
        """
        Define a subroutine in the class symbol table.

        Args:
            name: The subroutine name.
            symbol_type: The subroutine type.
            kind: The subroutine kind.
            is_void: Whether the subroutine returns void.
        """
        self.class_symbol_table.insert({
            'name': name,
            'type': symbol_type,
            'kind': kind,
            '#': self.add_id(name, symbol_type, kind),
            'void': is_void
        })

    def define(self, name: str, symbol_type: str, kind: str) -> None:
        """
        Define a class-level symbol.

        Args:
            name: The symbol name.
            symbol_type: The symbol type.
            kind: The symbol kind.
        """
        self.class_symbol_table.insert({
            'name': name,
            'type': symbol_type,
            'kind': kind,
            '#': self.add_id(name, symbol_type, kind)
        })

    def define_method(self, name: str, symbol_type: str, kind: str) -> None:
        """
        Define a method-level symbol.

        Args:
            name: The symbol name.
            symbol_type: The symbol type.
            kind: The symbol kind.
        """
        self.method_symbol_table.insert({
            'name': name,
            'type': symbol_type,
            'kind': kind,
            '#': self.add_id(name, symbol_type, kind)
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
        """Traverse both symbol tables (for debugging)."""
        self.class_symbol_table.traverse('x', '')
        self.method_symbol_table.traverse('x', '')

    def get_kind(self, identifier: str) -> Optional[str]:
        """
        Get the kind/segment of a symbol by its identifier.

        Args:
            identifier: The symbol name to look up.

        Returns:
            The VM segment name ('local', 'argument', 'static', 'this') or None.
        """
        kind_found = self.method_symbol_table.traverse('kind', identifier)
        if kind_found is not None:
            if kind_found == 'var':
                return 'local'
            elif kind_found == 'argument':
                return 'argument'
        else:
            static_or_field = self.class_symbol_table.traverse('kind', identifier)
            if static_or_field == 'static':
                return 'static'
            elif static_or_field == 'field':
                return 'this'
        return None

    def get_id(self, identifier: str) -> Optional[Union[int, str]]:
        """
        Get the index of a symbol by its identifier.

        Args:
            identifier: The symbol name to look up.

        Returns:
            The symbol's index or None if not found.
        """
        found_id = self.method_symbol_table.traverse('#', identifier)
        if found_id is not None:
            return found_id
        return self.class_symbol_table.traverse('#', identifier)

    def get_void(self, identifier: str) -> Optional[bool]:
        """
        Check if a subroutine returns void.

        Args:
            identifier: The subroutine name to look up.

        Returns:
            True if void, False if not, None if not found.
        """
        found_void = self.method_symbol_table.traverse('void', identifier)
        if found_void is not None:
            return found_void
        return self.class_symbol_table.traverse('void', identifier)
