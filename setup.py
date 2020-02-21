from setuptools import setup

setup(
   name='teammood',
   version='1.0',
   description="Teammood (https://app.teammood.com) is a online app that polls teams daily to see how they are doing and to catch problems before they become big. Geared towards agile dev teams it's a easy way to see how everyone is operating.",
   author='shaungehring',
   author_email='shaungehring@me.com',
   packages=['teammood'],  #same as name
   install_requires=['requests'], #external packages as dependencies
)
