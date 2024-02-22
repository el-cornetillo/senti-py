from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='senti-py',
    version='1.0.1',
    description='A sentiment analysis classifier in spanish.',
    long_description=long_description,
    url='https://github.com/aylliote/senti-py',
    download_url='https://github.com/aylliote/senti-py/archive/master.zip',
    author='Elliot',
    license='Sondeos',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Sondeos developpers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Sondeos License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='natural language processing sentiment analysis',
    #   packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages = ['classifier', 'crawlers'],
    install_requires=['pandas', 'numpy', 'tqdm','nltk', 'sklearn', 'marisa-trie','spacy','es_core_web_md'],
    extras_require={
        'crawl': ['bs4', 'urllib']
            },
    data_files=[('data', ['classifier/data/sensaCineSerie.txt', 'classifier/data/sensaCineMovie.txt',
                            'classifier/data/pedidosYa.txt', 'classifier/data/tripAdvisorHotel.txt',
                            'classifier/data/tripAdvisorRestaurant.txt', 'classifier/data/tripAdvisorAttraction.rar',
                            'classifier/data/openCine.txt', 'classifier/data/quejas.txt', 
                            'classifier/data/apestan.rar', 'classifier/data/badTweets.txt',
                        'classifier/data/goodTweets.txt', 'classifier/data/tassTweets.txt',
                        'classifier/data/MercadoPos.rar', 'classifier/data/MercadoNeg.txt' ])]
)
