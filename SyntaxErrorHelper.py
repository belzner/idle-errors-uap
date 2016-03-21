from tkinter import END

def writeSyntaxError(shell, value, text):
    # I don't know what to do with text yet, but it'll probably
    # be useful for processing
    msg = getattr(value, 'msg', '') or value or "<no detail available>"
    lineno = getattr(value, 'lineno', '') or 1
    linepos = "startpos + %d lines" % (lineno-1)
    shell.write("\nYou dun goofed\nSyntaxError: "+msg+"\n")
    errorline = text.get(linepos, linepos+" lineend")
    print(errorline)
    shell.tkconsole.showprompt()
