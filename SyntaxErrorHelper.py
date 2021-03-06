from tkinter import END
import ast
import io
import tokenize
import keyword

from HyperParser import HyperParser

ERR_PAREN = "You may have forgotten a closing bracket to match the opening bracket on line %d"
ERR_RESERVED = "You may have tried to use the reserved word '%s' as a variable name on line %d"
ERR_COLON = "You may have forgotten a colon at the end of line %d"
ERR_ASSIGN = "You may have used '=' when you meant to use a comparison operator (such as '==') on line %d"

def writeSyntaxError(shell, value, win):
    text = win.text
    msg = getattr(value, 'msg', '') or value or "<no detail available>"
    lineno = getattr(value, 'lineno', '') or 1
    offset = getattr(value, 'offset', '') or 0
    linepos = "startpos + %d lines" % (lineno-1)
    prevcode = text.get("startpos", linepos+" linestart")
    errorline = text.get(linepos, linepos+" lineend")
    if prevcode.startswith('>>> '):
        prevcode = prevcode[4:]
    if errorline.startswith('>>> '):
        errorline = errorline[4:]

    extramsg = ""

    # Check for missing closing bracket
    hasBrackets = (HyperParser(win, linepos+" lineend")
                   .get_surrounding_brackets())
    if hasBrackets is not None: # Has brackets at all
        matchedBrackets = (HyperParser(win, linepos)
                           .get_surrounding_brackets(mustclose=True))
        if matchedBrackets is None: # No closing bracket
            extramsg = ERR_PAREN % int(hasBrackets[0].split('.')[0])
            text.tag_remove("ERROR", "1.0", "end")
            win.colorize_syntax_error(text, hasBrackets[0])

    try:
        tokens = list(tokenize.tokenize(io.BytesIO(bytes(errorline, 'utf-8')).readline))

        # Order of tests matters because of course it does

        # Check for missing colon at end of statement
        statementName = ''
        for i in range(len(tokens)):
            if tokens[i].type is tokenize.NAME:
                statementName = tokens[i].string
                break
        if statementName in ['if', 'elif', 'else', 'for', 'while', 'class', 'def']:
            hasColon = False
            for i in range(len(tokens))[::-1]:
                if tokens[i].exact_type is tokenize.COLON:
                    hasColon = True
                    break
            if not hasColon:
                extramsg = ERR_COLON % lineno

        # Check for using = (assignment) in if/elif/while
        if statementName in ['if', 'elif', 'while']:
            for i in range(len(tokens)):
                if tokens[i].exact_type is tokenize.EQUAL:
                    extramsg = ERR_ASSIGN % lineno
                    break

        # Check for using reserved word as variable name (assignment)
        equalsPos = -1
        for i in range(len(tokens)):
            if tokens[i].exact_type is tokenize.EQUAL:
                equalsPos = i
                break
        if equalsPos > 0 and tokens[equalsPos-1].type is tokenize.NAME:
            for i in range(equalsPos)[::-1]:
                if tokens[i].type is tokenize.NAME:
                    if keyword.iskeyword(tokens[i].string):
                        extramsg = ERR_RESERVED % (tokens[i].string, lineno)
                        break
                    else:
                        if i > 0 and tokens[i-1].exact_type is not tokenize.COMMA:
                            break

        # Check for using reserved word as variable name (other cases)
        for t in tokens:
            if t.type is tokenize.NAME and keyword.iskeyword(t.string):
                newtestline = errorline[:t.start[1]] + 'x' + errorline[t.end[1]:]
                try:
                    ast.parse(prevcode + newtestline)
                    extramsg = ERR_RESERVED % (t.string, lineno)
                    break
                except SyntaxError as err:
                    newlineno = getattr(err, 'lineno', '') or 1
                    newoffset = getattr(err, 'offset', '') or 0
                    if newlineno > lineno or (newlineno is lineno and newoffset > offset):
                        extramsg = ERR_RESERVED % (t.string, lineno)
                        break

    except Exception as e:
        print('error', e)

    shell.write("\nSyntaxError: "+msg+"\n"+extramsg+"\n")
    # Logging code for testing
    #if not extramsg:
    #    extramsg = msg
    #with open("../error_results.txt", "a") as f:
    #    f.write(extramsg + "\n")
    shell.tkconsole.showprompt()
