import logging
from pathlib import Path
from typing import Optional, List

import keras_cv
import numpy as np
import tensorflow as tf
from PIL import Image
from keras_cv import bounding_box
from keras_cv.metrics import COCOMeanAveragePrecision, COCORecall
from tensorflow import keras

from .basicmodel import BasicModel

logger = logging.getLogger(__name__)


class VataDetectorModel(BasicModel):
    MODEL_FILES_PATH = Path(__file__).resolve().parent.parent / 'model_files/vata-detector'

    LABELS = [
        "z",
        "v",
        "colorado",
        "russian_flag",
    ]

    CLASS_MAPPING = dict(zip(range(len(LABELS)), LABELS))

    IMAGE_SIZE = (1024, 1024)

    BBOX_FORMAT = 'xywh'

    _model: Optional[keras.Model] = None

    def load(self):
        logger.debug(f'Tring to load model from "{self.MODEL_FILES_PATH}"')
        self._model = keras.models.load_model(self.MODEL_FILES_PATH,
                                              compile=False,
                                              custom_objects={'COCOMeanAveragePrecision': COCOMeanAveragePrecision,
                                                              'COCORecall': COCORecall,
                                                              })
        self._model.compile()
        logger.info(f'AI model "{self._model.name}" loaded successfully')
        self._model.summary()

    def predict(self, images: List[str], confidence: float = 0.5):
        prediction_decoder = self.get_predication_decoder(confidence)
        input_arr, original_sizes = self._read_images(images)
        raw_predictions = self._model.predict(input_arr)
        predictions = prediction_decoder(input_arr, raw_predictions)
        predictions = self._normalize_predictions(predictions, input_arr, original_sizes)
        return self._convert_predictions(predictions)

    def _convert_predictions(self, predictions):
        def cast_to(x, type=tf.int32):
            return tf.cast(x, type).numpy().item()

        result = []
        for boxes in predictions:
            converted_boxes = []
            for box in boxes:
                x, y, width, height, label, pr = box
                converted_boxes.append({
                    'x': cast_to(x),
                    'y': cast_to(y),
                    'width': cast_to(width),
                    'height': cast_to(height),
                    'label': self.CLASS_MAPPING[cast_to(label)],
                    'pr': cast_to(pr, tf.float32)
                })

            result.append(converted_boxes)
        return result

    def _normalize_predictions(self, predictions, input_arr, original_sizes):
        resized_predictions = []
        for i, prediction in enumerate(predictions):
            orig_size = original_sizes[i]
            input_img = input_arr[i]
            clipped_prediction = bounding_box.clip_to_image(prediction, input_img, self.BBOX_FORMAT)
            rel = bounding_box.convert_format(clipped_prediction, self.BBOX_FORMAT, 'rel_yxyx', input_img)
            resized_prediction = bounding_box.convert_format(rel, 'rel_yxyx', self.BBOX_FORMAT,
                                                             image_shape=(orig_size[1], orig_size[0], 3))
            resized_predictions.append(resized_prediction)
        return resized_predictions

    def _read_images(self, images: List[str]):
        input_arr = []
        original_sizes = []
        for img_path in images:
            with open(img_path, "rb") as f:
                pil_img = Image.open(f)
                original_sizes.append(pil_img.size)
                pil_img.close()

            img = keras.utils.load_img(img_path, target_size=self.IMAGE_SIZE)
            input_arr.append(keras.utils.img_to_array(img))

        return np.array(input_arr), original_sizes

    def get_predication_decoder(self, confidence: float = 0.5,
                                iou: float = 0.5) -> keras_cv.layers.NmsPredictionDecoder:
        return keras_cv.layers.NmsPredictionDecoder(
            bounding_box_format=self.BBOX_FORMAT,
            anchor_generator=keras_cv.models.RetinaNet.default_anchor_generator(
                bounding_box_format=self.BBOX_FORMAT
            ),
            suppression_layer=keras_cv.layers.NonMaxSuppression(
                iou_threshold=iou,
                bounding_box_format=self.BBOX_FORMAT,
                classes=len(self.LABELS),
                confidence_threshold=confidence,
            ),
        )
