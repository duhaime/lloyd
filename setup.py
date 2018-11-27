from setuptools import setup

setup (
  name='lloyd',
  version='0.0.2',
  packages=['lloyd'],
  keywords = ['data-visualization', 'geometry', 'voronoi', 'lloyd-iteration'],
  description='Lloyd iteration for distributing points in two-dimensional space.',
  url='https://github.com/duhaime/lloyd',
  author='Douglas Duhaime',
  author_email='douglas.duhaime@gmail.com',
  license='MIT',
  install_requires=open('requirements.txt').read().split('\n'),
)