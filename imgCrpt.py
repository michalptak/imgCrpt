#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# AES CBC image encryption GUI.

import sys
import os.path
import hashlib
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
    QDesktopWidget, QHBoxLayout, QVBoxLayout, QMainWindow,
    QTextEdit, QAction, QFileDialog, QLabel, QInputDialog,
    QMessageBox, QLineEdit)
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from PIL import Image


def crypt(passwd, mode):
    # Set initialization vector for simplicity.
    # It should be random and stored though.
    IV = 16*b'\x00'

    # Open image and extract the raw pixel data.
    im = Image.open(f)
    data = im.tobytes()

    # Get the original data length to upnad it after enc/dec process.
    dlength = len(data)

    # If the data is not a multiple of 16, pad it to satisfy AES's req.
    if dlength % 16 != 0:
        data = Padding.pad(data, 16)

    # Encrypt/decrypt image data using AES CBC mode.
    aes = AES.new(passwd, AES.MODE_CBC, IV)
    if mode == 'enc':
        cdata = aes.encrypt(data)
    elif mode == 'dec':
        cdata = aes.decrypt(data)

    # Unpad the data.
    imfinal = cdata[:dlength]

    # Create a new PIL object and put encrypted image data into it.
    im2 = Image.frombytes("RGB", im.size, imfinal)

    # Get file extension.
    fext = os.path.splitext(f)[1][1:]

    # Save image.
    im2.save(os.path.splitext(f)[0] + '_' + mode + '.' + fext,
                 'JPEG' if fext.lower() == 'jpg' else fext)

    showSuccessDialog(im2)

# Mapping the RGB
def toRGB(data):
    r, g, b = tuple(map(lambda d: [data[i] for i in range(0,len(data))
                    if i % 3 == d], [0, 1, 2]))
    pixels = tuple(zip(r,g,b))
    return pixels

def showInfoDialog():
    QMessageBox.information(enc, 'File not detected',
        'Choose an image first.')

def showSuccessDialog(im):
    btnInput = QMessageBox.information(enc, 'Operation completed',
        'Press Open to see the result.', QMessageBox.Open |
        QMessageBox.Close)
    if btnInput == QMessageBox.Open:
        im.show()

def showInputDialog(mode):
    try:
        if f:
            password, ok = QInputDialog.getText(enc, 'Password',
                'Enter the password:', QLineEdit.Password)
            if not password and ok:
                QMessageBox.information(enc, 'No password entered',
                    'Enter the password first.')
            elif password and ok:
                hpass = hashlib.sha256(password.encode()).digest()
                crypt(hpass, mode)
    except NameError:
        showInfoDialog()

def showFileDialog():
    fname = QFileDialog.getOpenFileName(enc, 'OpenFile',
        '', 'Images (*.jpeg *.jpg *.bmp *.png)')
    if fname[0]:
        global f
        f = fname[0]

# GUI
class Crypto(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Buttons
        self.encryptButton = QPushButton('Encrypt')
        self.decryptButton = QPushButton('Decrypt')
        self.openButton = QPushButton(QIcon('open-archive.svg'), '',
                                        self)

        self.openButton.clicked.connect(showFileDialog)
        self.encryptButton.clicked.connect(
                    lambda : showInputDialog('enc'))
        self.decryptButton.clicked.connect(
                    lambda : showInputDialog('dec'))

        # Layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.encryptButton)
        hbox.addWidget(self.decryptButton)

        hbox2 = QHBoxLayout()
        hbox2.addStretch()
        hbox2.addWidget(self.openButton)

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # Window properties.
        self.setFixedSize(250, 200)
        self.center()
        self.setWindowTitle('Image Encryption')
        self.setWindowIcon(QIcon('user-secret.svg'))

        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        self.drawImage(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(102, 0, 255))
        qp.setFont(QFont('Times', 9))
        qp.drawText(130, 152, 'choose image')

        try:
            # Show selected file's name.
            imgname = os.path.basename(f)
            if len(imgname) > 16:
                imgname = os.path.basename(f)[:13] + '...'
            qp.drawText(15, 152, imgname)
        except NameError:
            qp.drawText(15, 152, '')

    # Show selected or default image.
    def drawImage(self, event, qp):
        try:
            qp.drawPixmap(65, 10, 120, 120, QPixmap(f))
        except NameError:
            qp.drawPixmap(65, 10, 120, 120, QPixmap('user-secret.svg'))

    # Center app window.
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    enc = Crypto()
    sys.exit(app.exec_())
