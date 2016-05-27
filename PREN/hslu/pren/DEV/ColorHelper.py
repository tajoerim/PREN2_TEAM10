import cv2
import numpy as np
    
class helper:

    # Callbackmethode für Schieberegler
    def nothing(*arg):
        pass

help = helper()

# Schieberegler für HSV-Grenzwerte
cv2.namedWindow('frame')
cv2.createTrackbar('H1', 'frame', 106, 255, help.nothing)
cv2.createTrackbar('S1', 'frame', 6, 255, help.nothing)
cv2.createTrackbar('V1', 'frame', 34, 255, help.nothing)

cv2.createTrackbar('H2', 'frame', 164, 255, help.nothing)
cv2.createTrackbar('S2', 'frame', 255, 255, help.nothing)
cv2.createTrackbar('V2', 'frame', 255, 255, help.nothing)

# Schieberegler für Bildauswahl (1.jpg - 15.jpg)
cv2.createTrackbar('IMG', 'frame', 0, 18, help.nothing)


while(True):

    # Werte der Schieberegler lesen
    h1 = cv2.getTrackbarPos('H1', 'frame')
    s1 = cv2.getTrackbarPos('S1', 'frame')
    v1 = cv2.getTrackbarPos('V1', 'frame')
    
    h2 = cv2.getTrackbarPos('H2', 'frame')
    s2 = cv2.getTrackbarPos('S2', 'frame')
    v2 = cv2.getTrackbarPos('V2', 'frame')

    img = cv2.getTrackbarPos('IMG', 'frame')

    # Bild laden
    frame = cv2.imread('C:\\Users\\Christoph\\Pictures\\Container\\' + str(img) + '.jpg')
    
    # Bild in HSV konvertieren
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
    # Bildmaskierung nach HSV-Grenzwerten
    both = cv2.inRange(hsv,np.array((h1,s1,v1)),np.array((h2,s2,v2)))
    erode = cv2.erode(both,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)

    # Konturen der Maskierung auslesen
    contours,hierarchy = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    # Durch alle Konturen iterieren und nur die groesste im Range erfassen
    maxX = maxY = maxW = maxH = 0
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
                
        if ((w*h) > (maxW*maxH)):
            maxX = x
            maxY = y
            maxH = h
            maxW = w
                
    # Grösste Kontur einrahmen
    cv2.rectangle(frame, (maxX,maxY), (maxX+maxW,maxY+maxH), (0,0,255), thickness=2, lineType=8, shift=0)

    # Alle konturen zeichnen
    cv2.drawContours(frame, contours, -1, (255,0,0), 1)
            
    # Ergebnis darstellen
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break