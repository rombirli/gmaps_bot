import os

import cv2
import numpy as np
import pyautogui

from config import plot_figures


def find(template: str, threshold: float = 0.8) -> ((int, int), ...):
    global i
    screenshot = pyautogui.screenshot()
    if not os.path.exists('generated'):
        os.mkdir('generated')
    screenshot.save('generated/screenshot.png')
    screenshot = cv2.imread('generated/screenshot.png', 0)
    # match pin template at all position on the screenshot
    template_ = cv2.imread(f'templates/{template}.png', 0)
    w, h = template_.shape[::-1]
    res = cv2.matchTemplate(screenshot, template_, cv2.TM_CCOEFF_NORMED)

    loc = tuple(zip(*np.where(res >= threshold)[::-1]))
    if plot_figures and len(loc) > 0:
        for pt in loc:
            cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        i = 0
        while os.path.exists(f'generated/{template} {i}.png'):
            i += 1
        cv2.imwrite(f'generated/{template} {i}.png', screenshot)
    return tuple(map(lambda pt: (pt[0] + w / 2, pt[1] + h / 2), loc))
