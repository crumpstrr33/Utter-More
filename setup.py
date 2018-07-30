from setuptools import setup, find_packages
import re

with open('README.md', 'r') as f:
    long_description = f.read()

with open('utter_more/__init__.py', 'r') as f:
    setup_file = f.read()
version = re.findall(r'__version__ = \'(.*)\'', setup_file)[0]
name = re.findall(r'__name__ = \'(.*)\'', setup_file)[0]

setup(
    name=name,
    version=version,
    author='Jacob Scott',
    author_email='jscott12009@gmail.com',
    description='Creates utterances for Amazon\'s Alexa.',
    license='MIT',
    url='https://github.com/crumpstrr33/Utter-More',
    packages=find_packages(exclude=['test*']),
    python_requires='>=3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
