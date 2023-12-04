import sys
import utils
import profiler

result = profiler.profile(sys.argv[1])

print result

