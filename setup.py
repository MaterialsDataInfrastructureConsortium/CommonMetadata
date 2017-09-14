from setuptools import setup, find_packages

setup(
    name='matmeta',
    version='0.1.0',
    url='https://github.com/jasonthiese/CommonMetadata',
    description='Common support for meta-data',
    author='Jason Thiese',
    author_email="jasonthiese@gmail.com",
    license="Apache v2",
    packages=find_packages(),
    install_requires=[
        'pypif'
    ]
)
