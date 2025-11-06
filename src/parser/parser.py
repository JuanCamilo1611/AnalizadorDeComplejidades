from pathlib import Path
try:
    from lark import Lark, Transformer
except ImportError as e:
    raise RuntimeError("Falta la dependencia 'lark'. Instálala con: python -m pip install lark") from e

# Resolve grammar path relative to this file
GRAMMAR_PATH = Path(__file__).resolve().parent / "grammar.lark"

with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr", propagate_positions=True, maybe_placeholders=False)

class ASTBuilder(Transformer):
    def start(self, items):
        return list(items)

    # simple representations: numbers -> int, var -> str, length_call -> ("length", "A")
    def number(self, n):
        return int(n[0])

    def var(self, name):
        return str(name[0])

    def array_access(self, items):
        return {"type": "array_access", "name": str(items[0]), "index": items[1]}

    def length_call(self, items):
        return {"type": "length", "name": str(items[0])}

    def neg(self, items):
        return f"(-{items[0]})"

    # expr and term: we return strings like "(a + b)" to keep it simple
    def expr(self, items):
        s = str(items[0])
        i = 1
        while i < len(items):
            op = str(items[i])
            right = str(items[i+1])
            s = f"({s} {op} {right})"
            i += 2
        return s

    def term(self, items):
        return self.expr(items)  # same handling

    # lvalue
    def lvalue(self, items):
        # items are sequences like ['A', '.', 'f', ['index'...]] but transformer already simplifies name & index
        # We'll produce a string representation
        parts = []
        for it in items:
            parts.append(str(it))
        return "".join(parts)

    def assignment(self, items):
        return {"type": "assign", "target": items[0], "value": items[1]}

    def block(self, items):
        return list(items)

    def for_stmt(self, items):
        # items: NAME, startExpr, endExpr, block
        return {"type": "for", "var": str(items[0]), "start": items[1], "end": items[2], "body": items[3]}

    def while_stmt(self, items):
        # items: condition, block
        return {"type": "while", "condition": items[0], "body": items[1]}

    def repeat_stmt(self, items):
        # items: block, condition
        return {"type": "repeat", "body": items[0], "condition": items[1]}

    def if_stmt(self, items):
        # items: condition, then_block, else_block
        return {
            "type": "if", 
            "condition": items[0], 
            "then": items[1], 
            "else": items[2] if len(items) > 2 else None
            }

    def call_stmt(self, items):
        name = str(items[0])
        args = items[1] if len(items) > 1 else []
        return {"type": "call", "name": name, "args": args}

    def arg_list(self, items):
        return list(items)

    def comment(self, items):
        return {"type": "comment"}

def parse_code(code: str):
    tree = parser.parse(code)
    ast = ASTBuilder().transform(tree)
    return ast
