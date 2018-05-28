#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chromeremote import ChromeTabThread


def print_ret(kwargs):
    # This func will be called when received a registed chrome event.
    assert 'current_tab' in kwargs
    print(kwargs)
    return


class ExampleTab(ChromeTabThread):

    def test_recv(self, result):
        # Handle received result here.
        print("Received result:", result)

    def run(self):
        self.register_event("Network.responseReceived",
                            print_ret)  # Register a event before thread started.
        self.open_tab()
        self.Network.enable(maxTotalBufferSize=10000000,
                            maxResourceBufferSize=5000000)
        # You can add callback for every request.
        self.Page.enable(callback=self.test_recv)
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
