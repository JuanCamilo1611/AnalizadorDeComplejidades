from src.parser.parser import parse_code
from src.analyzer.complexity import analyze

code = """
if (x > 0) then
    begin
        y ← y + 1
    end
else
    begin
        y ← 0
    end
"""

ast = parse_code(code)
print("AST:")
import pprint; pprint.pprint(ast)

result = analyze(ast)
print("\nComplejidad estimada:")
pprint.pprint(result)
