"""Project setup."""

from setuptools import find_packages, setup

setup(
    name='civsim',
    description='A basic civilisation simulation and modelling system',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',

    author='UtilityHotbar',
    url='https://github.com/UtilityHotbar/civsim/',

    install_requires=[open('requirements.txt', 'r').read()],

    packages=find_packages(include=['civsim', 'civsim.*']),

    setup_requires=['setuptools_scm'],
    use_scm_version={
        'write_to': 'civsim/scmversion.py',
        'write_to_template': "__version__ = '{version}'\n",
    },

    include_package_data=True,

    entry_points={
        'console_scripts': [
            'civsim-version=civsim.scripts.version:main',
            'civsim-run=civsim.scripts.run:main',
        ],
    },

    classifiers=[
        'Development Status :: 3 - Beta',
        'Environment :: Console',

        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',

        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',

        'Programming Language :: Python',
    ],
)
