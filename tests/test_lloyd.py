import pytest
import sys
[sys.path.append(i) for i in ['.', '..']]
from lloyd import Field
import numpy as np

@pytest.fixture()
def arr():
  np.random.seed(141)
  arr = np.random.rand(100,2)
  # create duplicate inputs
  arr[1][0] = arr[0][0]
  arr[1][1] = arr[0][1]
  return arr

@pytest.fixture()
def constrained(arr):
  field = Field(arr)
  field.relax()
  return field

@pytest.fixture()
def unconstrained(arr):
  field = Field(arr, constrain=False)
  field.relax()
  return field

def test_result_points_same_shape(arr, constrained, unconstrained):
  '''
  Ensure the points returned from the transformation
  have the same shape as the input points
  '''
  for field in [constrained, unconstrained]:
    assert field.get_points().shape == arr.shape


def test_points_in_bb(arr, constrained):
  '''
  Ensure all input points are in the bounding box
  '''
  domains = constrained.get_domains(arr)
  for x, y in constrained.get_points():
    assert x >= domains['x']['min']
    assert x <= domains['x']['max']
    assert y >= domains['y']['min']
    assert y <= domains['y']['max']

def test_no_empty_regions(constrained, unconstrained):
  '''
  Ensure there are no empty regions in voronoi.regions.
  '''
  for field in [constrained, unconstrained]:
    for i in field.voronoi.regions:
      assert len(i) > 0