import sys

from .batch import Batch

if __name__ == '__main__':
    if len(sys.argv) < 2: raise Exception("Required argument: Batch Path")
    path = sys.argv[1]

    batch = Batch.from_json(path)
    batch.process()