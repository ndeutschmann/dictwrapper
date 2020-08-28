from setuptools import find_packages, setup

setup(
    name='dictwrapper',
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.3",
        "pandas>=1.1"
    ],
    version='1.0',
    description='Basic Dictionary Wrapper',
    long_description=open("README.md").read(),
    author='Nicolas Deutschmann',
    author_email="nicolas.deutschmann@gmail.com",
    license='MIT',
)
