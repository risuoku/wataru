from .base import RuleBase

from jupyter_client.kernelspec import KernelSpecManager
import IPython

from wataru.logging import getLogger
import wataru.exceptions as wtex
import wataru.utils as utils
import wataru.rules.templates as modtpl

import os
import shutil
import re

__all__ = [
    'SetupJupyter',
]

logger = getLogger(__name__)

KERNEL_CONFIG_NAME = 'kernel.json'


class SetupJupyter(RuleBase):
    kerneldir_default = 'wataru_default'
    ipythonprofile_default = 'wataru_default'

    def __init__(self, md, kerneldir = None, ipythonprofile = None):
        self._md_path = md.path
        self._md_file = md.metadata
        self._kerneldir = kerneldir or self.__class__.kerneldir_default
        self._ipythonprofile = ipythonprofile or self.__class__.ipythonprofile_default

    def converge(self):
        # for jupyter
        ksm = KernelSpecManager()
        kernel_done = False
        abskd = None
        for kd in ksm.kernel_dirs:
            abskd = os.path.join(kd, self._kerneldir)
            if os.path.isdir(abskd): # 存在していたらbreak
                logger.debug('already exist')
                kernel_done = True
                break
            else:
                try:
                    os.makedirs(abskd)
                    logger.debug('created => {}'.format(abskd))
                    kernel_done = True
                    break
                except PermissionError:
                    # ignore exception
                    pass

        if not kernel_done:
            raise wtex.ConvergeFailed()

        # for IPython
        ipythonprofile_done = False
        try:
            IPython.paths.locate_profile(self._ipythonprofile)
            ipythonprofile_done = True
        except Exception as e:
            logger.debug('ipythondir may be not found .. {}'.format(e))
            try:
                utils.do_console_command('ipython profile create {}'.format(self._ipythonprofile))
                logger.debug('created => {}'.format(self._ipythonprofile))
                ipythonprofile_done = True
            except:
                pass

        if not ipythonprofile_done:
            raise wtex.ConvergeFailed()

        # install KERNEL_CONFIG
        utils.save_file(
            os.path.join(abskd, KERNEL_CONFIG_NAME),
            modtpl.get(os.path.join(self._md_path, KERNEL_CONFIG_NAME + '.tpl'))
                .render({
                    'kernel_display_name': 'wataru Python3',
                    'kernel_argv_profile': self._ipythonprofile
                })
        )

        # install ipython configs
        my_ipy_profile_dir = os.path.join(self._md_path, 'ipython_profile_dir')
        my_ipy_profile_dir_abs = os.path.join(modtpl.get_template_abspath(), my_ipy_profile_dir)
        if os.path.isdir(my_ipy_profile_dir_abs):
            logger.debug('ipython_profile_dir found.')
            ipy_profile_dir = IPython.paths.locate_profile(self._ipythonprofile)
            my_ipy_pdir_list = os.listdir(my_ipy_profile_dir_abs)
            for my_ipydir in my_ipy_pdir_list:
                target_ipydir = os.path.join(ipy_profile_dir, my_ipydir)
                if os.path.isdir(target_ipydir):
                    shutil.rmtree(target_ipydir)
                os.makedirs(target_ipydir)
                for ipy_file_tpl in os.listdir(os.path.join(my_ipy_profile_dir_abs, my_ipydir)):
                    ipy_file = re.sub('\.tpl', '', ipy_file_tpl)
                    utils.save_file (
                        os.path.join(target_ipydir, ipy_file),
                        modtpl.get(os.path.join(my_ipy_profile_dir, my_ipydir, ipy_file_tpl)).render()
                    )
        else:
            logger.debug('ipython_profile_dir not found.')
        
        # update metadata file
        utils.save_file(
            self._md_file.abspath,
            modtpl.get(self._md_file.path + '.tpl')
                .render({
                    'kernel_dir': abskd,
                    'ipython_profile_dir': IPython.paths.locate_profile(self._ipythonprofile)
                })
        )
        logger.debug('metadata file updated.')
