from setuptools import setup


setup(name = 'scluster',
    version = '1.0.0',
    description = 'Simple ssdeep clustering',
    author = '0xab00d',
    author_email = '0xab00d@protonmail.com',
    url = 'https://github.com/0xab00d/scluster',
    py_modules = ['scluster'],
    install_requires=[
          'ssdeep',
    ],
)
