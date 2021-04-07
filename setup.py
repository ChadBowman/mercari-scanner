import pathlib
from setuptools import find_packages
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(
    name='mercari-scanner',
    version='0.1.1',
    author='Chad Bowman',
    author_email='chad.bowman0+github@gmail.com',
    description='Scan and receive alerts for newly listed items on Mercari',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/ChadBowman/mercari-scanner',
    licence='MIT',
    packages=find_packages(),
    install_requires=[
        'requests >=2.25.1',
        'scrapy >=2.4.1'
    ],
    entry_points={
        'console_scripts': [
            'mercari-scanner=mercari_scanner.__main__:main'
        ]
    }
)
