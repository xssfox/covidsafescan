import setuptools

setuptools.setup(name='covidsafescan',
      version='1.6',
      description='Covid Safe Scanner',
      author='xssfox',
      author_email='pypi@sprocketfox.io',
      url='https://github.com/xssfox/covidsafescan',
      packages=['covidsafescan'],
      entry_points = {
          'console_scripts': ['covidsafescan=covidsafescan:__main__']
      },
      install_requires=['bleak', 'twisted']
     )