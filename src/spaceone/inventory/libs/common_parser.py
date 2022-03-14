import logging
import yaml


_LOGGER = logging.getLogger(__name__)


def get_data_from_yaml(file_path):
    with open(file_path) as f:
        dict = yaml.load(f, Loader=yaml.FullLoader)

    return dict



