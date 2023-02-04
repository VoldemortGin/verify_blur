import shutil
from pathlib import Path
from typing import Union

import cv2
import hydra
import numpy as np
from fastai.vision.utils import verify_image, get_image_files

# from fastai.vision.all import get_image_files
from omegaconf import DictConfig

from image_crop_gt_for_dir import crop_dir


def variance_of_laplacian(image: np.ndarray) -> float:
    """
    Calculate the Laplacian of the image and then return the focus measure,
    which is simply the variance of the Laplacian

    :param image:
    :return:
    """
    assert len(image.shape) == 2, 'The channel of the image must be 1.'
    return cv2.Laplacian(image, cv2.CV_64F).var()


def save(
    blur_threshold: float,
    calculate_threshold: float,
    blur_dir: Union[str, Path],
    distinct_dir: Union[str, Path],
    i_path: Union[str, Path],
    image: np.ndarray,
) -> None:
    """
    This function saves the image to the blur_dir and the distinct_dir.
    The blur_dir and the distinct_dir are created if they do not exist.

    :param blur_threshold: threshold set in the configuration.
    :param calculate_threshold:
    :param blur_dir:
    :param distinct_dir:
    :param i_path:
    :param image:
    :return:
    """
    i_path = Path(i_path)
    blur_dir = Path(blur_dir)
    distinct_dir = Path(distinct_dir)

    blur_dir.mkdir(parents=True, exist_ok=True)
    distinct_dir.mkdir(parents=True, exist_ok=True)

    if calculate_threshold < blur_threshold:
        cv2.imwrite(str(blur_dir / i_path.name), image)
        shutil.copy(
            i_path.with_suffix('.json'), blur_dir / i_path.with_suffix('.json').name
        )
    else:
        cv2.imwrite(str(distinct_dir / i_path.name), image)
        shutil.copy(
            i_path.with_suffix('.json'), distinct_dir / i_path.with_suffix('.json').name
        )


@hydra.main(
    version_base=None, config_path='configs', config_name='object_detection.yaml'
)
def main(cfg: DictConfig) -> None:
    """
    This is the main function of the script.

    :param cfg: No need to add this args, hydra will take care of it.
    :return:
    """
    print('Starting', cfg['task_name'])
    base = Path(cfg['base_dir'])
    assert base.is_dir(), f'{base} is not a directory'
    blur_dir = base / cfg['blur_dir']
    blur_dir.mkdir(parents=True, exist_ok=True)
    distinct_dir = base / cfg['distinct_dir']
    distinct_dir.mkdir(parents=True, exist_ok=True)
    blur_crop_dir = base / cfg['blur_crop_dir']
    blur_crop_dir.mkdir(parents=True, exist_ok=True)
    distinct_crop_dir = base / cfg['distinct_crop_dir']
    distinct_crop_dir.mkdir(parents=True, exist_ok=True)
    blur_threshold = cfg['blur_threshold']
    labelme_dir = cfg['labelme_dir']
    # save_dir = cfg['save_dir']
    temp_dir = cfg['temp_dir']
    padding = cfg['padding']

    # First create
    crop_dir(labelme_dir=labelme_dir, save_dir=temp_dir, padding=padding)
    for i in get_image_files(temp_dir):
        image = cv2.imread(str(i))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        calculate_threshold = variance_of_laplacian(image=image)

        print(f'{i.name}\'s calculate_threshold: {calculate_threshold}')

        save(
            blur_threshold=blur_threshold,
            calculate_threshold=calculate_threshold,
            blur_dir=blur_crop_dir,
            distinct_dir=distinct_crop_dir,
            i_path=i,
            image=image,
        )

    # The whole picture should be copied to the blur directory,
    # as long as there is a crop picture cropped from it in the blur_crop directory.
    blur_list = list(set([i.name.split('_')[0] for i in get_image_files(blur_crop_dir)]))
    for i in get_image_files(labelme_dir):
        if i.name in blur_list:
            shutil.copy(i, blur_dir / i.name)
            shutil.copy(i.with_suffix('.json'), blur_dir / i.with_suffix('.json'))
        else:
            shutil.copy(i, distinct_dir / i.name)
            shutil.copy(i.with_suffix('.json'), distinct_dir / i.with_suffix('.json').name)


if __name__ == '__main__':

    main()
