import numpy as np
import csv
from astropy.io import fits
import numpy as np
coord=[]
T=[]
S=[]
fichier = open('VarEtSum2.csv','rb')
fichiercsv = csv.reader(fichier, delimiter=';')
for ligne in fichiercsv:
	coord.append(ligne[0])
	T.append(ligne[1])
	S.append(ligne[2])
a1 = np.array(coord)#remplacer par coordsim
a2 = np.array(T)#remplacer par T
a3 = np.array(S)#remplacer par S
col1 = fits.Column(name='Coordonnees', format='22A', array=a1)
col2 = fits.Column(name='Type de sources', format='50A', array=a2)
col3 = fits.Column(name='Nombre de spectre', format='E', array=a3)
cols = fits.ColDefs([col1, col2, col3])
tbhdu = fits.new_table(cols)
tbhdu.writeto('VarEtSum2.fits')
