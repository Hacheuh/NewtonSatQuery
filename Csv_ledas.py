
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException

r=raw_input('Quel fichier csv voulez-vous afficher ? ')


#recuperation de chaque coordonnees pour les deux formats : respectivement simbad et ledas

fichier = open(r,'rU')
fichiercsv = csv.reader(fichier, delimiter=';')
coordsim = []
coordled = []
coor=[]
coord=[]
for ligne in fichiercsv:
#    ligne[0]=ligne[0][:]
    
    coordonnees = ligne[0] # mettre a la place la coordonnee voulu
    coor.append(coordonnees)
    coord.append(coordonnees)
    coordonnees = coordonnees[6:] # coordonnees = "125702.3+220152"
    charCoordonnees = list(coordonnees) # charCoordonnees =[1,2,5,7,0,2,.,3,+,2,2,0,1,5,2]
    charCoordonnees.insert(13,' ') # charCoordonnees =[1,2,5,7,0,2,.,3,+,2,2,0,1, ,5,2]
    charCoordonnees.insert(11,' ') # charCoordonnees =[1,2,5,7,0,2,.,3,+,2,2, ,0,1, ,5,2]
    charCoordonnees.insert(8,' ') # charCoordonnees =[1,2,5,7,0,2,.,3, ,+,2,2, ,0,1, ,5,2]
    charCoordonnees.insert(4,' ') # charCoordonnees =[1,2,5,7, ,0,2,.,3, ,+,2,2, ,0,1, ,5,2]
    charCoordonnees.insert(2,' ') # charCoordonnees =[1,2, ,5,7, ,0,2,.,3, ,+,2,2, ,0,1, ,5,2]
    coordonnees = ''.join(charCoordonnees) # coordonnees = "12 57 02.3 +22 01 52"
    coordsim.append(coordonnees)
    charCoordonnees = list(coordonnees) # charCoordonnees = [1,2, ,5,7, ,0,2,.,3, ,+,2,2, ,0,1, ,5,2]
    charCoordonnees.insert(10,',') # charCoordonnees = [1,2, ,5,7, ,0,2,.,3,',', ,+,2,2, ,0,1, ,5,2]
    coordonnees = ''.join(charCoordonnees) # coordonnees = "12 57 02.3, +22 01 52"
    coordled.append(coordonnees)

#
#print coordsim
#print coordled

#Recherche des informations sur internet

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.stylesheet', 2)
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
browser = webdriver.Firefox(firefox_profile=firefox_profile)#utiliser phamtom js par la suite

n=len(coordsim) #nombre de sources 
ERROR = []
T=[]
S=[]
p=0
for i in range(n): #boucle pour chaque coordonnees
    l=coordsim[i]
    l_2=coordled[i]
    print "Progression : " +str(i+1) +"/" +str(n)
    
#ouverture de Simbad pour le type de source
    
    browser.get('http://simbad.u-strasbg.fr/simbad/sim-fcoo')
    m=0
    while m<10:
        try:
            elem = browser.find_element_by_name("Coord")
            elem.send_keys(l)
            query = browser.find_element_by_name("submit")
            query.send_keys(Keys.RETURN)
            obj = browser.find_element_by_css_selector("table#datatable > tbody.datatable > tr:first-child > td:nth-child(2) > a[href]")
            obj.send_keys(Keys.RETURN)
        except NoSuchElementException:
            m=m+1
        except ElementNotVisibleException:
            m=m+1
        else:
            m=10
            
    m=0
    while m<10:
        try:
            txt = browser.find_element_by_css_selector("html > body > div > table > tbody > tr > td > table > tbody > tr > td > font[size='+2']")
            txt = txt.text
            txt = txt.split(' -- ')
            txt = txt[1]
            T.append(txt)
        except NoSuchElementException:
            try :
                txt = browser.find_element_by_css_selector("html > body > div > table:nth-child(3) > tbody > tr > td > b ")
                txt = txt.text
                txt = txt[:28]
                T.append(txt)
            except NoSuchElementException:
                m=m+1
                if m==10:
		    T.append('Null')
            else:
                m=10
        else:
            m=10
    
    
#Ouverture LEDAS pour l'existence d'un spectre
    browser.get('http://ledas-www.star.le.ac.uk/arnie5/arnie5.php?action=basic&catname=3xmm')
#recherche par coordonnees
    m=0
    while m<10:
        try:
            elem = browser.find_element_by_name("coordinates")
            elem.send_keys(l_2)
            query = browser.find_element_by_name("process")
            query.send_keys(Keys.RETURN)
#ouverture du summary
            summary = browser.find_element_by_class_name("vot_button")
            browser.execute_script("document.querySelector('div#Layer2 table.resultstable tbody tr td a.vot_button').setAttribute('target', '')");
            summary.send_keys(Keys.RETURN)
    #releve du nombre de spectre/timeseries
    
            
            txt = browser.find_elements_by_css_selector("html > body > div.detid > div.detid_tbl > div.other_det > div.other_det_list > table > tbody > tr > td:nth-child(7) ")
            s=0    

            for a in range(len(txt)):
                stxt = txt[a].text
#                print stxt
                if stxt=="Y / Y":
                    s=s+1
                elif stxt=="Y / N":
                    s=s+1
                elif stxt=="N / Y":
                    s=s+1
                else:
                    s=s

            s=str(s)
#            print s
            S.append(s)
            #print s
            
        except NoSuchElementException:
	    try:
		nosou = browser.find_element_by_css_selector("html > body > table > tbody > tr > td > center > font[color='red']")
		stxt = nosou.text
		stxt = stxt.split(' found')
		stxt = stxt[0]
		S.append(stxt)
            except NoSuchElementException:
		m=m+1
	    	if m==10:
			S.append('Null')
	    else:
		m=10
        else: 
            m=10
browser.close()
#print S
    

#reouverture du csv afin de completer la deuxieme colonne et troisieme colonne

out = open(r, "wb")
for i in range(n):
    coor[i]=coor[i]+';'+T[i]+';'+S[i] 
    out.write(coor[i]+'\n')

out.close()


import numpy as np
from astropy.io import fits
import numpy as np
a1 = np.array(coord)#remplacer par coordsim
a2 = np.array(T)#remplacer par T
a3 = np.array(S)#remplacer par S
a4=np.array(coordled)
col1 = fits.Column(name='Coordonnees', format='21A', array=a1)
col2 = fits.Column(name='Type de sources', format='50A', array=a2)
col3 = fits.Column(name='Nombre de spectre', format='10A', array=a3)
col4 = fits.Column(name='Ledas', format='30A', array=a4)
cols = fits.ColDefs([col1, col2, col3,col4])
tbhdu = fits.new_table(cols)
tbhdu.writeto(r+".fits")

