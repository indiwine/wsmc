import math
from typing import List

from PIL import Image
from keras.utils import Sequence


class ImageSizeSequence(Sequence):
    def __init__(self, img_paths: List[str], batch_size: int):
        self._img_paths = img_paths
        self._batch_size = batch_size

    def __getitem__(self, index):
        img_batch = self._img_paths[index * self._batch_size:(index + 1) * self._batch_size]
        return [Image.open(img_path).size for img_path in img_batch]

    def __len__(self):
        return math.ceil(len(self._img_paths) / self._batch_size)
