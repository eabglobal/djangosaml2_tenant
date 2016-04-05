# Copyright (C) 2010-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.core.files.storage import default_storage

from saml2.config import SPConfig

import djangosaml2
from djangosaml2.utils import get_custom_setting, get_endpoints

from .exceptions import MissingSAMLMetadataException


BASE_PATH = getattr(settings, 'SAML2_IDP_BASE_DIR', os.path.dirname(djangosaml2.__file__))

_sp_config_map = {}


def get_config_loader(path, request=None):
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing SAML config loader %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured(
            'Error importing SAML config loader. Is SAML_CONFIG_LOADER '
            'a correctly string with a callable path?'
        )
    try:
        config_loader = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a "%s" config loader' %
            (module, attr)
        )

    if not hasattr(config_loader, '__call__'):
        raise ImproperlyConfigured(
            "SAML config loader must be a callable object.")

    return config_loader


def config_settings_loader(request):
    """Utility function to load the pysaml2 configuration for a single tenant/member/schema.

    This is also the default config loader.
    This sets the metadata to depend on the tenant
    """
    conf = SPConfig()
    tenant_config = copy.deepcopy(settings.SAML_CONFIG)

    if "local" in settings.SAML_CONFIG["metadata"]:
        default_storage_objects = settings.SAML_CONFIG["metadata"]["local"][request.tenant.schema_name]
        # Local files might be s3 objects
        # If yes they should be copied locally as saml2 only works with local files
        directory = os.path.join(BASE_PATH, request.tenant.schema_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        local_files = []
        for object_name in default_storage_objects:
            path = os.path.join(directory, object_name)
            if not os.path.exists(path):
                # We need this here in spite of makedirs above as s3 object names can have /
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                file_content = default_storage.open(object_name).read()
                with open(path, "w") as open_file:
                    open_file.write(file_content)
            local_files.append(path)
        tenant_config["metadata"]["local"] = local_files

    if "remote" in settings.SAML_CONFIG["metadata"]:
        tenant_config["metadata"]["remote"] = settings.SAML_CONFIG["metadata"]["remote"][request.tenant.schema_name]

    # If SAML metadata can specified inline, SAML_CONFIG['metadata']['inline'] is supposed to contain valid XML metadata
    # But if we simply put the 'DB' placeholder value there instead of valid XML, ask tenant.Member to get the XML
    # metadata from the DB for the requesting tenant/member/schema.
    if settings.SAML_CONFIG['metadata'].get('inline') == 'DB':
        metadata = request.tenant.get_saml_metadata()
        if metadata:
            tenant_config['metadata']['inline'] = [metadata, ]
        else:
            raise MissingSAMLMetadataException("SAML metadata is not specified")

    tenant_config["service"]["sp"]["endpoints"] = get_endpoints(request)
    conf.load(tenant_config)

    return conf


def get_config(config_loader_path=None, request=None):
    sp_config = _sp_config_map.get(request.tenant.schema_name, None)
    if not sp_config:
        config_loader_path = config_loader_path or get_custom_setting(
            'SAML_CONFIG_LOADER', 'djangosaml2.conf.config_settings_loader')

        config_loader = get_config_loader(config_loader_path)
        sp_config = config_loader(request)
        _sp_config_map[request.tenant.schema_name] = sp_config
    return sp_config
