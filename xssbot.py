# coding=utf-8
'''
xssbot 必须具有以下功能
1.可对指定url进行访问
2.拦截alert等框框
3.拦截页内跳转
4.锁定设定cookies(未实现)
    在EditThisCookie的chrome扩展中使用扩展特有的接口实现
    chrome.cookies.onChanged.addListener
    但在https://chromedevtools.github.io/devtools-protocol/文档中并没有相关类似功能、


'''
from chromeremote import ChromeTabThread as ChromeTab


class XssbotTab(ChromeTab):
    # 一个页面允许运行10秒
    TAB_TIMEOUT = 10

    def __init__(self, url, host, port):
        super(XssbotTab, self).__init__(host, port)
        self.opened = False
        self.url = url
        self.initjs = '''
window.alert =function(){};
window.confirm =function(){};
window.prompt = function(){};
window.open= function(){};
'''

    def run(self):
        def processNavigation(para):
            # 仅处理第一次我们跳转，其他禁止跳转
            if self.opened:
                response = 'CancelAndIgnore'
            else:
                self.opened = True
                response = 'Proceed'
            self.Page.processNavigation(
                response=response, navigationId=para['navigationId'])

        def javascriptDialogOpening(para):
            # 基本上rewrite后就不会有弹框了，但如果有就关闭弹框
            self.Page.handleJavaScriptDialog(accept=False, promptText='')

        self.open_tab()
        self.Page.enable()
        self.register_event("Page.navigationRequested", processNavigation)
        self.register_event("Page.javascriptDialogOpening",
                            javascriptDialogOpening)
        # 设置所有跳转需要进行管制
        self.Page.setControlNavigations(enabled=True)
        self.Page.addScriptToEvaluateOnLoad(
            scriptSource=self.initjs, identifier='rewrite')

        # 打开设定url
        self.Page.navigate(url=self.url)

        super(XssbotTab, self).run()


if __name__ == '__main__':
    tab = XssbotTab(
        'https://github.com/BugScanTeam/chromeremote', '127.0.0.1', 9222)
    tab.start()
