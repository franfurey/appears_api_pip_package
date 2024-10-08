# setup.py
from setuptools import setup, find_packages

setup(
    name='appeears-api-client',
    version='0.1.2',
    packages=find_packages(),
    license='MIT',
    description='Python client for interacting with NASA Earthdata\'s AppEEARS API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Francisco Furey',
    author_email='franciscofurey@gmail.com',
    url='https://github.com/franfurey/appeears_api_pip_package',
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
