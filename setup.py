from setuptools import setup

setup (
  name='lloyd',
  version='0.0.10',
  packages=['lloyd'],
  keywords = ['data-visualization', 'geometry', 'voronoi', 'lloyd-iteration'],
  description='Lloyd iteration for distributing points in two-dimensional space.',
  url='https://github.com/duhaime/lloyd',
  author='Douglas Duhaime',
  author_email='douglas.duhaime@gmail.com',
  license='MIT',
  install_requires=[
    'matplotlib>=2.0.0',
    'numpy>=1.15.2',
    'scikit-learn>=0.18.1',
    'scipy>=1.1.0',
    'umap-learn>=0.2.3',
  ],
)