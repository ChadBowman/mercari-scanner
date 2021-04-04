from setuptools import find_packages
from setuptools import setup

setup(
    name='mercari-scanner',
    version='0.1.0',
    author='Chad Bowman',
    author_email='chad.bowman0+github@gmail.com',
    description='Scan and recieve alerts for newly listed items on Mercari',
    packages=find_packages(),
    install_requires=[
        'requests >=2.25.1',
        'scrapy >=2.4.1'
    ]
)
