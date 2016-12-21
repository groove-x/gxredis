from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name="gxredis",
    version=version,
    author="Junya Hayashi",
    author_email="junya-hayashi@groove-x.com",
    packages=find_packages(exclude=["test"]),
    test_suite="test",
)
