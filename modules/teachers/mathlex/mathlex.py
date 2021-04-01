from typing import *
import re


class Token:
    def __init__(self, kind: str, data: Union[str, list]):
        self.kind = kind.lower()
        self.data = data

    def __str__(self):
        if isinstance(self.data, list):
            s = self.kind + ":\n"
            for whatever in self.data:
                s += re.sub("^", "   ", str(whatever), flags = re.MULTILINE) + "\n"
            return s[:-1]       

        return "%s(%s)" % (self.kind, self.data)


class TokenDefinition:
    def __init__(self, kind: str, pattern: str, converter: Optional[Callable[[str], float]] = None):
        self.kind = kind.lower()
        self.pattern = pattern
        self.converter = converter


TOKEN_DEFINITIONS: List[TokenDefinition] = [
    TokenDefinition("word", "[a-zA-Z]+"),
    TokenDefinition("number", "\d+([.,]\d+)?", lambda s: float(s)),
    TokenDefinition("operator", "!=|==|<|>|<=|>=|=\/=|\/=|[+\-*\/^=]")
]


def tokenize(expression: str) -> List[Token]:
    """převede řetězec na seznam tokenů"""

    tokens = []

    while expression:
        # odstranit mezery ze začátku řetězce
        expression = expression.lstrip()
        if expression == "":
            break

        # zkontrolovat závorky
        if expression[0] == "(":
            depth = 1
            for i in range(1, len(expression)):
                if expression[i] == "(":
                    depth += 1
                elif expression[i] == ")":
                    depth -= 1
                    if depth == 0:
                        tokens.append(Token("subexpr", tokenize(expression[1:i])))
                        expression = expression[i+1:]
                        break
            continue

        foundToken = False

        # vzít token ze začátku řetězce
        for tokenDef in TOKEN_DEFINITIONS:
            match = re.match(tokenDef.pattern, expression)
            if match:
                text = match.group(0)
                value = tokenDef.converter(text) if tokenDef.converter else text
                tokens.append(Token(tokenDef.kind, value))
                expression = expression[len(text):]
                foundToken = True
                break

        if not foundToken:
            break
    
    return tokens
