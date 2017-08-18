#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chromeremote import ChromeTab, TabTimeout
import time


class CallbackFuncs(object):

    def __init__(self, domain):
        self.domain = domain

    def print_ret(self, kwargs):
        # This func will be called when received a registed chrome event.
        print kwargs

    def go_to_not_found(self, kwargs):
        # Handle received result here.
        current_tab = kwargs.get('current_tab')
        current_tab.Page.navigate(
            url='http://{domain}/non_exists_path'.format(domain=self.domain))


def main():
    import time
    callbacks = CallbackFuncs('www.baidu.com')
    tab = ChromeTab('127.0.0.1', 9222)

    # Register a event before started so you can capture all events.
    tab.register_event("Network.responseReceived",
                       callbacks.print_ret)

    # Open a new tab.
    tab.open_tab()

    # Some settings:
    tab.Network.enable(
        maxTotalBufferSize=10000000,
        maxResourceBufferSize=5000000)
    tab.Page.enable()

    # Request a URL
    tab.Page.navigate(url='http://www.baidu.com/')
    # You can add callback for every request.
    tab.Page.getResourceTree(callback=callbacks.go_to_not_found)
    try:
        for msg in tab.messages(timeout_return_none=True):
            if time.time() - tab.start_time > 5:
                # Custom timeout
                break
            if msg is None:
                # If you want to save the waitting time to do something else, set timeout_return_none to True
                # Otherwise ignore this param.
                continue

            if msg.get('method', None) == 'Network.dataReceived':
                # You can handle unregisted or registed events here by the
                # method name. Or just use callbacks for all.
                print('Do something here with this message.')
                print('See more methods(event) for NetWork at https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-resourceChangedPriority .')
    except TabTimeout:
        # Global tab timeout.
        pass
    tab.kill()
    time.sleep(2)


if __name__ == '__main__':
    main()
