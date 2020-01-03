from scipy.spatial import Voronoi
import numpy as np

class Field():
  '''
  Create a Voronoi map that can be used to run Lloyd
  relaxation on an array of 2D points. For background,
  see: https://en.wikipedia.org/wiki/Lloyd%27s_algorithm
  '''

  def __init__(self, *args, **kwargs):
    '''
    Store the points and bounding box of the points to which
    Lloyd relaxation will be applied.
    @param np.array `arr`: a numpy array with shape n, 2, where n
      is the number of 2D points to be moved
    @param float `epsilon`: the delta between the input point
      domain and the pseudo-points used to constrain the points
    '''
    arr = args[0]
    if not isinstance(arr, np.ndarray) or arr.shape[1] != 2:
      raise Exception('Please provide a numpy array with shape n,2')
    self.points = arr
    # find the bounding box of the input data
    self.domains = self.get_domains(arr)
    # ensure no two points have the exact same coords
    self.jitter_points()
    self.bb_points = self.get_bb_points(arr)
    self.constrain = kwargs.get('constrain', True)
    self.build_voronoi()


  def jitter_points(self, scalar=.000000001):
    '''
    Ensure no two points have the same coords or else the number
    of regions will be less than the number of input points
    '''
    while self.points_contain_duplicates():
      positive = np.random.rand( len(self.points), 2 ) * scalar
      negative = np.random.rand( len(self.points), 2 ) * scalar
      self.points = self.points + positive - negative
      self.constrain_points()


  def constrain_points(self):
    '''
    Update any points that have drifted beyond the boundaries of this space
    '''
    for point in self.points:
      if point[0] < self.domains['x']['min']: point[0] = self.domains['x']['min']
      if point[0] > self.domains['x']['max']: point[0] = self.domains['x']['max']
      if point[1] < self.domains['y']['min']: point[1] = self.domains['y']['min']
      if point[1] > self.domains['y']['max']: point[1] = self.domains['y']['max']


  def get_domains(self, arr):
    '''
    Return an object with the x, y domains of `arr`
    '''
    x = arr[:, 0]
    y = arr[:, 1]
    return {
      'x': {
        'min': min(x),
        'max': max(x),
      },
      'y': {
        'min': min(y),
        'max': max(y),
      }
    }


  def get_bb_points(self, arr):
    '''
    Given an array of 2D points, return the four vertex bounding box
    '''
    return np.array([
      [self.domains['x']['min'], self.domains['y']['min']],
      [self.domains['x']['max'], self.domains['y']['min']],
      [self.domains['x']['min'], self.domains['y']['max']],
      [self.domains['x']['max'], self.domains['y']['max']],
    ])


  def build_voronoi(self):
    '''
    Build a voronoi map from self.points. For background on
    self.voronoi attributes, see: https://docs.scipy.org/doc/scipy/
      reference/generated/scipy.spatial.Voronoi.html
    '''
    # build the voronoi tessellation map
    self.voronoi = Voronoi(self.points, qhull_options='Qbb Qc Qx')

    # constrain voronoi vertices within bounding box
    if self.constrain:
      for idx, vertex in enumerate(self.voronoi.vertices):
        x, y = vertex
        if x < self.domains['x']['min']:
          self.voronoi.vertices[idx][0] = self.domains['x']['min']
        if x > self.domains['x']['max']:
          self.voronoi.vertices[idx][0] = self.domains['x']['max']
        if y < self.domains['y']['min']:
          self.voronoi.vertices[idx][1] = self.domains['y']['min']
        if y > self.domains['y']['max']:
          self.voronoi.vertices[idx][1] = self.domains['y']['max']


  def points_contain_duplicates(self):
    '''
    Return a boolean indicating whether self.points contains duplicates
    '''
    vals, count = np.unique(self.points, return_counts=True)
    return np.any(vals[count > 1])


  def find_centroid(self, vertices):
    '''
    Find the centroid of a Voroni region described by `vertices`,
    and return a np array with the x and y coords of that centroid.
    The equation for the method used here to find the centroid of a
    2D polygon is given here: https://en.wikipedia.org/wiki/
      Centroid#Of_a_polygon
    @params: np.array `vertices` a numpy array with shape n,2
    @returns np.array a numpy array that defines the x, y coords
      of the centroid described by `vertices`
    '''
    area = 0
    centroid_x = 0
    centroid_y = 0
    for i in range(len(vertices)-1):
      step = (vertices[i  , 0] * vertices[i+1, 1]) - \
             (vertices[i+1, 0] * vertices[i  , 1])
      area += step
      centroid_x += (vertices[i, 0] + vertices[i+1, 0]) * step
      centroid_y += (vertices[i, 1] + vertices[i+1, 1]) * step
    area /= 2
    # prevent division by zero - equation linked above
    if area == 0: area += 0.0000001
    centroid_x = (1.0/(6.0*area)) * centroid_x
    centroid_y = (1.0/(6.0*area)) * centroid_y
    # prevent centroids from escaping bounding box
    if self.constrain:
      if centroid_x < self.domains['x']['min']: centroid_x = self.domains['x']['min']
      if centroid_x > self.domains['x']['max']: centroid_x = self.domains['x']['max']
      if centroid_y < self.domains['y']['min']: centroid_y = self.domains['y']['min']
      if centroid_y > self.domains['y']['max']: centroid_y = self.domains['y']['max']
    return np.array([centroid_x, centroid_y])


  def relax(self):
    '''
    Moves each point to the centroid of its cell in the voronoi
    map to "relax" the points (i.e. jitter the points so as
    to spread them out within the space).
    '''
    centroids = []
    for idx in self.voronoi.point_region:
      # the region is a series of indices into self.voronoi.vertices
      # remove point at infinity, designated by index -1
      region = [i for i in self.voronoi.regions[idx] if i != -1]
      # enclose the polygon
      region = region + [region[0]]
      # get the vertices for this region
      verts = self.voronoi.vertices[region]
      # find the centroid of those vertices
      centroids.append(self.find_centroid(verts))
    self.points = np.array(centroids)
    self.constrain_points()
    self.jitter_points()
    self.build_voronoi()


  def get_points(self):
    '''
    Return the input points in the new projected positions
    @returns np.array a numpy array that contains the same number
      of observations in the input points, in identical order
    '''
    return self.points