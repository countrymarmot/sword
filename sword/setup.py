'''
Created on Sep 17, 2013

@author: mzfa
'''
'''
Created on Jul 1, 2013

@author: mzfa
'''
from setuptools import setup
#from setuptools import find_packages

import sys

sys.path.append('src')

setup(
      name="sword",
      version="1.0",
      package_dir={'':'src'},
      packages=['sword',
                'sword/db'],
      package_data={'':['*.xml']},
      author="mzfa",
      description='put xml test log files into database "trackpad"',
      platforms="any"
      )
