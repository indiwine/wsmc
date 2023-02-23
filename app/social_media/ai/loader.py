from .models.vatadetectormodel import VataDetectorModel

_models = {}


# TODO: Add real logic here
def load_models():
    if VataDetectorModel not in _models:
        inst = VataDetectorModel()
        inst.load()
        _models[VataDetectorModel] = inst


def get_model() -> VataDetectorModel:
    if VataDetectorModel not in _models:
        load_models()
    return _models[VataDetectorModel]
