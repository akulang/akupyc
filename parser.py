import sys
from lexer import *
import random
import string

class Parser:
    def __init__(self, lexer, emitter, usestdlib):
        self.lexer = lexer
        self.emitter = emitter
        self.usestdlib = usestdlib

        self.globals = dict()
        self.locals = dict()
        self.types = set()
        self.types.add('int')
        self.types.add('int8')
        self.types.add('int16')
        self.types.add('int32')
        self.types.add('int64')
        self.types.add('char')
        self.types.add('double')
        self.types.add('uint8')
        self.types.add('uint16')
        self.types.add('uint32')
        self.types.add('uint64')
        self.types.add('void')
        self.types.add('string')
        self.structs = set()
        self.structsymbols = dict()
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
                if not name in self.globals.keys():
                    self.globals[name] = fctype
                else:
                    self.abort("function `%s` already declared")
                self.nextToken()
                self.match(TokenType.LPAREN)
                self.locals[name] = dict()
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
                        self.locals[name][self.curToken.text] = ftype
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

                if fctype == 'string':
                    fctype = 'char*'
                self.emitter.functionLine("{} {}({})".format(fctype, name, ', '.join(args)) + "{")

                while self.checkToken(TokenType.NEWLINE):
                    self.nextToken()

                while not self.checkToken(TokenType.RBRACE):
                    self.statement(self.emitter.functionLine, self.emitter.function, self.locals[name])

                self.match(TokenType.RBRACE)
                self.emitter.functionLine("}")
            else:
                # anon function
                pass

        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            porfunc("while(")
            self.match(TokenType.LPAREN)
            self.comparison(porfunc, scope)

            self.match(TokenType.RPAREN)
            self.match(TokenType.LBRACE)

            linefunc("){")

            while self.checkToken(TokenType.NEWLINE):
                self.nextToken()

            while not self.checkToken(TokenType.RBRACE):
                self.statement(linefunc, porfunc, scope)

            self.match(TokenType.RBRACE)
            linefunc("}")

        elif self.checkToken(TokenType.FOR):
            '''
            self.nextToken()
            self.match(TokenType.LPAREN)

            rid = 'for' + ''.join([random.choice(string.ascii_letters) for n in range(4)])
            self.locals[rid] = dict()

            porfunc("for(")
            if self.checkToken(TokenType.TYPE):
                ftype = self.curToken.text
                if not ftype in self.types:
                    self.abort("type does not exist `%s`" % ftype)
                self.nextToken()
                name = self.curToken.text
                self.match(TokenType.IDENT)
                self.match(TokenType.EQ)
                porfunc("%s %s = " % (ftype, name))
                self.expression(porfunc, scope)
                self.match(TokenType.SEMI)
                self.locals[rid][name] = ftype
                porfunc(";")
                
            else:
                self.match(TokenType.SEMI)
                porfunc(";")

            if self.checkToken(TokenType.SEMI):
                self.match(TokenType.SEMI)
                porfunc(";")
            else:
                self.comparison(porfunc, self.locals[rid])
                self.match(TokenType.SEMI)
                porfunc(";")
            
            print(self.curToken.kind.name)
            self.primary(porfunc, self.locals[rid])
            self.match(TokenType.RPAREN)
            linefunc("){")
            self.match(TokenType.LBRACE)

            while self.checkToken(TokenType.NEWLINE):
                self.nextToken()
            
            while not self.checkToken(TokenType.RBRACE):
                self.statement(linefunc, porfunc, self.locals[rid])

            self.match(TokenType.RBRACE)
            linefunc("}")'''

        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.match(TokenType.LPAREN)
            porfunc("if(")
            self.comparison(porfunc, scope)

            self.match(TokenType.RPAREN)
            self.match(TokenType.LBRACE)
            linefunc("){")

            while self.checkToken(TokenType.NEWLINE):
                self.nextToken()

            while not self.checkToken(TokenType.RBRACE):
                self.statement(linefunc, porfunc, scope)

            self.match(TokenType.RBRACE)
            porfunc("}")
            if self.checkToken(TokenType.ELIF):
                while self.checkToken(TokenType.ELIF):
                    self.nextToken()
                    self.match(TokenType.LPAREN)
                    porfunc(" else if(")
                    self.comparison(porfunc, scope)
                    self.match(TokenType.RPAREN)
                    linefunc("){")
                    self.match(TokenType.LBRACE)

                    while self.checkToken(TokenType.NEWLINE):
                        self.nextToken()

                    while not self.checkToken(TokenType.RBRACE):
                        self.statement(linefunc, porfunc, scope)

                    if not self.checkToken(TokenType.RBRACE):
                        self.abort("expected RBRACE, got " + self.curToken.kind.name)
                    porfunc("}")
                    self.nextToken()
                
                if self.checkToken(TokenType.ELSE):
                    self.nextToken()
                    linefunc(" else {")
                    self.match(TokenType.LBRACE)

                    while self.checkToken(TokenType.NEWLINE):
                        self.nextToken()

                    while not self.checkToken(TokenType.RBRACE):
                        self.statement(linefunc, porfunc, scope)

                    self.match(TokenType.RBRACE)
                    porfunc("}\n")

            elif self.checkToken(TokenType.ELSE):
                self.nextToken()
                linefunc(" else {")
                self.match(TokenType.LBRACE)

                while self.checkToken(TokenType.NEWLINE):
                    self.nextToken()

                while not self.checkToken(TokenType.RBRACE):
                    self.statement(linefunc, porfunc, scope)

                self.match(TokenType.RBRACE)
                porfunc("}\n")
            else:
                porfunc("\n")


        elif self.checkToken(TokenType.INCLUDE):
            self.nextToken()
            lib = self.curToken.text
            self.match(TokenType.STRING)
            self.cheaders.add(lib)

        elif self.checkToken(TokenType.EXTERN):
            self.nextToken()
            self.globals[self.curToken.text] = '@void'
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
                self.structsymbols[name] = self.structsymbols[ortype]
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
            self.structsymbols[name] = set()
            while self.checkToken(TokenType.NEWLINE):
                self.nextToken()
                
            while not self.checkToken(TokenType.RBRACE):
                stype = self.curToken.text
                self.match(TokenType.TYPE)
                sname = self.curToken.text
                self.match(TokenType.IDENT)
                self.match(TokenType.SEMI)
                self.match(TokenType.NEWLINE)
                if stype != "string":
                    self.emitter.macro("\t%s %s;\n" % (stype, sname))
                else:
                    self.emitter.macro("\tchar* %s;\n" % (sname))
                self.structsymbols[name].add(sname)

            self.match(TokenType.RBRACE)
            self.emitter.macro("};\n")
        
        elif self.checkToken(TokenType.IDENT):
            name = self.curToken.text
            self.nextToken()
            if self.checkToken(TokenType.LPAREN): # func call
                if not name in scope.keys():
                    if not name in self.globals.keys():
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
            if name in scope.keys():
                self.abort("symbol `%s` already declared in scope" % name)
            elif name in self.globals.keys():
                self.abort("symbol `%s` already declared" % name)
            else:
                scope[name] = ftype

            self.match(TokenType.EQ)
            if not self.checkToken(TokenType.LBRACE):
                if ftype != 'string':
                    porfunc("%s %s = " % (ftype, name))
                else:
                    porfunc("char* %s = " % (name))
                self.expression(porfunc, scope)
                linefunc(";")
            else:
                self.nextToken()
                if not ftype in self.types:
                    self.abort("attempting to initialize a type that doesn't exist `%s`" % ftype)
                porfunc("%s %s = { " % (ftype, name))
                while not self.checkToken(TokenType.RBRACE):
                    self.expression(porfunc, scope)
                    if self.checkToken(TokenType.COMMA):
                        porfunc(", ")
                        self.nextToken()
                
                porfunc(" };\n")
                self.structsymbols[name] = self.structsymbols[ftype]
                self.match(TokenType.RBRACE)

        else:
            self.abort("invalid statement at " + self.curToken.text + "(" + self.curToken.kind.name + ")")

        self.match(TokenType.SEMI)
        self.nl()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.BANGEQ)

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

    def comparison(self, porfunc, scope):
        self.expression(porfunc, scope)

        if self.isComparisonOperator():
            porfunc(self.curToken.text)
            self.nextToken()
            self.expression(porfunc, scope)

        while self.isComparisonOperator():
            porfunc(self.curToken.text)
            self.nextToken()
            self.expression(porfunc, scope)



    def primary(self, porfunc, scope):

        if self.checkToken(TokenType.NUMBER):
            porfunc(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            ename = self.curToken.text
            if self.checkPeek(TokenType.LPAREN): # func call
                self.nextToken()
                if not ename in scope.keys():
                    if not ename in self.globals.keys():
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
            elif self.checkPeek(TokenType.DOT): # struct property
                self.nextToken()
                self.nextToken()
                prop = self.curToken.text
                self.match(TokenType.IDENT)
                if not ename in scope.keys():
                    if not ename in self.globals.keys():
                        self.abort("referencing a symbol that isn't assigned yet or doesn't exist `%s`" % ename)
                
                if not prop in self.structsymbols[ename]:
                    self.abort("struct `%s` does not have property `%s`" % (ename, prop))
                porfunc("%s.%s" % (ename, prop))
            elif self.checkToken(TokenType.PLUS):
                print(self.curToken.kind.name)
                self.nextToken()
                self.match(TokenType.PLUS)
                porfunc("%s++" % ename)
                
            else:
                if ename not in scope:
                    self.abort("referencing a symbol that isn't assigned yet or doesn't exist `%s`" % ename)
            
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
            self.statement(self.emitter.emitLine, self.emitter.emit, self.globals)

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