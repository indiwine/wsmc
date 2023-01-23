from .models.vatadetectormodel import VataDetectorModel

_models = {}


def load_models():
    inst = VataDetectorModel()
    inst.load()
    _models[VataDetectorModel] = inst


def get_model():
    return _models[VataDetectorModel]
