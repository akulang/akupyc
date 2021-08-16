#! /bin/python3

# AKUC - Aku Compiler

import sys
import os
from lexer import Lexer
from parser import Emitter, Parser
import argparse

def main():
    if(len(sys.argv) == 1):
        sys.exit("akuc: \033[31;1mfatal\033[0m: no input file specified.")
    elif(len(sys.argv) == 2):
        with open(sys.argv[1], 'r') as inputFile:
            input = inputFile.read()

        lexer = Lexer(input)
        emitter = Emitter("out.c")
        parser = Parser(lexer, emitter, True)

        parser.program()
        emitter.writeFile()
        os.system('gcc -g out.c lib/*.c -Ilib/ -o {}'.format(sys.argv[1].split(".")[0]))
        os.remove("out.c")
    elif(len(sys.argv) >= 3):
        with open(sys.argv[1], 'r') as inputFile:
            input = inputFile.read()

        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--out", help="compiled output file", action="store", default=sys.argv[1].split(".")[0])
        parser.add_argument("--nostdlib", help="don't include stdlib", action="store_true")
        parser.add_argument("-c", "--outasc", help="output C code instead of compiling", action="store_true")
        parser.add_argument("--includeo", help="include object files", action="append", nargs="+")
        parser.add_argument("--usecc", help=argparse.SUPPRESS, action="store")
        parser.add_argument("--baremetal", help="compile yu for bare metal", action="store_true")
        parser.add_argument("--dryrun", help="print gcc backend command", action="store_true")

        args = parser.parse_args(sys.argv[2:])

        extraflags = []
        if args.baremetal:
            extraflags.append("-std=gnu99 -ffreestanding -Wall -Wextra")
            args.nostdlib = True

        if not os.path.exists(sys.argv[1]):
            sys.exit("yuc: \033[31;1mfatal\033[0m: input file does not exist.")

        lexer = Lexer(input)
        outC = "out" + sys.argv[1].split('.')[0] + ".c"
        emitter = Emitter(outC)
        parser = Parser(lexer, emitter, not args.nostdlib)

        parser.program()
        emitter.writeFile()
        compiler = "gcc"
        if args.usecc:
            compiler = args.usecc
        
        rawcincludes = []
        if args.includeo:
           rawcincludes = args.includeo 

        cincludes = []
        for item in rawcincludes:
            for itemx in item:
                cincludes.append(itemx)

        if not args.outasc:
            if not args.nostdlib:
                cmd = '{} {} {} lib/*.c -Ilib/ {} -o {}'.format(compiler, outC, ' '.join(cincludes), ' '.join(extraflags), args.out)
                if args.dryrun:
                    print(cmd)
                else:
                    os.system(cmd)
            else:
                cmd = '{} -c {} {} {} -o {}'.format(compiler, outC, ' '.join(cincludes), ' '.join(extraflags), args.out)
                if args.dryrun:
                    print(cmd)
                else:
                    os.system(cmd)

        if not args.outasc:
            os.remove(outC)

main()
