import threading
import cv2


class Navigator(threading.Thread):
    FRAME_HEIGHT = 240
    FRAME_WIDTH = 320
    FPS = 24
    SPLIT_NUM = 12
    CENTER = 160
    ANGLE = 20
    AREA_MIN1 = 1000   # Konturen kleiner als ein strich verwerfen
    AREA_MAX1 = 10000  # Konturen zusammengestzt mittellinie und querlinie, verwerfen
    AREA_MIN2 = 23000  # sehr grosse Konturen (Start/Ziel) auswerten

    DEBUG = True

    # Constructor
    def __init__(self, webcamPort):
        threading.Thread.__init__(self)
        self.port = webcamPort
        self.distance = 0

    # set frame size and fps
    def setCam(self):
        cap = cv2.VideoCapture(self.port)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        cap.set(cv2.cv.CV_CAP_PROP_FPS, self.FPS)
        return cap

    def rotateImage(self, image, angle):
        # row,col = image.shape
        center = (120, 160)
        # center=tuple(np.array([row,col])/2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        new_image = cv2.warpAffine(image, rot_mat, (320, 240))
        return new_image

    def getDistance(self):
        return self.distance

    def setDistance(self, mat):
        self.distance = (mat[self.SPLIT_NUM / 2][0]) - self.CENTER

    # split frame
    def split(self, frame):
        copy = frame.copy()
        partset = []
        x1 = 0
        x2 = self.FRAME_WIDTH
        for i in range(self.SPLIT_NUM):
            y1 = (self.FRAME_HEIGHT / self.SPLIT_NUM) * i
            y2 = (self.FRAME_HEIGHT / self.SPLIT_NUM) * (i + 1)
            part = copy[y1:y2, x1:x2]
            partset.append(part)
        return partset

    # find contours of splited frame and calc there rightmost points
    def findPoints(self, splitset):
        partcnt = []
        for i in range(self.SPLIT_NUM):
            contours, h = cv2.findContours(splitset[i], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            points = []
            for cnt in contours:
                rm = tuple(cnt[cnt[:, :, 0].argmax()][0])
                rightmost = (int(rm[0]), int(rm[1]) + self.FRAME_HEIGHT / self.SPLIT_NUM * i)
                points.append(rightmost)
            partcnt.append(points)
        return partcnt

    # find contours
    def findContours(self, frame):
        copy = frame.copy()
        cnt = []
        contours, h = cv2.findContours(copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if self.AREA_MIN1 < area < self.AREA_MAX1 or area > self.AREA_MIN2:
                (x, y), (MA, ma), angle = cv2.fitEllipse(c)
                if 0 < angle < self.ANGLE or 180 > angle > 180 - self.ANGLE:
                    cnt.append(c)
        return cnt

    # check if points in contour
    def checkPoints(self, contours, points):
        i = 0
        checkedPoints = []
        for pset in points:
            pointset = []
            for point in pset:
                for cnt in contours:
                    test = cv2.pointPolygonTest(cnt, point, False)
                    if test != -1:
                        pointset.append(point)
            if len(pointset) > 0:
                checkedPoints.append(max(pointset))
            else:
                if len(checkedPoints) > 0:
                    lastpoint = checkedPoints[i-1]
                    newpoint = (lastpoint[0], lastpoint[1]+self.FRAME_HEIGHT/self.SPLIT_NUM)
                    checkedPoints.append(newpoint)
                else:
                    default = (self.CENTER, int(self.FRAME_HEIGHT/self.SPLIT_NUM*(i+0.5)))
                    checkedPoints.append(default)
            i += 1
        return checkedPoints

    #draw contour
    def drawContours(self, contours, target):
        if len(contours) > 0:
            cv2.drawContours(target, contours, -1, (0, 255, 0), 2)

    # start cam
    def run(self):
        cap = self.setCam()

        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Otsu's thresholding after Gaussian filtering
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            ret1, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # calculate points
            contours = self.findContours(th)
            split = self.split(th)
            points = self.findPoints(split)
            chp = self.checkPoints(contours, points)
            self.setDistance(chp)

            # Display stuff to Debug
            if self.DEBUG:
                text = str(self.getDistance())
                cv2.putText(frame, text, (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

                self.drawContours(contours, frame)
                # draw points
                for p in chp:
                    cv2.circle(frame, p, 1, (255, 0, 0), 5)
                # draw line
                for i in range(1, len(chp)):
                    cv2.line(frame, chp[i - 1], chp[i], (0, 0, 255), 2)

                cv2.imshow('original', frame)
                cv2.imshow('OTSU', th)
                cv2.moveWindow('OTSU', 340, 0)

            if cv2.waitKey(50) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
