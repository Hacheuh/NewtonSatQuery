#STS (search type and spectra) est un programme permettant comme son nom l'indique de rechercher pour une detection donnee dans 3XMM d'acceder aux types d'objets si celui-ci est repertorie et au nombre de spectres disponibles pour la source correspondante. Le programme necessite qu'on lui donne un tableau (en fait un tableau a une colonne) en format .csv en entree. Cette colonne doit contenir les IAUNAME en format 3XMM. 
#Remarque : il est possible de modifier le code de manière a accepter des IAUNAME d'autres bases de données, cela aura par contre une incidence sur la recherche de spectre, se faisant à partir de la base de donnée 3XMM de Ledas.

import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException

r=raw_input('Quel fichier csv voulez-vous afficher ? ')
f=str(r)
f=f[:-4] #on se servira de f a la fin pour la creation du fits en lui donnant le meme nom que le csv sans le .csv
#recuperation de chaque coordonnees pour les deux formats : respectivement simbad et ledas

fichier = open(r,'rb')
fichiercsv = csv.reader(fichier, delimiter=';')
coordsim = [] #liste qui contiendra les coordonnees en format Simbad
coordled = [] #liste qui contiendra les coordonnees en format Ledas
coor=[] #liste qui contiendra les IAUNAME originaux
coord=[]
for ligne in fichiercsv:
    coordonnees = ligne[0]
    coor.append(coordonnees)
    coord.append(coordonnees)
    coordonnees = coordonnees[6:] # exemple : coordonnees = "125702.3+220152"
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

#Recherche des informations sur internet

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.stylesheet', 2)
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false') #Ce profil de Firefox permet de simplifier et d'accelerer la navigation entre les différentes pages internet.
#alternative : utiliser phamtomJS par la suite pour une execution plus rapide des recherches et effectuee sans affichage des pages
browser = webdriver.Firefox(firefox_profile=firefox_profile)

n=len(coordsim) #nombre de sources 
T=[] #liste qui contiendra les types d'objets
S=[] #liste qui contiendra le nombre de spectre disponible
p=0
for i in range(n): #boucle pour chaque coordonnees
    l=coordsim[i]
    l_2=coordled[i]
    print "Progression : " +str(i+1) +"/" +str(n) #affichage de la progression pour un suivi a partir du panneau de commande.
    
#ouverture de Simbad pour le type de source
    
    browser.get('http://simbad.u-strasbg.fr/simbad/sim-fcoo')
    m=0
    while m<10:
        try:
            elem = browser.find_element_by_name("Coord")
            elem.send_keys(l)
            query = browser.find_element_by_name("submit")
            query.send_keys(Keys.RETURN)
            obj = browser.find_element_by_css_selector("table#datatable > tbody.datatable > tr:first-child > td:nth-child(2) > a[href]") #le programme selectionne le resultat le plus proche des coordonnees dans le tableau des resultats, ce n'est pas forcement ce resultat qui est le plus précis au niveau du type.
            obj.send_keys(Keys.RETURN)
        #Gestion des erreurs pour les elements html précedent.
        except NoSuchElementException:
            m=m+1
        except ElementNotVisibleException:
            m=m+1
        else:
            m=10
            
    m=0
    while m<10:
        try:
            txt = browser.find_element_by_css_selector("html > body > div > table > tbody > tr > td > table > tbody > tr > td > font[size='+2']") #recuperation de l'element html correspondant au texte donnant le type de source.
            txt = txt.text
            txt = txt.split(' -- ') #l'element html est generalement constitué sur le modele suivant : identifiant de l'objet -- type d'objet. On separe le texte en deux chaines de caractères qu'on met ensuite dans une liste txt
            txt = txt[1] #On prend le deuxieme element de la liste pour n'avoir que  le type d'objet.
            T.append(txt)
        #Gestion des erreurs
        except NoSuchElementException:
            try :
                txt = browser.find_element_by_css_selector("html > body > div > table:nth-child(3) > tbody > tr > td > b ") #cas ou la contrepartie n'existe pas dans simbad, on recupere l'element correspondant au No Astronomical Object Found
                txt = txt.text
                txt = txt[:28]
                T.append(txt)
            except NoSuchElementException:
                m=m+1
                if m==10:
		    T.append('Null') #Pour toutes les autres erreurs on affiche null, l'utilisateur peut ainsi verifier au cas par cas les erreurs en cause. Ces erreurs non repertoriees represente une part negligeable du tableau final.
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
    
            
            txt = browser.find_elements_by_css_selector("html > body > div.detid > div.detid_tbl > div.other_det > div.other_det_list > table > tbody > tr > td:nth-child(7) ") #Recuperation de l'element correspondant a la colonne de test d'existence des spectres : Y/Y, N/N...
            s=0    
#on va comparer cet element a ce qui nous interesse, c'est a dire les cas ou il existe un spectre ou des timeseries et on place un compteur s qui augmente chaque fois que les elements sont identiques a nos comparateurs.
            for a in range(len(txt)):
                stxt = txt[a].text
                if stxt=="Y / Y":
                    s=s+1
                elif stxt=="Y / N":
                    s=s+1
                elif stxt=="N / Y":
                    s=s+1
                else:
                    s=s
            s=str(s) #on transforme s en chaine de caractere
            S.append(s)
        #Gestion des erreurs
        except NoSuchElementException:
	    try:
		nosou = browser.find_element_by_css_selector("html > body > table > tbody > tr > td > center > font[color='red']") #cas ou les coordonnees que l'on a mis ne sont pas repertoriees dans la base de donnees 3XMM de ledas, on recupere le message : No sources found. ... la suite correspondant au temps de la recherche
		stxt = nosou.text
		stxt = stxt.split(' found') #on supprime la partie donnant le temps de recherche
		stxt = stxt[0]
		S.append(stxt)
            #Gestion de toutes les autres erreurs
            except NoSuchElementException:
		m=m+1
	    	if m==10:
			S.append('Null') #meme commentaire que precedemment
	    else:
		m=10
        else: 
            m=10
	p=p+1
browser.close()
    

#reouverture du csv afin de completer la deuxieme colonne et troisieme colonne

out = open(r, "wb")
for i in range(n):
    coor[i]=coor[i]+';'+T[i]+';'+S[i] 
    out.write(coor[i]+'\n')
out.close()

#creation du fits
import numpy as np
from astropy.io import fits
import numpy as np
a1 = np.array(coord)
a2 = np.array(T)
a3 = np.array(S)
col1 = fits.Column(name='Coordonnees', format='21A', array=a1) #au format 3XMM les IAUNAME sont compose de 21 caracteres, si on utilise d'autres IAUNAME il faudra modifier le format de la colonne.
col2 = fits.Column(name='Type de sources', format='50A', array=a2) #50 caracteres utilise pour le type d'objet
col3 = fits.Column(name='Nombre de spectre', format='10A', array=a3) #on utilise 10 caracteres meme si le nombre de spectre ne peut depasser 2 chiffre afin de traiter les elements d'erreur
cols = fits.ColDefs([col1, col2, col3])
tbhdu = fits.new_table(cols)
tbhdu.writeto(f+'.fits')

#H. GASCUEL/F. TONNEAU/L. LE LONQUER