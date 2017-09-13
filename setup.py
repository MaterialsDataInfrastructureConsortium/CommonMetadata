from setuptools import setup, find_packages

setup(
    name='pubmeta',
    version='0.0.0',
    url='https://github.com/jasonthiese/CommonMetadata',
    description='Common support for meta-data',
    author='Jason Thiese',
    packages=find_packages(),
    install_requires=[
        'pypif'
    ]
)
