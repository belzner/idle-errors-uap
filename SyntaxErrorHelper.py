from tkinter import END
import io
import tokenize

ERR_PAREN = "You may have forgotten a closing paren on line "

def missingClosingParen(line):
    parens = 0
    for i in range(len(line)):
        if line[i] == '(':
            parens += 1
        if line[i] == ')':
            parens -= 1
    return parens > 0

def writeSyntaxError(shell, value, text):
    # I don't know what to do with text yet, but it'll probably
    # be useful for processing
    msg = getattr(value, 'msg', '') or value or "<no detail available>"
    lineno = getattr(value, 'lineno', '') or 1
    linepos = "startpos + %d lines" % (lineno-1)
    errorline = text.get(linepos, linepos+" lineend")
    if errorline.startswith('>>> '):
        errorline = errorline[4:]
    print(errorline)

    # Hacky way of checking for missing trailing parens
    extramsg = ""
    try:
        compile(errorline.strip(), "tmp.py", "exec")
    except SyntaxError as se:
        # Check for error on last line of file
        if "unexpected EOF while parsing" in str(se) and missingClosingParen(errorline):
            extramsg = ERR_PAREN + str(lineno-1)
    else: # The error is not in this line, check the previous line
        previousline = text.get(linepos+" -1l linestart", linepos+" -1l lineend")
        print(previousline)
        if missingClosingParen(previousline): # More opening parens than closing parens
            extramsg = ERR_PAREN + str(lineno-1)

    shell.write("\nSyntaxError: "+msg+"\n"+extramsg+"\n")
    shell.tkconsole.showprompt()
