import enum
import sys

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    SEMI = 4
    TYPE = 5
    CHAR = 6
    FLOAT = 7

    LABEL = 101
    GOTO = 102
    LET = 103
    IF = 104
    ELSE = 105
    ELIF = 106
    WHILE = 107
    INCLUDE = 108
    RETURN = 109
    FUNC = 110
    EXTERN = 111
    STRUCT = 112
    TYPEDEF = 113
    FOR = 114

    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    BANGEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211
    LPAREN = 212
    RPAREN = 213
    LBRACE = 214
    RBRACE = 215
    COMMA = 216
    HASH = 217
    DOT = 218
    LSQUARE = 219
    RSQUARE = 220
    LSHIFT = 221
    RSHIFT = 222
    BOR = 223
    BAND = 224
    LOR = 225
    LAND = 226

def ishex(c):
    if c in "abcdefABCDEF0123456789":
        return True
    else:
        return False

class Token:
    def __init__(self, text, kind):
        self.text = text
        self.kind = kind

    @staticmethod
    def checkIfKeyword(text):
        for kind in TokenType:
            if kind.name.lower() == text and kind.value >= 100 and kind.value < 200:
                return kind
        return None

class Lexer:
    def __init__(self, source):
        self.source = source + '\n'
        self.current = ''
        self.pos = -1
        self.nextChar()

    def nextChar(self):
        self.pos += 1
        if self.pos >= len(self.source):
            self.current = '\0'
        else:
            self.current = self.source[self.pos]

    def peek(self):
        if self.pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.pos + 1]

    def abort(self, reason):
        sys.exit("akuc: \033[31;1mlexer\033[0m: " + reason)
    
    def skipWhitespace(self):
        while self.current == ' ' or self.current == '\t' or self.current == '\r':
            self.nextChar()

    def skipComment(self):
        if self.current == '/':
            self.nextChar()
            if self.current == '/':
                while self.current != '\n':
                    self.nextChar()
            elif self.current == '*':
                self.nextChar()
                while not (self.current == '*' and self.peek() == '/'):
                    self.nextChar()
                self.nextChar()
                self.nextChar()
 
    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None

        if self.current == '+':
            token = Token(self.current, TokenType.PLUS)
        elif self.current == '-':
            token = Token(self.current, TokenType.MINUS)
        elif self.current == '*':
            token = Token(self.current, TokenType.ASTERISK)
        elif self.current == '/':
            token = Token(self.current, TokenType.SLASH)
        elif self.current == '=':
            if self.peek() == '=':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.EQEQ)
            else:
                token = Token(self.current, TokenType.EQ)
        elif self.current == '>':
            if self.peek() == '=':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.GTEQ)
            elif self.peek() == '>':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.RSHIFT)
            else:
                token = Token(self.current, TokenType.GT)
        elif self.current == '<':
            if self.peek() == '=':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.LTEQ)
            elif self.peek() == '<':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.LSHIFT)
            else:
                token = Token(self.current, TokenType.LT)
        elif self.current == '!':
            if self.peek() == '=':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.BANGEQ)
            else:
                self.abort("expected !=, got !`%s`" % self.peek())
        elif self.current == '|':
            if self.peek() == '|':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.LOR)
            else:
                token = Token(self.current, TokenType.BOR)
        elif self.current == '&':
            if self.peek() == '&':
                lastChar = self.current
                self.nextChar()
                token = Token(lastChar + self.current, TokenType.LAND)
            else:
                token = Token(self.current, TokenType.BAND)
        elif self.current == '\"':
            self.nextChar()
            startPos = self.pos
            marked = False

            while not (not marked and self.current == '\"'):
                marked = False
                if self.current == '\r' or self.current == '\n' or self.current == '\t':
                    self.abort("illegal character for string")
                if self.current == '\\':
                    marked = True
                self.nextChar()

            tokText = self.source[startPos:self.pos]
            token = Token(tokText, TokenType.STRING)
        elif self.current == '\'':
            self.nextChar()
            startPos = self.pos
            allowed = 1
            marked = False

            while not (not marked and self.current == '\''):
                marked = False
                if not self.current.isascii():
                    self.abort("character exceeds ASCII range 0-255")
                if self.current == '\r' or self.current == '\n' or self.current == '\t':
                    self.abort("illegal escape in character")
                if self.current == '\\':
                    marked = True
                    allowed = 2
                self.nextChar()

            tokText = self.source[startPos:self.pos]
            if self.pos - startPos > allowed:
                self.abort("character of illegal length `%s`" % (self.pos - startPos))
            token = Token(tokText, TokenType.CHAR)
        elif self.current.isdigit():
            if self.peek() != 'x':
                startPos = self.pos
                isFloat = False

                while self.peek().isdigit():
                    self.nextChar()
                if self.peek() == '.':
                    isFloat = True
                    self.nextChar()
                    while self.peek().isdigit():
                        self.nextChar()
                    
            
                tokText = self.source[startPos:self.pos + 1]
                if not isFloat:
                    token = Token(tokText, TokenType.NUMBER)
                else:
                    token = Token(tokText, TokenType.FLOAT)
            else:
                self.nextChar()
                self.nextChar()
                startPos = self.pos
                while ishex(self.peek()):
                    self.nextChar()
            
                tokText = self.source[startPos:self.pos + 1]
                token = Token(str(int(tokText, 16)), TokenType.NUMBER)


        elif self.current == '@':
            startPos = self.pos + 1
            while self.peek().isalnum() or self.peek() == '_':
                self.nextChar()

            tokText = self.source[startPos:self.pos + 1]
            keyword = Token.checkIfKeyword(tokText)
            token = Token(tokText, TokenType.TYPE)

        elif self.current == '#':
            token = Token(self.current, TokenType.HASH)

        elif self.current.isalpha():
            startPos = self.pos
            while self.peek().isalnum() or self.peek() == '_':
                self.nextChar()

            tokText = self.source[startPos:self.pos + 1]
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None:
                token = Token(tokText, TokenType.IDENT)
            else:
                token = Token(tokText, keyword)
        elif self.current == '(':
            token = Token(self.current, TokenType.LPAREN)
        elif self.current == ')':
            token = Token(self.current, TokenType.RPAREN)
        elif self.current == '{':
            token = Token(self.current, TokenType.LBRACE)
        elif self.current == '}':
            token = Token(self.current, TokenType.RBRACE)
        elif self.current == ';':
            token = Token(self.current, TokenType.SEMI)
        elif self.current == ',':
            token = Token(self.current, TokenType.COMMA)
        elif self.current == '.':
            token = Token(self.current, TokenType.DOT)
        elif self.current == '[':
            token = Token(self.current, TokenType.LSQUARE)
        elif self.current == ']':
            token = Token(self.current, TokenType.RSQUARE)
        elif self.current == '\n':
            token = Token(self.current, TokenType.NEWLINE)
        elif self.current == '\0':
            token = Token('', TokenType.EOF)
        else:
            self.abort("unknown token `" + self.current + "`")

        self.nextChar()
        return token
