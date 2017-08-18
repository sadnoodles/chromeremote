#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chromeremote import ChromeTab, TabTimeout
from base64 import b64decode
from time import time
from functools import partial

LOADING_FINISH = '''
        window.onload=function()
{
    console.log('Finish');
};
        '''


class InitChrome(ChromeTab):
    def __init__(self, host, port):
        super(InitChrome, self).__init__(host, port)


class ScreenShot():
    def __init__(self, tab):
        self.tab = tab
        self.loading_finished = False
        self.screenshot_status = False

    def loading_finish(self, kwargs):
        text = kwargs.get('message').get('text')
        if text == 'Finish':
            self.loading_finished = True

    def screenshot(self, save_path, kwargs):
        'get and write screenshot'
        data = kwargs.get('data')
        with open(save_path, 'wb') as f:
            f.write(b64decode(data))
        self.screenshot_status = True

    def init_setting(self):
        'init chrome setting here'
        self.tab.open_tab()
        self.tab.register_event("Console.messageAdded", self.loading_finish)
        self.tab.Network.enable(
            maxTotalBufferSize=10000000, maxResourceBufferSize=5000000)
        self.tab.Page.enable()
        self.tab.Console.enable()
        self.tab.Page.addScriptToEvaluateOnLoad(
            scriptSource=LOADING_FINISH, identifier='rewrite')

    def run(self, task):
        self.init_setting()
        url = task.get('url')
        save_path = task.get('save_path')
        self.tab.Page.navigate(url=url)
        try:
            for msg in self.tab.messages(timeout_return_none=True):
                if self.loading_finish:
                    self.tab.Page.captureScreenshot(callback=partial(
                        self.screenshot, save_path))
                if self.screenshot_status or time() - self.tab.start_time > 10:
                    break
                if msg is None:
                    continue
        except TabTimeout:
            pass
        finally:
            self.tab.close_tab()


def main():
    tab = InitChrome(host='127.0.0.1', port=9222)
    task = {'url': 'https://www.baidu.com', 'save_path': 'baidu.png'}
    screenshot = ScreenShot(tab=tab)
    screenshot.run(task=task)


if __name__ == '__main__':
    main()