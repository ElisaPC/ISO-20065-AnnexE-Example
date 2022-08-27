import spectra_i
import _formula
import _criteria
import _critical_band
import numpy as np
import _uncertainty

EXAMPLE_SPECTRUM_FREQS=[96.9, 99.6, 102.3, 105.0, 107.7, 110.4, 113.0, 115.7, 118.4, 121.1, 
123.8, 126.5, 129.2, 131.9, 134.6, 137.3, 140.0, 142.7, 145.3, 148.0, 150.7, 153.4, 156.1, 158.8, 
161.5, 164.2, 166.9, 169.6, 172.3, 175.0, 177.6, 180.3, 183.0, 185.7, 188.4, 191.1, 193.8, 196.5]

EXAMPLE_SPECTRUM_Li=[49.40, 50.68, 50.09, 53.37, 44.47, 50.91, 51.41, 59.40, 64.54, 57.57,
51.02, 50.76, 59.93, 62.94, 58.49, 65.87, 62.66, 50.25, 51.32, 52.30, 52.58, 53.15, 67.04, 67.27, 
57.40, 57.17, 52.56, 51.39, 52.49, 47.68, 51.26, 49.03, 61.42, 59.52, 48.43, 50.84, 48.20, 55.95]

delta_f=2.7 	#line spacing
delta_fe=1.5 	#effective bandwith (Hanning window)
list_deltaLm=[] #list of final audibilities, the greatest will be the dec. aud.
dict_lines_assigned={} #this dictionary is used to see what lines are assigned to each tone in Lt, so they are not added twice in Ltm
#keys ft, values list of Lis assigned to get ft's Lt
dict_Lt={} #dictionary keys ft; values Lt
dict_LS={}	#dictionary keys ft; values LS
dict_aud={} #dictionary keys ft; values delta_L (audibilities)
dict_Li_LS={} #dictionary with the final list of Lis used to determine ft's LS after LS iteration
list_ft=[] #list of audible tones
list_ft_aud_not_distinct=[] ##list of audible tones that do not meet the distinctness conditions

#First we find the index in which there is maxima on the spectrum, i.e. a Li value which is higher that 
#the previous and the next one
list_index_max=[]
for i in range(0,len(EXAMPLE_SPECTRUM_Li)-1):
	if EXAMPLE_SPECTRUM_Li[i-1] < EXAMPLE_SPECTRUM_Li[i]> EXAMPLE_SPECTRUM_Li[i+1]:
		list_index_max.append(i)

print("List of index with spectrum maxima:",list_index_max)

#Study of each maximum. Calculation of the parameters for each maximum and study of the 
#fulfilment of conditions to consider said maximum as an audible tone.
for j in range(0, len(list_index_max)):
	ft=EXAMPLE_SPECTRUM_FREQS[list_index_max[j]]
	print("\n")
	print("************************************************************************************************************")
	print("ft=",ft)
	aud_i, dict_lines_assigned, list_ft_aud_not_distinct, dict_LS, dict_Lt, dict_Li_LS=spectra_i._spectra_i_calculations(EXAMPLE_SPECTRUM_Li, EXAMPLE_SPECTRUM_FREQS,delta_f, delta_fe, ft, list_index_max[j], dict_lines_assigned, list_ft_aud_not_distinct, dict_LS, dict_Lt, dict_Li_LS)
	if aud_i>0: #tones which audibility is to be studied
		dict_aud[ft]=round(aud_i,2)
		list_ft.append(ft)

print("\n")
print ("Dictionary of spectral lines that would be assigned for LTm in each tone:", dict_lines_assigned)
print("Dictionary of audibilities", dict_aud)
print("List of audible tones that do not met distinctness criteria:", list_ft_aud_not_distinct)
print("List of the tones with audibilities>0 ", list_ft)

#check the dictionary for the tones that are distinct but not audible, and erase them from it
dict_lines_assigned_aux=dict_lines_assigned.copy()
#Erase tones, that are finally not present, from the dictionary (distinct but not audible/present)
for keys in dict_lines_assigned_aux:
	if(keys in list_ft)==False:
		del dict_lines_assigned[keys] 

#Erase from the list of audible tones those that are not supposed to be studied even though they are audible 
#I.e. those which do not meet distinctness criteria
for z in range(0, len(list_ft_aud_not_distinct)):
	f=list_ft_aud_not_distinct[z]
	if f in list_ft:
		list_ft.remove(f) 
	if f in dict_aud:
		del dict_aud[f]

print("\n\n*********DECISIVE AUDIBILITY**********")
print("Confirmed audible tones (aud>0 + met criteria):", list_ft)

#Now we check that the spectral lines are not used for Ltm more than once, and if so the least pronounced tone is dismissed
dict_lines_assigned, list_ft, dict_aud=_criteria._single_addition_sp_lines(dict_lines_assigned, dict_aud, list_ft, EXAMPLE_SPECTRUM_FREQS, EXAMPLE_SPECTRUM_Li)
print("Tones under study after single addition criteria", list_ft)
print("UPDATED DICTIONARY of spectral lines for Ltm after the single additon criteria", dict_lines_assigned)

#If there are more than one tone in a CB, check the ft2-t1>fd criteria to see if the tones must be evaluated separetely
list_ft, dict_aud=_criteria.aud_tones_within_critical_band(list_ft, dict_aud, EXAMPLE_SPECTRUM_FREQS)
print("Tones under study after the fd criteria (FINAL LIST OF TONES FOR DEC. AUD.):", list_ft)

#Calculate delta_L again for (each) the tone ftm
for n in range(0,len(list_ft)):
	list_LT=[] #empty this list for each tone
	ftm=list_ft[n]
	ftm_index=EXAMPLE_SPECTRUM_FREQS.index(ftm)
	Li_ftm=EXAMPLE_SPECTRUM_Li[ftm_index]
	LSm=dict_LS.get(ftm)
	print("\n-------------------------------------------------------------------------------------------------------------------")
	print("Study of the DECISIVE AUD. for tone ", ftm, "with Li=", Li_ftm, "and its calculated LS=", round(LSm,2))
	#critical band 
	delta_fm,f1,f2=_critical_band._critical_band(ftm, EXAMPLE_SPECTRUM_FREQS)
	#print("f1=", f1)
	#print("f2=", f2)
	#Obtain the applicable Lts, to calculate Ltm of the tone under study, from the dictionary of Lts
	for f in dict_lines_assigned:
		if f>=f1 and f<=f2:
			Lt=dict_Lt.get(f)
			list_LT.append(round(Lt,2))
	print("For the tone", ftm, ", the list of applicable Lts for Ltm calculation is: ", list_LT)

	#Sum of the tone level LT of all the audible tones within ftm's critical band
	Sum=0
	for z in range(0,len(list_LT)):
		Sum=Sum+(np.power(10,0.1*list_LT[z]))
	LTm=10*np.log10(Sum)
	print("Summed tone level of the band LTm:", round(LTm,2))
	LGm=_formula._critical_band_level(LSm,delta_f,delta_fm)
	avm=_formula._masking_index(ftm)
	delta_Lm=_formula.audibility(LTm, LGm, avm)
	U_ftm=_uncertainty._uncertainty(dict_Li_LS[ftm], list_LT, delta_fm, delta_f)
	list_deltaLm.append(delta_Lm)
	print("Tone:", ftm, "-> For a masking index of av=",round(avm,2), "and a critical band level LGm=",round(LGm,2), "the DECISIVE audibility is", round(delta_Lm,2))	
	print("Final result: ", round(delta_Lm,2), "U=", round(U_ftm,2))

#Get the decisive audibility of the spectra, which is the highest delta_L obtained for the audible tones
greatest_deltaLm=0
for c in range(0,len(list_deltaLm)):
	if list_deltaLm[c]>greatest_deltaLm:
		greatest_deltaLm=list_deltaLm[c]
		tone_decisive_aud=list_ft[c]

print("\nDECISIVE AUDIBILITY OF THE SPECTRA")
print("The greatest decisive audibility is", round(greatest_deltaLm,2), "for the tone ftm=", tone_decisive_aud)


#Coge el tono 131.9 como tono de mayor audibilidad ya que LS da mas alto porque faltan Lis en el cálculo. ftm debería ser 137.3.
#Además los tonos que tiene en cuenta son 118.4 131.9 y 137.3 