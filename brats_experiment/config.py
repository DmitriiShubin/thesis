import ast
import os



# names:
DATA_PATH = '../data/brats/MICCAI_BraTS2020_TrainingData/'

SPLIT_TABLE_PATH = './split_table/'
SPLIT_TABLE_NAME = 'split_table.json'

DEBUG_FOLDER = '../data/CV_debug/'

for f in [DEBUG_FOLDER]:
    os.makedirs(f, exist_ok=True)
