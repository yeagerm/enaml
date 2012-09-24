#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Command-line tool to run .enaml files.

"""
import optparse
import os
import sys
import types

from enaml import imports
from enaml.stdlib.sessions import show_simple_view
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler


def main():
    usage = 'usage: %prog [options] enaml_file [script arguments]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.allow_interspersed_args = False
    parser.add_option('-c', '--component', default='Main',
                      help='The component to view')
    parser.add_option('-t', '--toolkit', default='qt',
                      help='The GUI toolikit to use')

    options, args = parser.parse_args()

    if len(args) == 0:
        print 'No .enaml file specified'
        sys.exit()
    else:
        enaml_file = args[0]
        script_argv = args[1:]

    with open(enaml_file) as f:
        enaml_code = f.read()

    # Parse and compile the Enaml source into a code object
    ast = parse(enaml_code, filename=enaml_file)
    code = EnamlCompiler.compile(ast, enaml_file)

    # Create a proper module in which to execute the compiled code so
    # that exceptions get reported with better meaning
    module = types.ModuleType('__main__')
    module.__file__ = enaml_file
    ns = module.__dict__

    # Put the directory of the Enaml file first in the path so relative imports
    # can work.
    sys.path.insert(0, os.path.abspath(os.path.dirname(enaml_file)))
    # Bung in the command line arguments.
    sys.argv = [enaml_file] + script_argv
    with imports():
        exec code in ns

    requested = options.component
    if requested in ns:
        component = ns[requested]
        descr = 'Enaml-run "%s" view' % requested
        show_simple_view(component(), options.toolkit, descr)
    elif 'main' in ns:
        ns['main']()
    else:
        msg = "Could not find component '%s'" % options.component
        print msg


if __name__ == '__main__':
    main()
