import unicodedata
from typing import List

from lark import Lark, Transformer, UnexpectedInput, v_args


def get_greek_letters():
    greek_dict = {}
    for i in range(0x0391, 0x03A9 + 1):
        char = chr(i)
        name = unicodedata.name(char, '').replace('GREEK CAPITAL LETTER ', '')
        if name:
            greek_dict[name.title()] = char

    for i in range(0x03B1, 0x03C9 + 1):
        char = chr(i)
        name = unicodedata.name(char, '').replace('GREEK SMALL LETTER ', '')
        if name:
            greek_dict[name.lower()] = char

    greek_dict["Lambda"] = greek_dict["Lamda"]
    greek_dict["lambda"] = greek_dict["lamda"]

    return greek_dict


class LatexTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.greek_letters = get_greek_letters()
        self.symbols = {"rangle": "⟩", "langle": "⟨", "otimes": "⊗"}

    @staticmethod
    def to_string(items: List) -> str:
        return ''.join(str(item) for item in items)

    def formula(self, items: List) -> str:
        return LatexTransformer.to_string(items)

    def expr(self, items: List) -> str:
        return LatexTransformer.to_string(items)

    @v_args(inline=True)
    def text(self, text) -> str:
        return str(text)

    def superscript(self, items: List) -> str:
        return f'<sup>{LatexTransformer.to_string(items)}</sup>'

    def subscript(self, items: List) -> str:
        return f'<sub>{LatexTransformer.to_string(items)}</sub>'

    @v_args(inline=True)
    def fraction(self, numerator_list: List, denominator_list: List) -> str:
        numerator = LatexTransformer.to_string(numerator_list)
        denominator = LatexTransformer.to_string(denominator_list)
        return (f'<sup>{numerator}</sup>'
                f' ⁄ '
                f'<sub>{denominator}</sub>')

    def subexpr(self, items: List) -> str:
        return LatexTransformer.to_string(items)

    @v_args(inline=True)
    def symbol(self, symbol) -> str:
        symbol_name = str(symbol)
        if symbol_name in self.greek_letters:
            return self.greek_letters[symbol_name]
        if symbol_name in self.symbols:
            return self.symbols[symbol_name]
        return f'\\{symbol_name}'

    @v_args(inline=True)
    def letter(self, letter) -> str:
        return str(letter)

    def ket(self, items) -> str:
        return f'|{LatexTransformer.to_string(items)}⟩'


def latex_to_html(latex_formula: str) -> str:
    grammar = r"""
    formula: expr+

    expr:  superscript | subscript | fraction | symbol | text | letter | ket

    superscript: "^" subexpr | "^" letter
    subscript: "_" subexpr | "_" letter
    fraction: "\\frac" subexpr subexpr
    subexpr: "{" expr+ "}"
    ket: "\\ket" subexpr
    symbol: "\\" /[a-zA-Z]+/
    letter: /[a-zA-Z0-9+-]/
    text: /[^\\{}_^]+/
    
    %import common.WS
    %ignore WS
    """
    try:
        if latex_formula.startswith("$"):
            latex_formula = latex_formula[1:]
        if latex_formula.endswith("$"):
            latex_formula = latex_formula[:-1]
        tree = Lark(grammar, start='formula').parse(latex_formula)
        html = LatexTransformer().transform(tree)
        return html
    except UnexpectedInput:
        return latex_formula


if __name__ == "__main__":
    print(get_greek_letters())
