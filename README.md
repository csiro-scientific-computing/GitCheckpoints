GitCheckpoints
=======

Requirements:
-------------
    IPython 3 or greater
    Git

Installation (from repository):
------------------------------
    git clone https://github.com/csiro-scientific-computing/GitCheckpoints.git gitcheckpoints
    cd gitcheckpoints
    python setup.py install
    add this line to IPython config:
        c.FileContentsManager.checkpoints_class = 'gitcheckpoints.GitCheckpoints'
