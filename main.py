import PyFalkon
import PyFalkon as Falkon
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QListWidget, QWidget, QMessageBox, QApplication, QVBoxLayout, QLineEdit
import uuid
from functools import partial
import os
import subprocess
import PySide2
    
class RequestInterceptor(PySide2.QtWebEngineCore.QWebEngineUrlRequestInterceptor):
    def interceptRequest(self,info):
        if info.firstPartyUrl() != self.url:
            print("Blocking URL:", info.requestUrl())
            info.block(True)
            return

class KioskPlugin(PyFalkon.PluginInterface, QtCore.QObject):
    def init(self, state, settingsPath):
        self.url = None
        Falkon.MainApplication.instance().plugins().mainWindowCreated.connect(self.onMainWindowCreated)
        self.profile = Falkon.MainApplication.instance().webProfile()
        
    def onMainWindowCreated(self, window):
        self.window = window
        window.tabWidget().tabInserted.connect(self.newTab)
        self.firstRun = True
        self.newTab(0)

        window.showFullScreen()
        window.toggleShowMenubar()
        window.menuBar().hide()
        window.menuWidget().hide()
        print([i for i in dir(window.tabWidget().webTab(0).webView()) if 'page' in i])
        tab = window.tabWidget().webTab(0)
        tab.webView().urlChanged.connect(self.singleURL)

    def singleURL(self, url):
        if self.url is None:
            self.url = url
            self.interceptor = RequestInterceptor()
            self.interceptor.url = url
            Falkon.MainApplication.instance().webProfile().setUrlRequestInterceptor(self.interceptor)

    def newTab(self, index):
        tab = self.window.tabWidget().webTab(1)
        while tab is not None:
            if self.firstRun:
                self.window.tabWidget().webTab(0).closeTab()
            else:
                tab.closeTab()
            tab = self.window.tabWidget().webTab(1)
        self.window.tabWidget().tabBar().hide()
        self.firstRun = False

    def unload(self):
        print("unload")

    def testPlugin(self):
        return True

PyFalkon.registerPlugin(KioskPlugin())

