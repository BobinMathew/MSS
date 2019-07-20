# -*- coding: utf-8 -*-
"""

    mslib.msui.mscolab_project
    ~~~~~~~~~~~~~~~~~~~~~

    Mscolab project window, to display chat, file change

    This file is part of mss.

    :copyright: 2019 Shivashis Padhi
    :license: APACHE-2.0, see LICENSE for details.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from mslib.msui.mss_qt import QtCore, QtWidgets, QtGui
from mslib.msui.mss_qt import ui_mscolab_project_window as ui
from mslib._tests.constants import MSCOLAB_URL

import logging
import requests
import json


class MSColabProjectWindow(QtWidgets.QMainWindow, ui.Ui_MscolabProject):
    """Derives QMainWindow to provide some common functionality to all
       MSUI view windows.
    """
    name = "MSColab Project Window"
    identifier = None

    viewCloses = QtCore.pyqtSignal(name="viewCloses")

    def __init__(self, token, p_id, conn, parent=None):
        """
        token: access_token
        p_id: project id
        conn: to send messages, recv messages, if a direct slot-signal can't be setup
            to be connected at parents'
        """
        super(MSColabProjectWindow, self).__init__(parent)
        self.setupUi(self)
        # constrain vertical layout
        self.verticalLayout_6.setSizeConstraint(self.verticalLayout_6.SetMinimumSize)
        self.token = token
        self.p_id = p_id
        self.conn = conn
        logging.debug(ui.Ui_MscolabProject)
        # establish button press handlers
        self.add.clicked.connect(self.add_handler)
        self.modify.clicked.connect(self.modify_handler)
        self.delete_1.clicked.connect(self.delete_handler)
        # send message handler
        self.sendMessage.clicked.connect(self.send_message)
        # load users
        self.load_users()
        # test widget add
        for i in range(50):
            item = QtWidgets.QListWidgetItem("dummy str" * 20 + "\n\n", parent=self.messages)
            self.messages.addItem(item)
        self.messages.setWordWrap(True)

    def send_message(self):
        """
        send message through connection
        """
        message_text = self.messageText.toPlainText()
        self.conn.send_message(message_text, self.p_id)

    def add_handler(self):
        # get username, p_id
        username = self.username.text()
        access_level = str(self.accessLevel.currentText())
        # send request to add
        data = {
            "token": self.token,
            "p_id": self.p_id,
            "username": username,
            "access_level": access_level
        }
        r = requests.post(MSCOLAB_URL + '/add_permission', data=data)
        if r.text == "True":
            self.load_users()
        else:
            # show a QMessageBox with errors
            pass

    def modify_handler(self):
        # get username, p_id
        username = self.username.text()
        access_level = str(self.accessLevel.currentText())
        # send request to modify
        data = {
            "token": self.token,
            "p_id": self.p_id,
            "username": username,
            "access_level": access_level
        }
        r = requests.post(MSCOLAB_URL + '/modify_permission', data=data)
        if r.text == "True":
            self.load_users()
        else:
            # show a QMessageBox with errors
            pass

    def delete_handler(self):
        # get username, p_id
        username = self.username.text()
        p_id = self.p_id
        # send request to delete
        data = {
            "token": self.token,
            "p_id": p_id,
            "username": username
        }
        r = requests.post(MSCOLAB_URL + '/revoke_permission', data=data)
        if r.text == "True":
            self.load_users()
        else:
            # show a QMessageBox with errors
            pass

    def load_users(self):
        # load users to side-tab here

        # make request to get users
        data = {
            "token": self.token,
            "p_id": self.p_id
        }
        r = requests.get(MSCOLAB_URL + '/authorized_users', data=data)
        if r.text == "False":
            # show QMessageBox errors here
            pass
        else:
            self.collaboratorsList.clear()
            users = json.loads(r.text)["users"]
            for user in users:
                item = QtWidgets.QListWidgetItem("{} - {}".format(user["username"],
                                                 user["access_level"]),
                                                 parent=self.collaboratorsList)
                item.username = user["username"]
                self.collaboratorsList.addItem(item)
            self.collaboratorsList.itemActivated.connect(self.update_username_wrt_item)

    def update_username_wrt_item(self, item):
        self.username.setText(item.username)
