#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chromeremote import ChromeTab


def print_ret(kwargs):
    # 在此处处理chrome的主动调用
    assert kwargs.has_key('current_tab')
    print kwargs
    return


class ExampleTab(ChromeTab):

    def test_recv(self, result):
        # 在此处处理调用的返回结果
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
