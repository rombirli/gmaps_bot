import asyncio

from automation import click
from images import find


class BotRemove:
    def __init__(self):
        self.is_running = False

    async def run(self):
        self.is_running = True
        while self.is_running:
            dots= list(find('dot', threshold=0.98))
            if dots:
                await click(dots[0])
                removes= list(find('remove'))
                if removes:
                    await click(removes[0])
                    remove_confirmations= list(find('remove_confirmation'))
                    if remove_confirmations:
                        await click(remove_confirmations[0])
            await asyncio.sleep(.5)

    def stop(self):
        self.is_running = False


if __name__ == '__main__':
    bot = BotRemove()
    try:
        asyncio.run(bot.run())
    except OSError:
        bot.stop()
        print('Ctrl Alt Del. Killing bot')

    except KeyboardInterrupt:
        bot.stop()
        print('Ctrl C. Killing bot')
