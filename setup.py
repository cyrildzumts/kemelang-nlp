import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
    
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='kemelang-nlp',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='The work on this project in focused on bringing NLP support to the kemelang project',
    long_description=README,
    url='https://github.com/cyrildzumts/kemelang-nlp',
    author='Cyrille Ngassam Nkwenga',
    author_email='cyrildz@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)