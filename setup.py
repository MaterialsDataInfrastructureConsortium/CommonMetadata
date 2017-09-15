from setuptools import setup, find_packages

setup(
    name='matmeta',
    version='0.1.1',
    url='https://github.com/MaterialsDataInfrastructureConsortium/CommonMetadata',
    description='Common support for materials metadata',
    author='Jason Thiese',
    author_email="jasonthiese@gmail.com",
    license="Apache v2",
    packages=find_packages(),
    install_requires=[
        'pypif'
    ]
)
