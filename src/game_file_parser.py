"""Tokenizer and tree parser for the game's brace-delimited data format.

The game's .def/.inc/.ext/.set files use an s-expression-like format with
curly-brace blocks, parenthesized calls, quoted strings, and semicolon
comments. Parsing them with line scanning and whitespace-sensitive
terminators is fragile, so this module provides a single real parser that
produces a node tree; extractors then query the tree instead of lines.
"""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class GameNode:
    """One block or call in the game data tree.

    Attributes:
        kind: "block" for {name ...}, "call" for (name ...)
        name: First token of the block/call, or "" if empty
        args: Scalar arguments following the name (strings)
        children: Nested GameNode children in order of appearance
    """

    kind: str
    name: str = ""
    args: list[str] = field(default_factory=list)
    children: list["GameNode"] = field(default_factory=list)

    def children_named(self, name: str, kind: str | None = None) -> list["GameNode"]:
        """Return direct children with the given name (and optional kind)."""
        return [
            child
            for child in self.children
            if child.name == name and (kind is None or child.kind == kind)
        ]

    def iter_descendants(self) -> Iterator["GameNode"]:
        """Yield this node and all descendants depth-first.

        Implemented iteratively so deeply nested or unbalanced input cannot
        exceed the Python recursion limit.
        """
        stack: list[GameNode] = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def find_descendants(self, name: str, kind: str | None = None) -> list["GameNode"]:
        """Return all descendants (any depth) with the given name."""
        return [
            node
            for node in self.iter_descendants()
            if node.name == name and (kind is None or node.kind == kind)
        ]


def _tokenize(text: str) -> list[str]:
    """Split game data text into structural tokens.

    Tokens are "{", "}", "(", ")", quoted strings (quotes stripped), and bare
    atoms. Semicolon comments are removed, but not inside quoted strings.

    Args:
        text: Raw file content

    Returns:
        list[str]: Ordered token list
    """
    tokens: list[str] = []
    current: list[str] = []
    in_quote = False
    in_comment = False

    def flush_atom() -> None:
        if current:
            tokens.append("".join(current))
            current.clear()

    for char in text:
        if in_comment:
            if char == "\n":
                in_comment = False
            continue
        if in_quote:
            if char == '"':
                in_quote = False
                flush_atom()
            else:
                current.append(char)
            continue
        if char == ";":
            flush_atom()
            in_comment = True
            continue
        if char == '"':
            flush_atom()
            in_quote = True
            continue
        if char in "{}()":
            flush_atom()
            tokens.append(char)
            continue
        if char.isspace():
            flush_atom()
            continue
        current.append(char)
    flush_atom()
    return tokens


def parse_game_file(text: str) -> GameNode:
    """Parse game data text into a fully nested tree.

    Nested blocks and calls become children of their enclosing node.
    Unbalanced or truncated input does not raise; any blocks still open at
    end of input are implicitly closed so partially valid files still yield
    their data.

    Args:
        text: Raw file content

    Returns:
        GameNode: Synthetic root (kind "root") with nested children
    """
    tokens = _tokenize(text)
    root = GameNode(kind="root")
    stack: list[GameNode] = [root]

    for token in tokens:
        if token in "{(":
            kind = "block" if token == "{" else "call"
            node = GameNode(kind=kind)
            stack[-1].children.append(node)
            stack.append(node)
            continue
        if token in "})":
            if len(stack) > 1:
                stack.pop()
            continue
        current = stack[-1]
        if current.name == "" and current.kind != "root":
            current.name = token
        else:
            current.args.append(token)

    return root


def node_to_entry_string(node: GameNode) -> str:
    """Reconstruct a single-level entry string like the raw source line.

    Produces the form '\t{item "name" arg1 arg2}' that
    convert_breed_inventory_entry_to_game_item_info() expects, with the first
    argument re-quoted (item/weapon names contain spaces).

    Args:
        node: Node representing an {item ...} or {weapon ...} entry

    Returns:
        str: Reconstructed entry string
    """
    opener, closer = ("{", "}") if node.kind == "block" else ("(", ")")
    if not node.args:
        return f'\t{opener}{node.name} ""{closer}\n'
    quoted_first = f'"{node.args[0]}"'
    rest = " ".join(node.args[1:])
    body = f"{node.name} {quoted_first}"
    if rest:
        body = f"{body} {rest}"
    return f"\t{opener}{body}{closer}\n"
