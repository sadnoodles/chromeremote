#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import websocket
import threading
import time
from functools import partial
import json
import traceback
import warnings


class WSMethod(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = self.name + "." + attr
        return partial(self.parent.ws_send, func_name)


class TabTimeout(Exception):
    pass


class Result(object):
    def __init__(self, message_id, func_name, callback=None):
        self.message_id = message_id
        self.func_name = func_name
        self.ready = False
        self.result = None
        self.callback = callback

    def set_result(self, result):
        self.result = result
        self.ready = True

    def __str__(self):
        return "<Result object <message id>: %s, <method>: %s, <ready>: %s, <result>: %s>" % (
            self.message_id, self.func_name, self.ready, self.result)


class ChromeDevToolsConnection(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_commad(self, method='', arg='', data=None):
        if not method:
            url = "http://{host}:{port}/json"
        else:
            url = "http://{host}:{port}/json/{method}/"
            if arg:
                url += "{arg}"

        url = url.format(
            host=self.host,
            port=self.port,
            method=method,
            arg=arg,
        )
        if data is None:
            resp = requests.get(url)
        else:
            resp = requests.post(url, data)

        if resp.status_code >= 400:
            raise requests.HTTPError(
                "<code>: {}, <mesage>:{}.".format(resp.status_code,
                                                  resp.text))

        return resp

    def get_tabs(self):
        resp = self.list()
        return resp.json()

    def new_tab(self, tab_info=None):
        tab = ChromeTab(connection=self)
        tab.open_tab(tab_info)
        return tab

    def __getattr__(self, func_name):
        return partial(self.send_commad, func_name)


class ChromeTab(object):

    WS_TIMEOUT = 0.2
    TAB_TIMEOUT = 60 * 60 * 2  # Close this tab after 2 hours.

    def __init__(self, host=None, port=None, connection=None, ws_timeout=0.2):
        if isinstance(connection, ChromeDevToolsConnection):
            # Using existing ChromeDevToolsConnection instance
            self.conn = connection
        else:
            # Initialize a new ChromeDevToolsConnection instance
            host = host or '127.0.0.1'
            port = port or 9222
            self.conn = ChromeDevToolsConnection(host, port)

        self.message_id = 0
        self.msg_lok = threading.Lock()
        self.tab_id = None
        self.ws = None
        self.ws_timeout = ws_timeout or self.WS_TIMEOUT
        self.start_time = 0
        self._running = True
        self._message_callbacks = {}
        self._events_callbacks = {}

    def get_message_id(self):
        self.msg_lok.acquire()
        self.message_id += 1
        msg_id = self.message_id
        self.msg_lok.release()
        return msg_id

    def _add_message_callback(self, message_id, func_name, callback):
        res = Result(
            message_id, func_name, callback)
        self._message_callbacks[message_id] = res
        return res

    def open_tab(self, tab_info=None):
        '''
        Open a new tab if tab_info not provided.
        "tab_info" if a dict get from http://{host}:{port}/json
        '''
        if tab_info:
            if not (isinstance(tab_info, dict) and
                    tab_info.has_key('id')
                    ):
                raise ValueError(
                    "'tab_info' must be a dict and contains key 'id'.")
            else:
                if not tab_info.has_key('webSocketDebuggerUrl'):
                    raise ValueError(
                        "'tab_info' has no 'webSocketDebuggerUrl', maybe Its in use.")
        else:
            resp = self.conn.new()
            tab_info = resp.json()
        self.tab_id = tab_info['id']
        self.connect_ws(tab_info['webSocketDebuggerUrl'])
        return self

    def connect_ws(self, ws_url):
        if self.ws:
            self.close_ws()
        self.ws = websocket.create_connection(ws_url)
        self.ws.settimeout(self.ws_timeout)

    def ws_send(self, func_name, **kwargs):
        callback = kwargs.pop('callback', None)
        message_id = self.get_message_id()
        call_obj = {"id": message_id,
                    "method": func_name, "params": kwargs}
        self.ws.send(json.dumps(call_obj))
        result = self._add_message_callback(
            message_id, func_name, callback)
        return result

    def register_event(self, event_name, function):
        if not callable(function):
            raise TypeError("function must be a callable.")
        self._events_callbacks[event_name] = function

    def unregister_event(self, event_name):
        return self._events_callbacks.pop(event_name, None)

    def get_status(self):
        "Return this tab is busy not not."
        raise NotImplementedError

    def close_ws(self):
        if not self.ws:
            return
        try:
            self.ws.close()
        except websocket.WebSocketConnectionClosedException:
            pass

    def close_tab(self):
        closed = False
        self._running = False
        if self.ws:
            self.close_ws()
        try:
            resp = self.conn.close(self.tab_id)
            if "Target is closing" in resp.text:
                closed = True
        except:
            closed = False

        return closed

    def kill(self):
        self.close_tab()

    def __getattr__(self, attr):
        self.check_ws_ready()
        genericelement = WSMethod(attr, self)
        self.__setattr__(attr, genericelement)
        return genericelement

    def handle_message_callback(self, message_id, result):
        # print "length of message_callbacks", len(self._message_callbacks)
        if not self._message_callbacks.has_key(message_id):
            raise ValueError
        callback_result = self._message_callbacks.pop(message_id)

        try:
            callback_result.set_result(result.copy())
            result['current_tab'] = self
            if not callback_result.callback:
                return
            callback_result.callback(result)
        except Exception as e:
            msg = ("Got an exception in message callback, "
                   "<message id>:{} ,"
                   "<request function>:{} ,"
                   "<callback function>:{} ")
            print(msg.format(
                message_id,
                callback_result.func_name,
                callback_result.callback))
            traceback.print_exc()

    def handle_event_callback(self, event_name, params):
        if not self._events_callbacks.has_key(event_name):
            return
        func = self._events_callbacks[event_name]
        try:
            params['current_tab'] = self
            func(params)
        except Exception as e:
            msg = ("Got an exception in event callback, "
                   "<event name>:{} ,"
                   "<callback function>:{} ")
            print(msg.format(
                event_name,
                func))
            traceback.print_exc()

    def handle_messages(self, parsed_message):
        if parsed_message.has_key('id') and parsed_message.has_key('result'):
            self.handle_message_callback(
                parsed_message['id'], parsed_message['result'])
        elif parsed_message.has_key('method') and parsed_message.has_key('params'):
            self.handle_event_callback(
                parsed_message['method'], parsed_message['params'])

    def check_ws_ready(self):
        if not self.ws:
            raise ValueError("Tab is not initialized.")

    def messages(self, auto_handle_message=True, timeout_return_none=False):
        self.start_time = time.time()
        self.check_ws_ready()
        while self._running:

            # check tab max timeout
            now = time.time()
            if now - self.start_time > self.TAB_TIMEOUT:
                raise TabTimeout()

            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                if auto_handle_message:
                    self.handle_messages(parsed_message)
                yield parsed_message
            except websocket.WebSocketTimeoutException:
                if timeout_return_none:
                    yield None
                continue
            except websocket.WebSocketConnectionClosedException:
                break
            except KeyboardInterrupt:
                break

    def run(self):
        if not self.tab_id and not self.ws:
            self.open_tab()
        for i in self.messages(auto_handle_message=False):
            self.handle_messages(i)
        self.close_tab()


class ChromeTabThread(ChromeTab, threading.Thread):

    def __init__(self, host=None, port=None, connection=None, ws_timeout=0.2):
        super(ChromeTabThread, self).__init__(
            host, port, connection, ws_timeout)
        super(ChromeTab, self).__init__()

    def run(self):
        if not self.tab_id and not self.ws:
            self.open_tab()
        for i in self.messages():
            pass
        self.close_tab()


def main():
    w1 = ChromeTabThread('127.0.0.1', 9222)
    w1.start()
    time.sleep(2)
    w1.kill()
    time.sleep(1)
    print w1.isAlive()


if __name__ == '__main__':
    main()
