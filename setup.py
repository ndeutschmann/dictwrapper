from setuptools import find_packages, setup

setup(
    name='dictwrapper',
    package_dir={'': 'src'},
    packages=['dictwrapper'],
    install_requires=[
        "pyyaml>=6.0",
        "pandas>=1.1"
    ],
    version='1.6',
    description='Basic Dictionary Wrapper',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Nicolas Deutschmann',
    author_email="nicolas.deutschmann@gmail.com",
    license='MIT',
)
