# Chrome Remote

A tool for Chrome remote dev debugging. Support:

1. Method callback.
2. Event callback.
3. Threaded. Async return.

## Install

1. use pip:

`pip install chromeremote`

2. Download this repo and run:

`pip install .` or `python set.py install`

3. from git:

`pip install git+https://github.com/sadnoodles/chromeremote` 

This commad require git.exe.

## Example

First use `chrome.exe --remote-debugging-port=9222` start Chrome ( need close all existing chrome windows first). Then run the example with: `python example.py`. This a simple example for how to use callback.

```python

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chromeremote import ChromeTab


def print_ret(kwargs):
    # 在此处处理chrome的Event主动调用
    assert kwargs.has_key('current_tab')
    print kwargs
    return


class ExampleTab(ChromeTab):

    def test_recv(self, result):
        # 在此处处理Method调用的返回结果
        print "Received result:", result

    def run(self):
        self.register_event("Network.responseReceived",
                            print_ret)  # 提前注册chrome会主动调用的函数。
        self.open_tab()
        self.Network.enable(maxTotalBufferSize=10000000,
                            maxResourceBufferSize=5000000)
        self.Page.enable(callback=self.test_recv)  # 每一个请求都可以有一个回调函数。
        self.Page.navigate(url='http://www.baidu.com/')
        self.Page.getResourceTree()
        super(ExampleTab, self).run()


def main():
    import time
    tab = ExampleTab('127.0.0.1', 9222)
    tab.start()
    time.sleep(10)
    tab.kill()
    time.sleep(2)


if __name__ == '__main__':
    main()

```



