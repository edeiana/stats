import sys
import numpy as np

import utils

medianTime, variance, medianIt = utils.getTimeAndVariance(sys.argv[1])
print 'Median Time = ' + str(medianTime)
print 'Median Iteration = ' + str(medianIt)
print 'Variance = ' + str(variance)

