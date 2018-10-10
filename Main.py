import sys
import cv2
import numpy as np
from PyQt4 import QtGui, QtCore, Qt, uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QApplication, QDialog, QListWidgetItem, QListWidget, QIcon
from openalpr import Alpr
from argparse import ArgumentParser
import time

alpr = None
cascPath = "pak.xml"
plateCascade = cv2.CascadeClassifier(cascPath)
#video_capture = cv2.VideoCapture('rtsp://admin:admin123@172.16.5.36/streaming/channels/2')
video_capture = cv2.VideoCapture('path video')


value = None
percentage = None

i = 0



class Video():
    def __init__(self, capture):
        self.capture = capture
        self.currentFrame = np.array([])
        # self.unusedFrame = np.array([])
        self.bbFrame = np.array([])
        self.allfaces = None


    def faceDetection(self, frame):
        global value
        global percentage
        alpr = Alpr("pak", "path/config/openalpr.conf",
                    "path/openalpr/runtime_data")

        frame = cv2.resize(frame, (740 , 480))


        faces = plateCascade.detectMultiScale(frame, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30))
        self.allfaces = faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255,0 ), 4)
            cv2.putText(frame,str(value)+"-"+str(percentage) + "%",(x-10,y-10),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)

        if not alpr.is_loaded():
            print("Error loading OpenALPR")
        else:
            print("Using OpenALPR " + alpr.get_version())

            alpr.set_top_n(7)
            alpr.set_default_region("wa")
            alpr.set_detect_region(False)


            cv2.imwrite("1.png",frame)
            jpeg_bytes = open("1.png", "rb").read()

            results = alpr.recognize_array(jpeg_bytes)

            print("Image size: %dx%d" % (results['img_width'], results['img_height']))
            print("Processing Time: %f" % results['processing_time_ms'])
            #print(str(results['results'][0][0]['candidates']['plate']))
            i = 0
            count = 0
            for plate in results['results']:
                i = 1
                print("Plate #%d" % i)
                print("   %12s %12s" % ("Plate", "Confidence"))
                for candidate in plate['candidates']:
                    prefix = "-"
                    if candidate['matches_template']:
                        prefix = "*"
                    if count >= 1:
                        break
                    print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))
                    value = candidate['plate']
                    percentage = candidate['confidence']
                    count = count + 1


        self.bbFrame = frame



    def captureNextFrame(self):
        """                           
        capture frame and reverse RBG BGR and return opencv image                                      
        """
        mainls = []


        ret, readFrame = self.capture.read()

        if (ret == True):
            self.currentFrame = cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)
            self.faceDetection(self.currentFrame)
            self.currentFrame = self.bbFrame






    @property
    def convertplateFrame(self):
        # try:
        faceList = []
        global i
        frame = self.currentFrame
        faces = self.allfaces
        # print faces
        for (x, y, w, h) in faces:
            # print "x: ",x,"y: ",y,"w: ",w,"h: ",h
            # face = np.array([])
            face = frame[y:y + h, x:x + w]
            height, width, channel = face.shape
            bytesPerLine = 3 * width
            # print "h: ",height,"w: ",width
            # print face
            face = cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)


            img = QtGui.QImage(face, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            # print "Face1"

            img = QtGui.QPixmap.fromImage(img)
            # print "Face2"

            faceList.append(img)
            # print "Face3"

            i += 1
            print (str(i))
        # print "convertplateFrame list ",str(len(faceList))
        return faceList
        # except:
        #     return None

    def convertFrame(self):
        """     converts frame to format suitable for QtGui            """
        try:
            height, width = self.currentFrame.shape[:2]
            img = QtGui.QImage(self.currentFrame,
                               width,
                               height,
                               QtGui.QImage.Format_RGB888)
            img = QtGui.QPixmap.fromImage(img)
            self.previousFrame = self.currentFrame
            return img
        except:
            return None


class Gui(QtGui.QMainWindow):
    # flist = None

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi('guidesign.ui', self)
        #self.ipList = ['0']
        self.camerasComboBox.currentIndexChanged.connect(self.selectionchangeCameras)
        self.show()
        # self.video = Video(cv2.VideoCapture('rtsp://admin:admin123@172.16.5.19/streaming/channels/2'))
        self.video = Video(cv2.VideoCapture('path Video'))
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.play)
        self.update()



    def play(self):
        try:
            self.video.captureNextFrame()
            self.videoFrame.setPixmap(self.video.convertFrame())
            self.videoFrame.setScaledContents(True)

            ls = self.video.convertplateFrame

            # ls = self.video.convertChips()
            #global value
            #plate = str(value)
            lsLength = len(ls)
            for x in range(0, lsLength):
                itm = QListWidgetItem("Plate")
                #txt = textEdit(str(value))
                self.textEdit1.setPlainText(str(value))
                itm.setIcon(QIcon(QtGui.QPixmap(ls[x]).scaled(100, 100)))
                self.facesFDlistWidget.addItem(itm)
            if lsLength is 0:
                self.textEdit1.setPlainText("")

    

        except TypeError:
            print ("No frame OR No Camera is available!")



    @pyqtSlot()
    def on_playFDQPushButton_clicked(self):
        self.startStream()

    @pyqtSlot()
    def on_stopFDQPushButton_clicked(self):
        self.stopStream()

    @pyqtSlot()
    def on_exitFDQPushButton_clicked(self):
        sys.exit()

    @pyqtSlot()
    def on_clearFDQPushButton_clicked(self):
        self.facesFDlistWidget.clear()
        self.textEdit1.setPlainText("")


    def stopStream(self):
        self._timer.stop()

    def startStream(self):
        self._timer.start(1)


    def selectionchangeDetails(self, i):
        global algoIndex
        print ("Items in the list are :", str(i))
        if i == 0:
            algoIndex = 0
            self.detailsFDQLabel.setText("1. Face Detection uses simple HAAR features.\n\n2. Only covers 5 meters of distance, 20 degree of face pose. \n\n3. Detect faces in few illumination conditions.")
        elif i == 1:
            algoIndex = 1
            self.detailsFDQLabel.setText("1. Face Detection uses HOG features.\n\n2. Only covers 4 meters of distance, 45 degree of face pose. \n\n3. Detect faces in few illumination conditions. \n\n4. It also provides face landmarks.")
        elif i == 2:
            algoIndex = 2
            self.detailsFDQLabel.setText("1. Face Detection uses Joint Face Detection and Alignment Using Multitask Cascaded Convolutional Networks.\n\n2. Covers approximately 20 meters distance with 90 degree of face pose. \n\n3. Detect faces in different illumination conditions.")
        else:
            algoIndex = 3
            self.detailsFDQLabel.setText("1. Face Detection uses HAAR trained with more than 50,000 faces.\n\n2. Covers 20 meters distance with 50 degree of face pose. \n\n3. And works in different illumination conditions.")

    def selectionchangeCameras(self,i):
        try:
            # self.stopStream()
            self.videoFrame.setPixmap(QtGui.QPixmap('images/loads.jpg'))
            #self.video = Video(cv2.VideoCapture(self.ipList[i]))
            if i == 0:
                self.video = Video(cv2.VideoCapture('output.avi'))
            elif i == 1:
                self.video = Video(cv2.VideoCapture('rtsp://admin:admin123@172.16.4.128/streaming/channels/102'))
            elif i == 2:
                self.video = Video(cv2.VideoCapture('rtsp://admin:admin123@172.16.5.36/streaming/channels/2'))


            # self.startStream()
        except TypeError:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)

            msg.setText("Camera is not avialable!")
            msg.exec_()




def main():
    app = QtGui.QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())


import res_rc

if __name__ == '__main__':
    main()
