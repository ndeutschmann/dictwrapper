from setuptools import find_packages, setup

setup(
    name='dictwrapper',
    package_dir={'':'src'},
    packages=['dictwrapper'],
    install_requires=[
        "ruamel.yaml <= 0.16.12",
        "pandas>=1.1"
    ],
    version='1.3',
    description='Basic Dictionary Wrapper',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Nicolas Deutschmann',
    author_email="nicolas.deutschmann@gmail.com",
    license='MIT',
)
