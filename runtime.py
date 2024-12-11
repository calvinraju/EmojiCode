class Interpreter:
    def __init__(self):
        self.variables = {}

    def run_model(self, model):
        for stmt in model.statements:
            self.run_statement(stmt)

    def run_statement(self, stmt):
        cls_name = stmt.__class__.__name__
        if cls_name == 'Assignment':
            value = self.eval_expression(stmt.expr)
            self.variables[stmt.var.name] = value
        elif cls_name == 'Print':
            value = self.eval_expression(stmt.value)
            print(value)
        elif cls_name == 'ForLoop':
            self.run_for_loop(stmt)
        elif cls_name == 'WhileLoop':
            self.run_while_loop(stmt)
        elif cls_name == 'Block':
            self.run_block(stmt)
        elif cls_name in ['Expression', 'AddSub', 'MulDiv', 'Number', 'String', 'VarRef', 'OrExpr', 'AndExpr', 'RelExpr', 'Primary', 'BooleanLiteral', 'TrueLiteral', 'FalseLiteral']:
            self.eval_expression(stmt)
        else:
            raise ValueError(f"Unknown statement type: {cls_name}")
        
    def run_block(self, block):
        for stmt in block.statements:
            self.run_statement(stmt)

    def run_for_loop(self, for_loop):
        # for_loop: init=Assignment; cond=Expression; step=Assignment; block=Block
        self.run_statement(for_loop.init)

        while self.eval_expression(for_loop.cond) != 0:
            self.run_block(for_loop.block)
            self.run_statement(for_loop.step)

    def run_while_loop(self, while_loop):
        # while_loop: cond=Expression; block=Block
        while self.eval_expression(while_loop.cond) != 0:
            self.run_block(while_loop.block)

    def eval_expression(self, expr):
        cls_name = expr.__class__.__name__
        if cls_name == 'OrExpr':
            return self.eval_or_expr(expr)
        elif cls_name == 'AndExpr':
            return self.eval_and_expr(expr)
        elif cls_name == 'RelExpr':
            return self.eval_rel_expr(expr)
        elif cls_name == 'AddSub':
            return self.eval_addsub(expr)
        elif cls_name == 'MulDiv':
            return self.eval_muldiv(expr)
        elif cls_name == 'Number':
            return int(expr.num)  # Convert the string digits to int
        elif cls_name == 'String':
            return expr.val[1:-1]  # Remove the quotes from the matched string
        elif cls_name == 'VarRef':
            var_name = expr.name
            if var_name not in self.variables:
                raise NameError(f"Variable '{var_name}' not defined.")
            return self.variables[var_name]
        elif cls_name == 'BooleanLiteral':
            return self.eval_bool_literal(expr)
        elif cls_name == 'Primary':
            return self.eval_primary(expr)
        else:
            raise ValueError(f"Unknown expression type: {cls_name}")
        
    def eval_primary(self, primary):
        # Primary: Number | String | VarRef | BooleanLiteral | '(' Expression ')'
        for c in primary._tx_children:
            if c.__class__.__name__ == 'Expression' or 'OrExpr' in c.__class__.__name__:
                return self.eval_expression(c)
        raise ValueError("Parenthesized expression not found in primary.")
        
    def eval_or_expr(self, expr):
        # OrExpr: left=AndExpr ((op=OrOp) right=AndExpr)*
        value = self.eval_expression(expr.left)
        if hasattr(expr, 'op'):
            for op, r in zip(expr.op, expr.right):
                rval = self.eval_expression(r)
                # Both value and rval should be boolean for logical ops
                value = self.to_bool(value)
                rval = self.to_bool(rval)
                if op == '⛓️':  # OR
                    value = value or rval
                else:
                    raise ValueError(f"Unknown OR operator: {op}")
        return value
    
    def eval_bool_literal(self, expr):
        for c in expr._tx_children:
            cls_name = c.__class__.__name__
            if cls_name == 'TrueLiteral':
                return True
            elif cls_name == 'FalseLiteral':
                return False
        raise ValueError(f"Unknown boolean literal: {expr}")
    
    def eval_and_expr(self, expr):
        # AndExpr: left=RelExpr ((op=AndOp) right=RelExpr)*
        value = self.eval_expression(expr.left)
        if hasattr(expr, 'op'):
            for op, r in zip(expr.op, expr.right):
                rval = self.eval_expression(r)
                value = self.to_bool(value)
                rval = self.to_bool(rval)
                if op == '🔗':  # AND
                    value = value and rval
                else:
                    raise ValueError(f"Unknown AND operator: {op}")
        return value
    
    def eval_rel_expr(self, expr):
        # RelExpr: left=AddSub ((op=RelOp) right=AddSub)?
        value = self.eval_addsub(expr.left)
        if hasattr(expr, 'op') and expr.op:
            op = expr.op[0]
            right_expr = expr.right[0]
            rval = self.eval_addsub(right_expr)
        
            if not (isinstance(value, int) and isinstance(rval, int)):
                raise TypeError("Relational operators require integer operands.")

            if op == '🤝':
                return value == rval
            elif op == '🚫':
                return value != rval
            elif op == '👈':
                return value < rval
            elif op == '👉':
                return value > rval
            elif op == '🪜':
                return value <= rval
            elif op == '⛰️':
                return value >= rval
            else:
                raise ValueError(f"Unknown relational operator: {op}")
        else:
            return value

    def eval_addsub(self, expr):
        # expr.left is a MulDiv
        value = self.eval_muldiv(expr.left)
        for op, r in zip(expr.op, expr.right):
            rval = self.eval_muldiv(r)
            if not (isinstance(value, int) and isinstance(rval, int)):
                raise TypeError(f"Add/Sub requires integers, got '{value}' and '{rval}'")
            if op == '➖':
                value = value - rval
            elif op == '➕':
                value = value + rval
            else:
                raise ValueError(f"Unknown operator: {op}")
        return value

    def eval_muldiv(self, expr):
        # expr.left is a Primary
        value = self.eval_expression(expr.left)
        for op, r in zip(expr.op, expr.right):
            rval = self.eval_expression(r)
            if not (isinstance(value, int) and isinstance(rval, int)):
                raise TypeError(f"Mul/Div requires integers, got '{value}' and '{rval}'")
            if op == '✖️':
                value = value * rval
            elif op == '➗':
                if rval == 0:
                    raise ZeroDivisionError("Division by zero")
                value = value // rval
            else:
                raise ValueError(f"Unknown operator: {op}")
        return value
    
    def to_bool(self, val):
        # Convert value to boolean if not already
        # Integers: non-zero is True, zero is False
        # Strings: non-empty True, empty False (if desired)        
        if isinstance(val, bool):
            return val
        elif isinstance(val, int):
            return val != 0
        elif isinstance(val, str):
            return len(val) != 0
        else:
            # Default conversion, try Python's bool
            return bool(val)
