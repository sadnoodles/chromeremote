#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import time
from chromeremote import ChromeDevToolsConnection, ChromeTabThread


def print_ret(kwargs):
    assert kwargs.has_key('current_tab')
    return


class TestConnection(unittest.TestCase):
    def setUp(self):
        self.conn = ChromeDevToolsConnection('127.0.0.1', 9222)

    def test_new_close_tab(self):
        resp = self.conn.new()
        self.assertEqual(resp.status_code, 200)
        ret = resp.json()
        time.sleep(1)
        resp = self.conn.close(ret["id"])
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Target is closing", resp.text)

    def test_get_tabs(self):
        tabs = self.conn.get_tabs()
        self.assertIsInstance(tabs, list)
        self.assertIsInstance(tabs[0], dict)
        self.assertEqual(tabs[0].has_key('id'), True)


class TestTab(unittest.TestCase):
    def setUp(self):
        # Ensure Chrome dev tools is open on 127.0.0.1:9222
        self.tab = ChromeTabThread('127.0.0.1', 9222)
        self.tab.open_tab()

    def test_register_event(self):

        self.tab.register_event("Network.responseReceived", print_ret)
        self.assertEqual(
            self.tab._events_callbacks["Network.responseReceived"], print_ret)

    def test_handle_event(self):
        called = []

        def event_func(kwargs):
            called.append(kwargs["some"])
        self.tab.register_event("Network.responseReceived", event_func)
        self.tab.handle_event_callback(
            "Network.responseReceived", {"some": "thing"})
        self.assertEqual(called[0], "thing")

    def test_handle_event_error(self):
        called = []

        # **kwarg cause error, use func(kwarg) pleas.
        def event_func(**kwargs):
            called.append(kwargs["some"])

        self.tab.register_event("Network.responseReceived", event_func)
        self.tab.handle_event_callback(
            "Network.responseReceived", {"some": "thing"})

    def test_handle_message_callback(self):
        result = self.tab.Page.enable(callback=print_ret)
        self.tab.handle_message_callback(result.message_id, {"hello": "you"})
        self.assertEqual(result.ready, True)
        self.assertEqual(self.tab._message_callbacks.has_key(
            result.message_id), False)

    def test_register_message_callback(self):
        result = self.tab.Page.enable(callback=print_ret)
        in_map = self.tab._message_callbacks[result.message_id]
        self.assertEqual(
            in_map.callback,
            print_ret
        )
        self.assertEqual(
            in_map.func_name,
            "Page.enable"
        )

    def test_close_thread(self):
        tab = ChromeTabThread('127.0.0.1', 9222)
        tab.open_tab()
        tab.start()
        time.sleep(1)
        tab.Page.enable()
        time.sleep(2)
        tab.kill()
        time.sleep(1)
        self.assertEqual(tab.isAlive(), False)

    def test_async_return(self):
        tab = ChromeTabThread('127.0.0.1', 9222)
        tab.open_tab()
        tab.start()
        import time
        tab.open_tab()
        result = tab.Page.enable()
        time.sleep(8)
        tab.kill()
        self.assertEqual(result.ready, True)
        self.assertIsInstance(result.result, dict)

    def tearDown(self):
        self.tab.kill()


if __name__ == '__main__':
    unittest.main()
