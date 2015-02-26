from __future__ import print_function
from setuptools import setup
import sys

def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)
    
def main():
    try:
        import IPython
        if IPython.version_info[0] < 3:
            fail("GitCheckpoints requires IPython 3.0 or greater.")
    except ImportError:
        fail("GitCheckpoints requires IPython.")
    
    setup(name='gitcheckpoints',
        version='0.1',
        description='Git based checkpoints for IPython',
        url='https://github.com/csiro-scientific-computing/gitcheckpoints',
        author='Alex Kruger',
        author_email='Alex.Kruger@csiro.au',
        license='CSIRO BSD MIT',
        packages=['gitcheckpoints'],
        classifiers=['Development Status :: 4 - Beta'],
        zip_safe=False)

if __name__ == '__main__':
    main()