# Copyright (C) 2015 Education Advisory Board
# Copyright (C) 2011-2012 Yaco Sistemas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='djangosaml2_tenant',
    version='0.20.1',
    description='pysaml2 integration for multi-tenant in Django',
    long_description='\n\n'.join([read('README'), read('CHANGES')]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
    keywords="django,pysaml2,saml2,federated authentication,multi-tenant",
    author="Education Advisory Board",
    author_email="msensenbrenn@eab.com",
    url="https://github.com/advisory/djangosaml2_tenant",
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pysaml2==2.2.0',
        'python-memcached==1.48',
        ],
    )
