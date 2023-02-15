import math
from typing import List, Tuple

import numpy as np
from keras.utils import img_to_array as keras_img_to_array, load_img as keras_load_img, Sequence


class ImagePredictionSequence(Sequence):
    def __init__(self, img_paths: List[str], batch_size: int, image_size: Tuple[int, int]):
        self._img_paths = img_paths
        self._batch_size = batch_size
        self._img_size = image_size

    def __getitem__(self, index):
        img_batch = self._img_paths[index * self._batch_size:(index + 1) * self._batch_size]
        return np.array(
            [
                keras_img_to_array(keras_load_img(img_path, target_size=self._img_size)) for img_path in img_batch
            ]
        )

    def __len__(self):
        return math.ceil(len(self._img_paths) / self._batch_size)
