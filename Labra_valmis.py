# -*- coding: cp1252 -*-
"""
Pohja, jonka päälle konenäkökameralabran koodi voidaan kirjoittaa.
Skripti lukee silmukassa kuvaa kameralta ja näyttää kuvan näytöllä.
Kuvaus ja kuvien näyttäminen (sekä opiskelijan skrptiin lisäämä 
toiminta) jatkuu, kunnes käyttäjä painaa näppäintä 'q'.
"""

import cv2
from pypylon import pylon
import numpy as np
# Luodaan kameraolio ja avataan se
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# Säädetään valotusaikaa (MUUTA TARVITTAESSA)
camera.ExposureTimeRaw.SetValue(200)  # 200 x 100 us = 20 ms 

# Tarkistetaan kuvan koko
new_width = camera.Width.GetValue() - camera.Width.GetInc()
if new_width >= camera.Width.GetMin():
    camera.Width.SetValue(new_width)

# Aloitetaan kuvanotto
camera.StartGrabbing()

# Niin kauan kuin kamera ottaa kuvia, luetaan ne yksi kerrallaan
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Luetaan kuvadata, pienennetään sitä, jotta se sopii näytölle,
        # ja näytetään se
        img = grabResult.Array
        preview_img = cv2.resize(img, None, fx=0.5, fy=0.5)
        cv2.imshow("kuva", preview_img)
        kuva= img
        #Pienennetään kuvaa
        kuva = cv2.resize(kuva, dsize=None, fx=0.5, fy=0.5)

        # Muutetaan harmaa sävy kuva bgr kuvaksi
        kuva_bgr = cv2.cvtColor(kuva, cv2.COLOR_GRAY2BGR)

        # Pehmennetään kuva
        #kuva = cv2.GaussianBlur(kuva, (3, 3),sigmaX=1, sigmaY=1)

        # Kynnystetään kuva otsulla
        arvo, mvkuva = cv2.threshold(kuva, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        #cv2.imshow("aariviivat kuvalle mvkuva", mvkuva)
        elementti = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        #mvkuva = cv2.morphologyEx(mvkuva, cv2.MORPH_CLOSE, elementti)
        #cv2.imshow("aariviivat kuvalleclose1", mvkuva)
        mvkuva = cv2.dilate(mvkuva, elementti)
        mvkuva = cv2.morphologyEx(mvkuva, cv2.MORPH_CLOSE, elementti)
        #cv2.imshow("aariviivat kuvalle dilateclose", mvkuva)
        mvkuva = cv2.erode(mvkuva, elementti)
        #cv2.imshow("aariviivat kuvalle erode", mvkuva)
        #mvkuva = cv2.morphologyEx(mvkuva, cv2.MORPH_CLOSE, elementti)
        #cv2.imshow("aariviivat kuvalleclose2", mvkuva)
        #cv2.waitKey(0)
        # 
        #maara, labelit, stats, painopisteet=cv2.connectedComponentsWithStats(mvkuva)

        # Etsitään ääriviivat, otetaan hierarkkia mukaan
        aariviivat, hierarkki = cv2.findContours(mvkuva, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Alustetaan objektien laskentaa varten muutujat
        mutterit = 0
        prikat = 0
        ruuvit = 0
        #sisa = 0
        # 53 pikseliä vastaa 10mm
        suhde = (53 / 10)
        # Loopataan ääriviivat ja piirretään sekä lasketaan ruuvit, muuterit ja prikat
        for i in range (0, len(aariviivat)):
            # Jälkimmäinen arkumentti tarkistaa onko sulkeva vai ei. True etsii sulkevan
            peri = cv2.arcLength(aariviivat[i],True)
            # Etsitään viivojen pituudet 5% heitolla
            approx = cv2.approxPolyDP(aariviivat[i], 0.05 * peri, True)
            # Haetaan ääriviivojen minimi alueet neliö
            rect = cv2.minAreaRect(aariviivat[i])
            # Laitetaan miniialueiden koordinaatit laatikkoon ja muutetaan kokonaisluvuiksi
            box = cv2.boxPoints(rect)
            box = np.int0(box) # boxin sisällä on neljä riviä ja 2 saraketta per rivi. eka kuvan vas ala,
            # sitten vas ylä, sitten oikea ylä ja viimeinen oikea ala koordinaatit. [y, x]
            
            rect = cv2.minEnclosingCircle(aariviivat[i])
            (x, y), r = rect
            #print(len(approx))

            
            #print("tulossa hierarkki0",hierarkki[0][i][0]
            #print("tulossa hierarkki1",hierarkki[0][i][1])
            #print("tulossa hierarkki2",hierarkki[0][i][2])
            #print("tulossa hierarkki3",hierarkki[0][i][3])
            #print("tulossa len", len(approx))
            #print("tulossa ala", ala)

            # Tällä saa piirrettyä sisähalkaisijat
            #if hierarkki[0][i][0] == -1 and hierarkki[0][i][1] == -1 and hierarkki[0][i][2] == -1:  
            #    sisa = sisa + 1
                #cv2.putText(kuva_bgr,f"sis halk {int(r)} mm", (int(x), int(y) - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)
            #    cv2.circle(kuva_bgr, (int(x), int(y)), int(r), (0, 255, 0), 2)

            # Vertaillaan if lauseilla mikä toteuttaa yhtälön ja piirtää viivat sekä laskee oikeat objektit
            if len(approx) == 6 and hierarkki[0][i][3] == -1: #ok
                mutterit = mutterit +1
                cv2.drawContours(kuva_bgr,[aariviivat[i]],0,(0,255,0),2)
                mutterin_paikka = hierarkki[0][i][2]
                mutterin_koko = cv2.minEnclosingCircle(aariviivat[mutterin_paikka])
                (mutterin_x, mutterin_y), mutterin_r = mutterin_koko
                cv2.putText(kuva_bgr,f"sis halk {int((mutterin_r * 2) / suhde)} mm", (int(mutterin_x), int(mutterin_y) - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)
                #cv2.circle(kuva_bgr, (int(mutterin_x), int(mutterin_y)), int(mutterin_r), (0, 255, 0), 2)
                
                
                
            elif len(approx) == 4  and hierarkki[0][i][3] == -1 and hierarkki[0][i][2] > 2\
                or hierarkki[0][i][1] == -1 and hierarkki[0][i][3] == -1\
                or len(approx) == 5  and hierarkki[0][i][3] == -1 and hierarkki[0][i][2] > 2:
                prikat = prikat + 1
                cv2.drawContours(kuva_bgr,[aariviivat[i]],0,(255,0,0),2)
                prikan_paikka = hierarkki[0][i][2]
                prikan_koko = cv2.minEnclosingCircle(aariviivat[prikan_paikka])
                (prikan_x, prikan_y), prikan_r = prikan_koko
                cv2.putText(kuva_bgr,f"sis halk {int((prikan_r*2) / suhde)} mm", (int(prikan_x), int(prikan_y) - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
                
                
                
            elif hierarkki[0][i][3] == -1 and hierarkki[0][i][2] == -1 and len(approx) == 3\
                or  hierarkki[0][i][3] == -1 and hierarkki[0][i][2] == -1 and len(approx) == 4\
                or  hierarkki[0][i][3] == -1 and hierarkki[0][i][2] >= 2 and len(approx) == 3:
                ruuvit = ruuvit + 1
                cv2.drawContours(kuva_bgr,[aariviivat[i]],0,(0,0,255),2)
                #print("ruuvi", r)
                #cv2.circle(kuva_bgr, (int(x), int(y)), int(r), (0, 0, 255), 2)
                cv2.putText(kuva_bgr,f"Pituus {int(((r) * 2) / suhde)} mm", (int(x), int(y) - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                # Jos käyttäjä painaa näppäintä 'q', kuvaus loppuu
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cv2.putText(kuva_bgr,f"Prikkoja on {prikat}", (0, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
    cv2.putText(kuva_bgr,f"Muttereita on {mutterit}", (0, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)
    cv2.putText(kuva_bgr,f"Ruuveja on {ruuvit}", (0, 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1) 
    cv2.imshow("Kuva",kuva_bgr)                  
    grabResult.Release()
camera.Close()
