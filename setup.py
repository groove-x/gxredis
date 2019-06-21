from setuptools import setup, find_packages

version = '0.3.0'

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

setup(
    name="gxredis",
    version=version,
    description="Simple redis-py wrapper library",
    long_description=readme,
    url="https://github.com/groove-x/gxredis",
    author="Junya Hayashi",
    author_email="junya.hayashi@groove-x.com",
    maintainer="Junya Hayashi",
    maintainer_email="junya-hayashi@groove-x.com",
    keywords=['Redis', 'key-value store'],
    packages=find_packages(exclude=["test"]),
    install_requires=["redis"],
    tests_require=["pytest"],
    license="MIT",
    test_suite="test",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
    ]
)
