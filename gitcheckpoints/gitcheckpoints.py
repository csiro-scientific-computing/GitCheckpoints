"""
Git-based Checkpoints implementations.
"""
import os
import shutil

from notebook.services.contents.checkpoints import Checkpoints
from notebook.services.contents.fileio import FileManagerMixin

from IPython.utils import tz
from IPython.utils.path import ensure_dir_exists
from IPython.utils.py3compat import getcwd
from traitlets import Unicode
from IPython.utils.encoding import DEFAULT_ENCODING
import subprocess


class GitCheckpoints(FileManagerMixin, Checkpoints):
    """
    A Checkpoints subclass that commits the file every checkpoint
    """

    root_dir = Unicode(config=True)
    
    def __init__(self, *args, **kwargs):
        super(GitCheckpoints, self).__init__(*args, **kwargs)
        self.git_dir = self._git_dir_default()
        self.log.info('Versioning notebooks with GitCheckpoints from local directory: ' + self.git_dir)
        try:
            subprocess.check_output(['git', 'init'], stderr=subprocess.STDOUT, cwd=self.git_dir)
        except subprocess.CalledProcessError as e:
            err = e.output.decode(DEFAULT_ENCODING, 'replace')
            self.log.exception(err)

    def _git_dir_default(self):
        try:
            return self.parent.parent.notebook_dir
        except AttributeError:
            try:
                return self.parent.root_dir
            except AttributeError:
                return getcwd()

    def _root_dir_default(self):
        try:
            return self.parent.root_dir
        except AttributeError:
            return getcwd()

    # ContentsManager-dependent checkpoint API
    def create_checkpoint(self, contents_mgr, path):
        """Create a checkpoint."""
        src_path = contents_mgr._get_os_path(path)
        try:
            subprocess.check_output(['git', 'add', src_path], stderr=subprocess.STDOUT, cwd=self.git_dir)
            subprocess.check_output(['git', 'commit', '-m', "Checkpoint for '%s'" % src_path], stderr=subprocess.STDOUT, cwd=self.git_dir)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                # no changes
                pass
            else:
                err = e.output.decode(DEFAULT_ENCODING, 'replace')
                self.log.exception(err)
                return None
        try:
            output = subprocess.check_output(['git', 'log', '--pretty=format:"%h - %cd"', src_path], stderr=subprocess.STDOUT, cwd=self.git_dir)
            output = output.decode(DEFAULT_ENCODING, 'replace')
            checkpoint = self.checkpoint_model(output.splitlines()[0])
            return checkpoint
        except subprocess.CalledProcessError as e:
            err = e.output.decode(DEFAULT_ENCODING, 'replace')
            self.log.exception(err)
            return None

    def restore_checkpoint(self, contents_mgr, checkpoint_id, path):
        """Restore a checkpoint."""
        path = path.strip('/')
        try:
            subprocess.check_output(['git', 'checkout', checkpoint_id, path], stderr=subprocess.STDOUT, cwd=self.git_dir)
        except subprocess.CalledProcessError as e:
            err = e.output.decode(DEFAULT_ENCODING, 'replace')
            self.log.exception(err)

    def rename_all_checkpoints(self, old_path, new_path):
        """Rename all checkpoints for old_path to new_path."""
        old_path = old_path.strip('/')
        new_path = new_path.strip('/')
        try:
            subprocess.check_output(['git', 'rm', old_path], stderr=subprocess.STDOUT, cwd=self.git_dir)
            subprocess.check_output(['git', 'add', new_path], stderr=subprocess.STDOUT, cwd=self.git_dir)
            subprocess.check_output(['git', 'commit', '-m', "Renamed '%s' to '%s'" % (old_path, new_path)], stderr=subprocess.STDOUT, cwd=self.git_dir)
        except subprocess.CalledProcessError as e:
            if e.returncode == 128:
                #file not committed
                pass
            else:
                err = e.output.decode(DEFAULT_ENCODING, 'replace')
                self.log.exception(err)
            
    # ContentsManager-independent checkpoint API
    def rename_checkpoint(self, checkpoint_id, old_path, new_path):
        """Rename a checkpoint from old_path to new_path."""
        pass

    def delete_all_checkpoints(self, path):
        """Delete all checkpoints for the given path."""
        path = path.strip('/')
        try:
            subprocess.check_output(['git', 'rm', path], stderr=subprocess.STDOUT, cwd=self.git_dir)
            subprocess.check_output(['git', 'commit', '-m', "Deleted '%s'" % path], stderr=subprocess.STDOUT, cwd=self.git_dir)
        except subprocess.CalledProcessError as e:
            if e.returncode == 128 or e.returncode == 1:
                #file not committed
                pass
            else:
                err = e.output.decode(DEFAULT_ENCODING, 'replace')
                self.log.exception(err)
            
    def delete_checkpoint(self, checkpoint_id, path):
        """delete a file's checkpoint"""
        pass

    def list_checkpoints(self, path):
        """list the checkpoints for a given file"""
        path = os.path.join(self.git_dir, path.lstrip('/').lstrip('\\'))
        checkpoints = []
        if os.path.isfile(path):
            try:
                output = subprocess.check_output(['git', 'log', '--pretty=format:"%h - %cd"', path], stderr=subprocess.STDOUT, cwd=self.git_dir)
                output = output.decode(DEFAULT_ENCODING, 'replace')
                for commit in output.splitlines():
                    cp = self.checkpoint_model(commit)
                    if cp:
                        checkpoints.append(cp)
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    #file not committed
                    pass
                else:
                    err = e.output.decode(DEFAULT_ENCODING, 'replace')
                    self.log.exception(err)
        return checkpoints

    def checkpoint_model(self, log):
        """construct the info dict for a given checkpoint"""
        commitinfo = log.strip('"').split('-', 1)
        if len(commitinfo) == 2:
            return dict(
                id = commitinfo[0].strip(),
                last_modified = commitinfo[1].strip()
            )
    
