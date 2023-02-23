import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple, Literal

import keras_cv
import tensorflow as tf
from dataclasses_json import dataclass_json
from keras_cv import bounding_box
from keras_cv.metrics import COCOMeanAveragePrecision, COCORecall
from tensorflow import keras

from .basicmodel import BasicModel
from .utils.imagepredictionsequence import ImagePredictionSequence
from .utils.imagesizesequence import ImageSizeSequence

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class VataPredictionItem:
    x: int
    y: int
    width: int
    height: int
    label: Literal['z', 'v', 'colorado', 'russian_flag']
    pr: float


class VataDetectorModel(BasicModel):
    """ Vata23 model to find russian symbols """

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

    BATCH_SIZE = 4

    _model: Optional[keras.Model] = None

    @property
    def name(self) -> str:
        return self._model.name

    def load(self):
        """
        Loads model into memory
        """
        logger.debug(f'Trying to load model from "{self.MODEL_FILES_PATH}"')
        self._model = keras.models.load_model(self.MODEL_FILES_PATH,
                                              compile=False,
                                              custom_objects={'COCOMeanAveragePrecision': COCOMeanAveragePrecision,
                                                              'COCORecall': COCORecall,
                                                              })
        logger.info(f'AI model "{self._model.name}" loaded successfully')
        self._model.summary()

    def predict(self, images: List[str], confidence: float = 0.5, iou: float = 0.5) -> List[List[VataPredictionItem]]:
        """
        Make predictions
        @param images: list of paths to images
        @param confidence: a float value in the range [0, 1]. All boxes with confidence
        below this value will be discarded
        @param iou: a float value in the range [0, 1] representing the minimum
        IoU threshold for two boxes to be considered same for suppression.
        @return: predictions per images. index in images list are corresponding to index in resulting list
        """
        logger.debug(f'Starting prediction of {len(images)} image(s)')
        t0 = time.perf_counter()

        prediction_decoder = self.get_predication_decoder(confidence, iou)
        input_arr, original_sizes = self._read_images(images)
        logger.debug('Images loaded, predicting...')

        raw_predictions = self._model.predict(input_arr,
                                              batch_size=self.BATCH_SIZE,
                                              use_multiprocessing=True,
                                              workers=4
                                              )
        logger.debug('Prediction done, decoding...')
        processed_predictions = []

        for i, imgs in enumerate(input_arr):
            raw_prediction_slice = raw_predictions[i * self.BATCH_SIZE:(i + 1) * self.BATCH_SIZE]
            sizes_slice = original_sizes[i]
            predictions = prediction_decoder(imgs, raw_prediction_slice)
            predictions = self._normalize_predictions(predictions, imgs, sizes_slice)
            processed_predictions = processed_predictions + predictions

        processed_predictions = self._convert_predictions(processed_predictions)

        logger.debug(f'Prediction took: {time.perf_counter() - t0}')
        return processed_predictions

    def _convert_predictions(self, predictions) -> List[List[VataPredictionItem]]:
        def cast_to(tensor, target_type=tf.int32):
            return tf.cast(tensor, target_type).numpy().item()

        result = []
        for boxes in predictions:
            converted_boxes = []
            for box in boxes:
                x, y, width, height, label, pr = box
                item = VataPredictionItem(
                    x=cast_to(x),
                    y=cast_to(y),
                    width=cast_to(width),
                    height=cast_to(height),
                    label=self.CLASS_MAPPING[cast_to(label)],
                    pr=cast_to(pr, tf.float32)
                )
                converted_boxes.append(item)

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

    def _read_images(self, images: List[str]) -> Tuple[ImagePredictionSequence, ImageSizeSequence]:
        generator = ImagePredictionSequence(images, self.BATCH_SIZE, self.IMAGE_SIZE)
        size_sequence = ImageSizeSequence(images, self.BATCH_SIZE)
        return generator, size_sequence

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
