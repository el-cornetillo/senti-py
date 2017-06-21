from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Sentiment Analysis Classifier',
    version='1.0.0'
    description='A sentiment analysis classifier in spanish.',
    long_description=long_description,
    url='https://github.com/pypa/sampleproject',
    author='Elliot Hofman',
    author_email='elliot.hofman@gmail.com',
    license='Sondeos',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Sondeos developpers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Sondeos License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='natural language processing sentiment analysis',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pandas', 'numpy', 'tqdm', 're', 'json', 'time',
                      'nltk' , 'sklearn', 'marisa-trie','spacy','es_core_web_md']

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'crawl': ['bs4', 'urllib']
            },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('data', ['classifier/data/sensaCineSerie.txt', 'classifier/data/sensaCineMovie.txt',
                            'classifier/data/pedidosYa.txt', 'classifier/data/tripAdvisorHotel.txt',
                            'classifier/data/tripAdvisorRestaurant.txt', 'classifier/data/tripAdvisorAttraction.txt',
                            'classifier/data/openCine.txt', 'classifier/data/quejas.txt', 
                            'classifier/data/apestan.txt', 'classifier/data/badTweets.txt',
                        'classifier/data/goodTweets.txt', 'classifier/data/tassTweets.txt',
                        'classifier/data/MercadoPos.txt', 'classifier/data/MercadoNeg.txt' ])]
)