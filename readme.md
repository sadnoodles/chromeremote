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
from chromeremote import ChromeTabThread


def print_ret(kwargs):
    # This func will be called when received a registed chrome event.
    assert kwargs.has_key('current_tab')
    print kwargs
    return


class ExampleTab(ChromeTabThread):

    def test_recv(self, result):
        # Handle received result here.
        print "Received result:", result

    def run(self):
        self.register_event("Network.responseReceived",
                            print_ret)  # Register a event before thread started.
        self.open_tab()
        self.Network.enable(maxTotalBufferSize=10000000,
                            maxResourceBufferSize=5000000)
        self.Page.enable(callback=self.test_recv)  # You can add callback for every request.
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

A XSS detection Example is added. See [xssbot.py](./examples/xssbot.py) Thanks for [howmp](https://github.com/howmp).

Generator example: [generator_example.py](./examples/generator_example.py)
Screenshot example: [screenshot.py](./examples/screenshot.py)