__author__ = 'jdroot'

from paste.script.serve import ServeCommand
ServeCommand("serve").run(["--reload", "development.ini"])