from .models.vatadetectormodel import VataDetectorModel

_models = {}


# TODO: Add real logic here
def load_models():
    inst = VataDetectorModel()
    inst.load()
    _models[VataDetectorModel] = inst


def get_model() -> VataDetectorModel:
    return _models[VataDetectorModel]
