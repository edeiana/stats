import os
import sys

def rmSeedConf(seedConfString):
  if (seedConfString == ''):
    return

  opentunerSeedConfFlag = '--seed-configuration='
  seedConfList = [elem.strip(opentunerSeedConfFlag) for elem in seedConfString.split()]
  for elem in seedConfList:
    if (os.path.isfile(elem)):
      os.remove(elem)

  return


rmSeedConf(sys.argv[1])

