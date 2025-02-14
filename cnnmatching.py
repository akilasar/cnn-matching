import argparse
import cv2
import numpy as np
import imageio
import plotmatch
from lib.cnn_feature import cnn_feature_extract
import matplotlib.pyplot as plt
import time
from skimage import measure
from skimage import transform

# #time count
# start = time.perf_counter()

_RESIDUAL_THRESHOLD = 30
#Test1nThbg6kXUpJWGl7E1IGOCspRomTxdCARLviKw6E5SY8
imgfile1 = '../runs/segment/predict/crops/heron-boats/image0.jpg'
imgfile2 = '../runs/segment/predict/crops/heron-boats/image09.jpg'

# start = time.perf_counter()

# read left image
image1 = cv2.imread(imgfile1)
image2 = cv2.imread(imgfile2)

# print('read image time is %6.3f' % (time.perf_counter() - start))

# start0 = time.perf_counter()

kps_left, sco_left, des_left = cnn_feature_extract(image1,  nfeatures = -1)
kps_right, sco_right, des_right = cnn_feature_extract(image2,  nfeatures = -1)

print('Feature_extract time is %6.3f, left: %6.3f,right %6.3f' % ((time.perf_counter() - start), len(kps_left), len(kps_right)))
start = time.perf_counter()

FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=40)
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des_left, des_right, k=2)

goodMatch = []
locations_1_to_use = []
locations_2_to_use = []

min_dist = 1000
max_dist = 0
disdif_avg = 0
for m, n in matches:
    disdif_avg += n.distance - m.distance
disdif_avg = disdif_avg / len(matches)

for m, n in matches:
    if n.distance > m.distance + disdif_avg:
        goodMatch.append(m)
        p2 = cv2.KeyPoint(kps_right[m.trainIdx][0],  kps_right[m.trainIdx][1],  1)
        p1 = cv2.KeyPoint(kps_left[m.queryIdx][0], kps_left[m.queryIdx][1], 1)
        locations_1_to_use.append([p1.pt[0], p1.pt[1]])
        locations_2_to_use.append([p2.pt[0], p2.pt[1]])
print('match num is %d' % len(goodMatch))
locations_1_to_use = np.array(locations_1_to_use)
locations_2_to_use = np.array(locations_2_to_use)

_, inliers = measure.ransac((locations_1_to_use, locations_2_to_use),
                          transform.AffineTransform,
                          min_samples=3,
                          residual_threshold=_RESIDUAL_THRESHOLD,
                          max_trials=1000)

print('Found %d inliers' % sum(inliers))

inlier_idxs = np.nonzero(inliers)[0]
matches = np.column_stack((inlier_idxs, inlier_idxs))
print('whole time is %6.3f' % (time.perf_counter() - start0))

plt.rcParams['savefig.dpi'] = 100 #图片像素
plt.rcParams['figure.dpi'] = 100 #分辨率
plt.rcParams['figure.figsize'] = (4.0, 3.0) # 设置figure_size尺寸
_, ax = plt.subplots()
plotmatch.plot_matches(
    ax,
    image1,
    image2,
    locations_1_to_use,
    locations_2_to_use,
    np.column_stack((inlier_idxs, inlier_idxs)),
    plot_matche_points = False,
    matchline = True,
    matchlinewidth = 0.3)
ax.axis('off')
ax.set_title('')
plt.show()