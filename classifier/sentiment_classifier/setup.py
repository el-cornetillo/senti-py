from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sondeos-classifier',
    version='1.0.0',
    description='A sentiment analysis classifier in spanish.',
    long_description=long_description,
    #url='https:\\github.com\aylliote\sentiment-spanish',
    #download_url='https:\\github.com\aylliote\senti-py\archive\master.zip',
    author='Elliot Hofman',
    author_email='elliot.hofman@gmail.com',
    license='MIT',

    # See https:\\pypi.python.org\pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='natural language processing sentiment analysis',
    #   packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages = ['classifier'],
    package_dir = {'classifier': 'classifier'},

    package_data = {'classifier': ['data/dictConjug.json', 'data/Countries.txt', 'data/Cities.txt', 'data/expressions.txt', 'img/bad_baby.jpg', 'img/good_baby.jpg',
    									'model/sentiment_pipeline.pkl']},


    install_requires=['numpy','nltk', 'sklearn','marisa-trie','scipy']
)