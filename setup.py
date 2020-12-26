from setuptools import find_packages, setup

setup(
    name='dictwrapper',
    packages=find_packages(),
    install_requires=[
        "ruamel.yaml<=0.15",
        "pandas>=1.1"
    ],
    version='1.1',
    description='Basic Dictionary Wrapper',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Nicolas Deutschmann',
    author_email="nicolas.deutschmann@gmail.com",
    license='MIT',
)
