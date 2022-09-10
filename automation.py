import asyncio
import random

import pyautogui


async def move_to(p: (int, int)):
    pyautogui.moveTo(p)
    await asyncio.sleep(0.5)


async def click(p: (int, int)):
    await move_to(p)
    pyautogui.click(p)
    await asyncio.sleep(0.5)


async def scroll(delta: int):
    pyautogui.scroll(delta)
    await asyncio.sleep(0.02)

async def press(key:str):
    pyautogui.press(key)
    await asyncio.sleep(.3)


async def write(text: str):
    i = 0
    while i < len(text):
        added = random.randint(3, 7)
        pyautogui.write(text[i:i + added])
        i += added
        await asyncio.sleep(random.random() * 0.1)
    await asyncio.sleep(0.1)
