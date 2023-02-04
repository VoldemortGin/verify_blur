import cv2
from pathlib import Path
from fastai.vision.all import get_image_files

save = Path('data/generate_blur')
save.mkdir(parents=True, exist_ok=True)
for i in get_image_files('data/case_ls'):
    img = cv2.imread(str(i))
    blured_img = cv2.GaussianBlur(img, (21, 21), 0)
    cv2.imwrite(str(save / i.name), blured_img)
