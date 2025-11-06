import re

# Modulo minimo para transformar AST en complejidad temporal O, Omega, Theta
# basado en reglas simples y heurísticas.


# heurística: detecta si una expresión depende de "n" o length(...)
def depends_on_n(expr):
    if expr is None:
        return False
    s = str(expr)
    # busca 'n', 'length(' o 'length ' o 'len' (heurístico)
    if re.search(r'\b(n|N|length|len|length\()', s):
        return True
    # si existe una letra (variable) en el bound, asumimos dependencia a tamaño
    if re.search(r'[a-zA-Z]', s) and not re.match(r'^\d+$', s):
        return True
    return False

def deg_to_str(d):
    if d == "?" or d is None:
        return "?"
    if d == 0:
        return "1"
    if d == 1:
        return "n"
    return f"n^{d}"

def complexity_from_ast(ast):
    """
    Devuelve dict { "O": "O(...)", "Omega": ..., "Theta": ... }
    AST esperado: lista de statements (como produce parser.parse_code)
    """
    worst_deg = degree_block(ast, mode="worst")
    best_deg  = degree_block(ast, mode="best")

    if worst_deg == best_deg:
        theta = worst_deg
    else:
        theta = None

    return {
        "O": f"O({deg_to_str(worst_deg)})" if worst_deg != "?" else "O(?)",
        "Omega": f"Ω({deg_to_str(best_deg)})" if best_deg != "?" else "Ω(?)",
        "Theta": f"Θ({deg_to_str(theta)})" if theta is not None else "Θ(?)"
    }

def degree_block(block, mode="worst"):
    """
    block: list of statements
    mode: "worst" or "best"
    Regla: secuencia -> tomar max(deg(stmt_i))
    """
    if not block:
        return 0
    degrees = [degree_stmt(s, mode) for s in block]
    # secuencia: tomar el mayor (dominante)
    # si alguna es "?" devolvemos "?"
    if any(d == "?" for d in degrees):
        return "?"
    return max(degrees)

def degree_stmt(stmt, mode="worst"):
    if stmt is None:
        return 0
    t = stmt.get("type") if isinstance(stmt, dict) else None
    if t is None:
        return 0

    if t == "assign":
        return 0

    if t == "comment":
        return 0

    if t == "call":
        # asumimos llamada coste constante por ahora (no-recursiva)
        return 0

    if t == "for":
        # detectamos si el límite depende de n
        end = stmt.get("end")
        loop_factor = 1 if depends_on_n(end) else 0
        body_deg = degree_block(stmt.get("body", []), mode)
        if body_deg == "?":
            return "?"
        # cuando el cuerpo es secuencial, su grado se multiplica por el factor: grado_total = loop_factor + body_deg
        return loop_factor + body_deg

    if t == "while":
        cond = stmt.get("condition")
        # heurística: si condición contiene n -> factor 1, else unknown -> ?
        loop_factor = 1 if depends_on_n(cond) else 0
        body_deg = degree_block(stmt.get("body", []), mode)
        if body_deg == "?":
            return "?"
        return loop_factor + body_deg

    if t == "repeat":
        # repeat-until similar a while
        cond = stmt.get("condition")
        loop_factor = 1 if depends_on_n(cond) else 0
        body_deg = degree_block(stmt.get("body", []), mode)
        if body_deg == "?":
            return "?"
        return loop_factor + body_deg

    if t == "if":
        then_deg = degree_block(stmt.get("then", []), mode)
        else_deg = degree_block(stmt.get("else", []), mode)
        if then_deg == "?" or else_deg == "?":
            return "?"
        if mode == "worst":
            return max(then_deg, else_deg)
        else:
            return min(then_deg, else_deg)

    # fallback
    return "?"

# --- función de ayuda para usar desde main.py ---
def analyze(ast):
    return complexity_from_ast(ast)
