import sys
from lexer import *

class Parser:
    def __init__(self, lexer, emitter, usestdlib):
        self.lexer = lexer
        self.emitter = emitter
        self.usestdlib = usestdlib

        self.symbols = set()
        self.types = set()
        self.types.add('int')
        self.types.add('int32')
        self.types.add('double')
        self.types.add('uint8')
        self.types.add('uint16')
        self.types.add('uint32')
        self.types.add('uint64')
        self.types.add('void')
        self.types.add('string')
        self.structs = set()
        self.labelsDeclared = set()
        self.labelsGotoed = set()
        self.cheaders = set()

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    def validType(self, typk):
        if typk in self.types:
            return True
        else:
            return False

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
        sys.exit("yuc: \033[31;1mparsing\033[0m: " + message + "")


    def nl(self):


        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def statement(self, linefunc, porfunc, scope):

        if self.checkToken(TokenType.FUNC):
            self.nextToken()
            fctype = self.curToken.text
            self.match(TokenType.TYPE)
            if not self.validType(fctype):
                self.abort("invalid type `%s`" % fctype)

            if self.checkToken(TokenType.IDENT):
                name = self.curToken.text
                if not name in scope:
                    scope.add(name)
                else:
                    self.abort("function `%s` already declared")
                self.nextToken()
                self.match(TokenType.LPAREN)
                args = []
                if self.checkToken(TokenType.TYPE):
                    ftype = self.curToken.text
                    if not self.validType(ftype):
                        self.abort("invalid type `%s`" % ftype)
                    self.nextToken()
                    if self.checkToken(TokenType.IDENT):
                        if ftype != "string":
                            args.append("%s %s" % (ftype, self.curToken.text))
                        else:
                            args.append("char* %s" % (self.curToken.text))
                        scope.add(self.curToken.text)
                        self.nextToken()
                        if not self.checkToken(TokenType.RPAREN):
                            if self.checkToken(TokenType.COMMA):
                                self.nextToken()
                            while self.checkToken(TokenType.TYPE):
                                if self.checkPeek(TokenType.IDENT):
                                    ftype = self.curToken.text
                                    if not self.validType(ftype):
                                        self.abort("invalid type `%s`" % ftype)
                                    self.nextToken()
                                    if ftype != "string":
                                        args.append("%s %s" % (ftype, self.curToken.text))
                                    else:
                                        args.append("char* %s" % (self.curToken.text))
                                    self.symbols.add(self.curToken.text)
                                    self.nextToken()
                                    if self.checkToken(TokenType.COMMA):
                                        self.nextToken()


                self.match(TokenType.RPAREN)
                self.match(TokenType.LBRACE)

                self.emitter.functionLine("{} {}({})".format(fctype, name, ', '.join(args)) + "{")

                while self.checkToken(TokenType.NEWLINE):
                    self.nextToken()

                while not self.checkToken(TokenType.RBRACE):
                    self.statement(self.emitter.functionLine, self.emitter.function, self.symbols)

                self.match(TokenType.RBRACE)
                self.emitter.functionLine("}")
            else:
                # anon function
                pass


        elif self.checkToken(TokenType.INCLUDE):
            self.nextToken()
            lib = self.curToken.text
            self.match(TokenType.STRING)
            self.cheaders.add(lib)

        elif self.checkToken(TokenType.EXTERN):
            self.nextToken()
            scope.add(self.curToken.text)
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.HASH):
            self.nextToken()
            htype = self.curToken.text
            self.match(TokenType.IDENT)
            if htype == "define":
                name = self.curToken.text
                self.match(TokenType.IDENT)
                if not name in scope:
                    scope.add(name)
                else:
                    self.abort("cannot define a macro that already exists")
                self.emitter.macro("#define %s " % name)
                self.expression(self.emitter.macro, scope)
                self.emitter.macro("\n")
            elif htype == "ifndef":
                name = self.curToken.text
                self.match(TokenType.IDENT)
                linefunc("#ifndef %s" % name)

            elif htype == "ifdef":
                name = self.curToken.text
                self.match(TokenType.IDENT)
                linefunc("#ifdef %s" % name)
            
            elif htype == "endif":
                name = self.curToken.text
                linefunc("#endif")

        elif self.checkToken(TokenType.TYPEDEF):
            self.nextToken()
            ortype = self.curToken.text
            self.nextToken()
            name = self.curToken.text
            self.types.add(name)
            self.match(TokenType.IDENT)
            if ortype in self.structs:
                self.emitter.macro("typedef struct %s %s;\n" % (ortype, name))
            else:
                self.emitter.macro("typedef %s %s;\n" % (ortype, name))
            
        elif self.checkToken(TokenType.STRUCT):
            self.nextToken()
            name = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.LBRACE)
            self.emitter.macro("struct %s {\n" % name)
            self.structs.add(name)
            while self.checkToken(TokenType.NEWLINE):
                self.nextToken()
                
            while not self.checkToken(TokenType.RBRACE):
                stype = self.curToken.text
                self.match(TokenType.TYPE)
                sname = self.curToken.text
                self.match(TokenType.IDENT)
                self.match(TokenType.SEMI)
                self.match(TokenType.NEWLINE)
                self.emitter.macro("\t%s %s;\n" % (stype, sname))

            self.match(TokenType.RBRACE)
            self.emitter.macro("};\n")
        
        elif self.checkToken(TokenType.IDENT):
            name = self.curToken.text
            self.nextToken()
            if self.checkToken(TokenType.LPAREN): # func call
                if not name in scope:
                    self.abort("function `%s` does not exist" % name)
                self.nextToken()
                porfunc("{}(".format(name))
                while not self.checkToken(TokenType.RPAREN):
                    self.expression(porfunc, scope)
                    if self.checkToken(TokenType.COMMA):
                        porfunc(", ")
                        self.nextToken()

                self.match(TokenType.RPAREN)
                linefunc(");")
            elif self.checkToken(TokenType.EQ): # symbol set
                self.match(TokenType.EQ)
                if name not in scope:
                    self.abort("symbol `%s` is not declared" % name)
                
                porfunc("%s = " % name)
                self.expression(porfunc, scope)
                linefunc(";")

        elif self.checkToken(TokenType.RETURN):
            self.nextToken()
            porfunc("return ")
            self.expression(porfunc, scope)
            linefunc(";")

        elif self.checkToken(TokenType.LABEL):
            self.nextToken()
            if self.curToken.text in self.labelsDeclared:
                self.abort("label already declared: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            linefunc(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            linefunc("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.TYPE):
            ftype = None
            ftype = self.curToken.text
            if not self.validType(ftype):
                self.abort("invalid type `%s`" % ftype)
            self.nextToken()

            name = self.curToken.text
            self.match(TokenType.IDENT)
            if name in self.symbols:
                self.abort("symbol already declared `%s`" % name)
            else:
                scope.add(name)

            self.match(TokenType.EQ)
            if ftype != 'string':
                porfunc("%s %s = " % (ftype, name))
            else:
                porfunc("char* %s = " % (name))
            self.expression(porfunc, scope)
            linefunc(";")

        else:
            self.abort("invalid statement at " + self.curToken.text + "(" + self.curToken.kind.name + ")")

        self.match(TokenType.SEMI)
        self.nl()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def term(self, porfunc, scope):

        self.unary(porfunc, scope)

        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            porfunc(self.curToken.text)
            self.nextToken()
            self.unary(porfunc, scope)

    def unary(self, porfunc, scope):

        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            porfunc(self.curToken.text)
            self.nextToken()
        self.primary(porfunc, scope)



    def primary(self, porfunc, scope):

        if self.checkToken(TokenType.NUMBER):
            porfunc(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            ename = self.curToken.text
            if self.checkPeek(TokenType.LPAREN): # func call
                self.nextToken()
                if not ename in scope:
                    self.abort("function `%s` does not exist" % ename)
                self.nextToken()
                porfunc("{}(".format(ename))
                while not self.checkToken(TokenType.RPAREN):
                    self.expression(porfunc, scope)
                    if self.checkToken(TokenType.COMMA):
                        porfunc(", ")
                        self.nextToken()

                self.match(TokenType.RPAREN)
                porfunc(")")
            else:
                if ename not in scope:
                    self.abort("referencing a symbol that isn't assigned yet or doesn't exist: " + ename)
            
                porfunc(ename)
                self.nextToken()
        elif self.checkToken(TokenType.STRING):
            porfunc("\"" + self.curToken.text + "\"")
            self.nextToken()
        else:
            self.abort("unexpected token at primary parsing: " + self.curToken.text)

    def expression(self, porfunc, scope):

        self.term(porfunc, scope)

        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            porfunc(self.curToken.text)
            self.nextToken()
            self.term(porfunc, scope)

    def program(self):
        self.emitter.headerLine("// generated by yuc\n")
        if self.usestdlib:
            self.emitter.headerLine("// yulib")
            self.emitter.headerLine("#include \"yulib.h\"\n\n")
        self.emitter.headerLine("// user headers")

        self.emitter.emit("\n\n")


        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement(self.emitter.emitLine, self.emitter.emit, self.symbols)

        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("attempted goto to undeclared label: " + label)

        for cheader in self.cheaders:
            self.emitter.headerLine("#include \"{}\"".format(cheader))
        self.emitter.headerLine("\n\n")

class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.headers = ""
        self.macros = ""
        self.functions = ""
        self.code = ""

    def emit(self, code):
        self.code += code

    def emitLine(self, code):
        self.code += code + '\n'

    def headerLine(self, code):
        self.headers += code + '\n'

    def macro(self, code):
        self.macros += code

    def functionLine(self, code):
        self.functions += code + '\n'

    def function(self, code):
        self.functions += code

    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.headers + self.macros + self.functions + self.code)