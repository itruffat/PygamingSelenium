from setuptools import setup

setup(
    name='PygamingTheSeleniumSystem',
    version='0.0.0a1',
    author='itruffat',
    description='Keyboard support for Selenium',
    long_description='A library that uses Pygames to give keyboard support to Selenium.',
    long_description_content_type='text/markdown',
    url='https://github.com/itruffat/PygamingSelenium',
    package_dir={'': 'src'},
    packages=['PygamingTheSeleniumSystem'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    include_package_data=True,
)
