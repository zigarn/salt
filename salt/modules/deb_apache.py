# -*- coding: utf-8 -*-
'''
Support for Apache

Please note: The functions in here are Debian-specific. Placing them in this
separate file will allow them to load only on Debian-based systems, while still
loading under the ``apache`` namespace.
'''
from __future__ import absolute_import

# Import python libs
import os
import logging

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)

__virtualname__ = 'apache'

SITE_AVAILABLE_DIR = '/etc/apache2/sites-available'
SITE_ENABLED_DIR = '/etc/apache2/sites-enabled'


def __virtual__():
    '''
    Only load the module if apache is installed
    '''
    cmd = _detect_os()
    if salt.utils.which(cmd) and __grains__['os_family'] == 'Debian':
        return __virtualname__
    return False


def _detect_os():
    '''
    Apache commands and paths differ depending on packaging
    '''
    # TODO: Add pillar support for the apachectl location
    if __grains__['os_family'] == 'RedHat':
        return 'apachectl'
    elif __grains__['os_family'] == 'Debian':
        return 'apache2ctl'
    else:
        return 'apachectl'


def check_site_enabled(site):
    '''
    Checks to see if the specific Site symlink is in /etc/apache2/sites-enabled.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.check_site_enabled example.com
    '''
    if os.path.islink('{0}/{1}'.format(SITE_ENABLED_DIR, site)):
        return True
    elif site == 'default' and os.path.islink('{0}/000-{1}'.format(SITE_ENABLED_DIR, site)):
        return True
    else:
        return False


def list_sites():
    '''
    List the sites in a dict::

        {'<site_name>': '<enabled_status>'}

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.list_sites
    '''
    site_list = os.listdir(SITE_AVAILABLE_DIR)
    ret = {}
    for site in site_list:
        ret[site] = check_site_enabled(site)
    return ret


def a2ensite(name=None,
             sites=None):
    '''
    Enable sites by running ``a2ensite``.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    name
        Name of the site to be enabled.

        CLI Example:

        .. code-block:: bash

            salt '*' apache.a2ensite example.com

    Multiple Sites Enabling Options:

    sites
        A list of sites to enable. Must be passed as a python list.

        CLI Example:

        .. code-block:: bash

            salt '*' apache.a2ensite sites='["example.com", "saltstack.com"]'
    '''
    command = ['a2ensite']
    if name:
        command.append(name)
    if sites:
        command.extend(sites)

    old = list_sites()
    res = __salt__['cmd.run_all'](command, python_shell=False)
    new = list_sites()
    ret = salt.utils.compare_dicts(old, new)

    if res['retcode'] != 0:
        ret['errors'] = res['stderr']

    return ret


def a2dissite(name=None,
              sites=None):
    '''
    Disable sites by running ``a2dissite``.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    name
        Name of the site to be disabled.

        CLI Example:

        .. code-block:: bash

            salt '*' apache.a2dissite example.com

    Multiple Sites Disabling Options:

    sites
        A list of sites to disable. Must be passed as a python list.

        CLI Example:

        .. code-block:: bash

            salt '*' apache.a2dissite sites='["example.com", "saltstack.com"]'
    '''
    command = ['a2dissite']
    if name:
        command.append(name)
    if sites:
        command.extend(sites)

    old = list_sites()
    res = __salt__['cmd.run_all'](command, python_shell=False)
    new = list_sites()
    ret = salt.utils.compare_dicts(old, new)

    if res['retcode'] != 0:
        ret['errors'] = res['stderr']

    return ret


def check_mod_enabled(mod):
    '''
    Checks to see if the specific mod symlink is in /etc/apache2/mods-enabled.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.check_mod_enabled status.conf
        salt '*' apache.check_mod_enabled status.load
    '''
    return os.path.islink('/etc/apache2/mods-enabled/{0}'.format(mod))


def a2enmod(mod):
    '''
    Runs a2enmod for the given mod.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.a2enmod vhost_alias
    '''
    ret = {}
    command = ['a2enmod', mod]

    try:
        status = __salt__['cmd.retcode'](command, python_shell=False)
    except Exception as e:
        return e

    ret['Name'] = 'Apache2 Enable Mod'
    ret['Mod'] = mod

    if status == 1:
        ret['Status'] = 'Mod {0} Not found'.format(mod)
    elif status == 0:
        ret['Status'] = 'Mod {0} enabled'.format(mod)
    else:
        ret['Status'] = status

    return ret


def a2dismod(mod):
    '''
    Runs a2dismod for the given mod.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.a2dismod vhost_alias
    '''
    ret = {}
    command = ['a2dismod', mod]

    try:
        status = __salt__['cmd.retcode'](command, python_shell=False)
    except Exception as e:
        return e

    ret['Name'] = 'Apache2 Disable Mod'
    ret['Mod'] = mod

    if status == 256:
        ret['Status'] = 'Mod {0} Not found'.format(mod)
    elif status == 0:
        ret['Status'] = 'Mod {0} disabled'.format(mod)
    else:
        ret['Status'] = status

    return ret


def check_conf_enabled(conf):
    '''
    .. versionadded:: Boron

    Checks to see if the specific conf symlink is in /etc/apache2/conf-enabled.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.check_conf_enabled security.conf
        salt '*' apache.check_conf_enabled status.load
    '''
    return os.path.islink('/etc/apache2/conf-enabled/{0}'.format(conf))


@salt.utils.decorators.which('a2enconf')
def a2enconf(conf):
    '''
    .. versionadded:: Boron

    Runs a2enconf for the given conf.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.a2enconf security
    '''
    ret = {}
    command = ['a2enconf', conf]

    try:
        status = __salt__['cmd.retcode'](command, python_shell=False)
    except Exception as e:
        return e

    ret['Name'] = 'Apache2 Enable Conf'
    ret['Conf'] = conf

    if status == 1:
        ret['Status'] = 'Conf {0} Not found'.format(conf)
    elif status == 0:
        ret['Status'] = 'Conf {0} enabled'.format(conf)
    else:
        ret['Status'] = status

    return ret


@salt.utils.decorators.which('a2disconf')
def a2disconf(conf):
    '''
    .. versionadded:: Boron

    Runs a2disconf for the given conf.

    This will only be functional on Debian-based operating systems (Ubuntu,
    Mint, etc).

    CLI Examples:

    .. code-block:: bash

        salt '*' apache.a2disconf security
    '''
    ret = {}
    command = ['a2disconf', conf]

    try:
        status = __salt__['cmd.retcode'](command, python_shell=False)
    except Exception as e:
        return e

    ret['Name'] = 'Apache2 Disable Conf'
    ret['Conf'] = conf

    if status == 256:
        ret['Status'] = 'Conf {0} Not found'.format(conf)
    elif status == 0:
        ret['Status'] = 'Conf {0} disabled'.format(conf)
    else:
        ret['Status'] = status

    return ret
