def writeSyntaxError(shell, msg, text):
    # I don't know what to do with text yet, but it'll probably
    # be useful for processing
    shell.write("\nYou dun goofed\nSyntaxError: "+msg+"\n")
    shell.tkconsole.showprompt()
