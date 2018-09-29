import pytest
import sys
[sys.path.append(i) for i in ['.', '..']]
from lloyd import Field
import numpy as np

@pytest.fixture()
def arr():
  np.random.seed(141)
  return np.random.rand(100,2)

@pytest.fixture()
def field(arr):
  field = Field(arr)
  field.relax()
  return field

def test_result_points_same_shape(arr, field):
  '''
  Ensure the points returned from the transformation
  have the same shape as the input points
  '''
  assert field.get_points().shape == arr.shape

def test_points_in_bb(field):
  '''
  Ensure all input points are in the bounding box
  '''
  for x, y in field.get_points():
    assert x >= field.bb[0]
    assert x <= field.bb[1]
    assert y >= field.bb[2]
    assert y <= field.bb[3]

def test_no_empty_regions(field):
  '''
  Ensure there are no empty regions in voronoi.regions.
  '''
  for i in field.voronoi.regions:
    assert len(i) > 0