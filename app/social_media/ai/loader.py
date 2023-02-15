from .models.vatadetectormodel import VataDetectorModel

_models = {}


# TODO: Add real logic here
def load_models():
    inst = VataDetectorModel()
    inst.load()
    _models[VataDetectorModel] = inst


def get_model() -> VataDetectorModel:
    if VataDetectorModel not in _models:
        raise RuntimeError("AI models haven't been loaded. Check 'WSMC_LOAD_AI' env var.")
    return _models[VataDetectorModel]
