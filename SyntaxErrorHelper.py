from tkinter import END
import io
import tokenize
import keyword

from HyperParser import HyperParser

ERR_PAREN = "You may have forgotten a closing bracket to match the opening bracket on line "
ERR_RESERVED = "You may have tried to use a reserved word as a variable name on line "

def writeSyntaxError(shell, value, win):
    text = win.text
    msg = getattr(value, 'msg', '') or value or "<no detail available>"
    lineno = getattr(value, 'lineno', '') or 1
    linepos = "startpos + %d lines" % (lineno-1)
    errorline = text.get(linepos, linepos+" lineend")
    if errorline.startswith('>>> '):
        errorline = errorline[4:]

    extramsg = ""

    # Check for missing closing bracket
    hasBrackets = (HyperParser(win, linepos)
                   .get_surrounding_brackets())
    if hasBrackets is not None: # Has brackets at all
        matchedBrackets = (HyperParser(win, linepos)
                           .get_surrounding_brackets(mustclose=True))
        if matchedBrackets is None: # No closing bracket
            extramsg = ERR_PAREN + hasBrackets[0].split('.')[0]

    # Check for using reserved word as variable name
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(bytes(errorline, 'utf-8')).readline))
        equalsPos = -1
        for i in range(len(tokens)):
            if tokens[i].exact_type is tokenize.EQUAL:
                equalsPos = i
                break
        if equalsPos > 0:
            for i in range(equalsPos):
                if tokens[i].type is tokenize.NAME and keyword.iskeyword(tokens[i].string):
                    extramsg = ERR_RESERVED + str(lineno)
    except Exception as e:
        print('error', e)

    shell.write("\nSyntaxError: "+msg+"\n"+extramsg+"\n")
    shell.tkconsole.showprompt()
