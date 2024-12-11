from textx import metamodel_from_file, TextXSyntaxError
from runtime import Interpreter

if __name__ == "__main__":
    # Load the grammar with autokwd disabled to rely only on our defined rules
    mm = metamodel_from_file('emojiLang.tx', autokwd=False)

    code = '''
    ⭐️ x 📝 123
    🖨 x
    ⭐️ y 📝 "Hello World"
    🖨 y
    
    '''
    model = mm.model_from_str(code)
    interpreter = Interpreter()
    interpreter.run_model(model)

# ➕ ➖ ✖️ ➗ 📝 ⭐️ 🖨 🔁
