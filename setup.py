# -*- coding: utf8 -*-
from setuptools import setup

# name can be any name.  This name will be used to create .egg file.
# name that is used in packages is the one that is used in the trac.ini file.
# use package name as entry_points
setup(
    name='TracSymfonyErrors',
    version='0.1',
    author='Michal Wujas',
    license = '''GPL''',
    author_email = 'michal@michalwujas.pl',
    description = 'Integrates Symfony Error Logger with Trac',
    packages=['symfonyerrors'],
    package_data={'symfonyerrors': ['templates/*.html']},
    entry_points = """
        [trac.plugins]
        tracsymfonyerrors.core = symfonyerrors.core
	tracsymfonyerrors.macros = symfonyerrors.macros
	tracsymfonyerrors.api = symfonyerrors.api
    """,
)

