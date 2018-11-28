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

    x = arr[:, 0]
    y = arr[:, 1]
    self.bb = [min(x), max(x), min(y), max(y)]
    self.constrain = kwargs.get('constrain', True)
    self.points = arr
    self.iterations = 0
    self.build_voronoi()


  def build_voronoi(self):
    '''
    Build a voronoi map from self.points. For background on
    self.voronoi attributes, see: https://docs.scipy.org/doc/scipy/
      reference/generated/scipy.spatial.Voronoi.html
    '''

    # remove old pseudo-points and add new pseudo-points to control spread
    if self.constrain:
      if self.iterations:
        self.points = self.points[:-4]
      self.points = np.vstack((self.points, np.array([
        [ self.bb[0], self.bb[2] ],
        [ self.bb[0], self.bb[3] ],
        [ self.bb[1], self.bb[2] ],
        [ self.bb[1], self.bb[3] ],
      ])))

    # ensure no two points have the exact same coords
    self.jitter_points()

    # build the voronoi tessellation map
    self.voronoi = Voronoi(self.points, qhull_options='Qbb Qc Qx')

    # make bounding box (bb) min, max of voronoi vertex positions
    if self.constrain:
      for idx, vertex in enumerate(self.voronoi.vertices):
        x, y = vertex
        if x < self.bb[0]: self.voronoi.vertices[idx][0] = self.bb[0]
        if x > self.bb[1]: self.voronoi.vertices[idx][0] = self.bb[1]
        if y < self.bb[2]: self.voronoi.vertices[idx][1] = self.bb[2]
        if y > self.bb[3]: self.voronoi.vertices[idx][1] = self.bb[3]

    # store the number of voronoi models this instance has built
    # so we can remove pseudo-points in the end
    self.iterations += 1


  def jitter_points(self, scalar=.0000001):
    '''
    Ensure no two points have the same coords or else the number
    of regions will be less than the number of input points
    '''
    s = set()
    while len(s) != len(self.points):
      s = {tuple(i) for i in self.points.tolist()}
      self.points = self.points + np.random.rand( len(self.points), 2 ) * scalar


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
      if centroid_x <= self.bb[0]: centroid_x = self.bb[0]
      if centroid_x >= self.bb[1]: centroid_x = self.bb[1]
      if centroid_y <= self.bb[2]: centroid_y = self.bb[2]
      if centroid_y >= self.bb[3]: centroid_y = self.bb[3]
    return np.array([centroid_x, centroid_y])


  def relax(self):
    '''
    Moves each point to the centroid of its cell in the voronoi
    map to "relax" the points (i.e. jitter the points so as
    to spread them out within the space).
    '''
    centroids = []
    for region in self.voronoi.regions:
      # skip blank regions
      if not region: continue
      # add first region index to region to create enclosed polygon
      region = region + [region[0]]
      # get the vertices for that region
      vertices = self.voronoi.vertices[region]
      # find the centroid of those vertices
      centroid = self.find_centroid(vertices)
      centroids.append(centroid)
    # reorder the centroids into the same order as the input points
    ordered = [None] * len(self.points)
    for idx, i in enumerate(centroids):
      pos = np.where(self.voronoi.point_region == idx)[0][0]
      ordered[pos] = np.array(i)
    self.points = np.vstack([i for i in ordered])
    self.build_voronoi()


  def get_points(self):
    '''
    Return the input points in the new projected positions
    @returns np.array a numpy array that contains the same number
      of observations in the input points, in identical order
    '''
    if self.iterations > 0 and self.constrain:
      return self.points[:-4]
    return self.points