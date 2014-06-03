
def main(args=None):
    if args is None:
        import sys
        args = sys.argv[1:]
    #Load the default config
    config = '/var/pycloud/default.ini'
    if len(args) > 0:
        config = args[0]

    from paste.script.serve import ServeCommand
    ServeCommand("serve").run([config])