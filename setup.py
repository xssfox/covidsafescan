import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='covidsafescan',
      version='1.14',
      description='Covid Safe Scanner',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='xssfox',
      author_email='pypi@sprocketfox.io',
      url='https://github.com/xssfox/covidsafescan',
      packages=['covidsafescan'],
      entry_points = {
          'console_scripts': ['covidsafescan=covidsafescan:__main__.main']
      },
      install_requires=['bleak'],
)
