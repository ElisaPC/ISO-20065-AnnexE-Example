from collections import Counter
import _critical_band
import numpy as np
import operator

#Function that dtermines if the number of spectral lines over and below ft is at least 5. LS second iteration criteria
#Param
#	Inputs:
#			listIndex - list of index corresponding to the spectral lines that fulfill the LS_ini+6 criteria 
#			Li_ft_index - index of ft
#	Output:
#			OK - boolean that is set to False if the num_lines over or below ft is less than 5, otherwise is set to True
def _iteration_criteria_LS(listIndex, Li_ft_index):
	nu=0 #num of lines below ft
	no=0 #num of lines over de ft
	for q in range(0, len(listIndex)):
		if listIndex[q]<Li_ft_index:
			nu=nu+1
		if listIndex[q]>Li_ft_index:
			no=no+1
	if no<5 or nu<5:
		OK=False
		print("The number of lines contributing to LS above or below the line under investigation is less than 5")
		print("\n")
	else :
		OK=True
	print("nu=",nu, "no=",no)
	return OK


#Function that during the iteration for LS' calculation tests if the new a energy mean value is 
#equal within a tolerance of ±0,005 dB to that of the previous iteration step
#Param: 
#	Inputs: list_Ls: list that contains the values of LS in every iteration step
#	Output: stop - boolean that is set to True if the iteration must be stopped because the criteria is met
def _iteration_criteria_2(list_LS):
	for j in range(1,len(list_LS)):
		if abs(list_LS[j]-list_LS[j-1])<0.005:
			print("Two consecutive LS have the same value or a difference below 0.005")
			stop=True
		else: 
			stop=False
	return stop


#The level frequency lines that can be defined as tones, ft, inside a critical band: a tone may only be present if 
#the level of the spectral line considered is at least 6 dB greater than the corresponding mean narrow-band level LS.
#This function tests if the tone satisfies this criteria
#	Inputs: LS - calculated mean narrow band level for ft
#			Li - ft's tone level
#	Output: tone_criteria: boolean set to False if the criteria is not fulfilled 
def tone_criteria(LS, Li):
	if Li>LS+6:
		tone_criteria=True
	else: tone_criteria=False
	return tone_criteria


#Function that determines if the tone meets the distinctness criteria
#Param: 
#	Inputs: ft - tone frequency
#			Lu - tone level of the frequency of the first spectral line below the tone ft
#			Lo - tone level of the frequency of the first spectral line over the tone ft
#			fu - tone level of the frequency of the first spectral line below the tone ft
#			fo tone level of the frequency of the first spectral line over the tone ft
#			LT_max - maximum narrow-band level (Li) of the tone	
#			Tone_BW - tone bandwidth: sum of the bandwidths of the spectral lines contributing to the tone
#	Output: ok - boolean that is set to False when the tone doesn´t meet the distinctness criteria, and to True if it does
def _distinctness_criteria(ft, Lu,Lo,fu,fo, LT_max, Tone_BW):
	delta_fR=26*(1+0.001*ft)
	delta_Lu=(ft/2)*((LT_max-Lu)/(ft-fu))
	delta_Lo=(ft)*((LT_max-Lo)/(fo-ft))
	print("delta_Lu and delta_Lo must be higher or equal to 24 dB. They are: (", round(delta_Lu,2),",", round(delta_Lo,2), ")")
	print("The tone bandwidth must be lower than the max: ", round(delta_fR,2))
	if (Tone_BW<delta_fR) and (delta_Lu>=24) and (delta_Lo>=24):
		ok=True
	else: ok=False
	return ok


#"It is possible for the energy of individual spectral lines to be assigned to a number of neighbouring tones
#at the same time. Upon addition of the tone levels of neighbouring tones, the energy of these individual
#spectral lines may not be summed more than once."
#This function ensures that when summing the tone levels of neighbouring tones, the energy of these individual spectral lines 
#are not summed more than once. Regarding the calculation of Ltm.
#Param: 
#	Inputs: dict_lines_assigned - This dictionary is used to see what lines are assigned to each tone in Lt, so they are 
#			not added twice in Ltm. Keys: ft, values: list of Lis assigned to get ft's Lt
#			dict_aud - dictionary keys ft; values delta_L (audibilities)
#			list_ft_audib - list of audible tonos in the spectra (yet to be assessed whether they meet all the criteria)
#			list_freqs - list of all the frequencies in the spectra, neccesary to get the index of the tones that
#						use the same level(s) to obtain Lt
#			list_Li - list of all the levels of respective f in the spectra, once obtained the index, the level of the tones
#					is determined with this list. If one is to be erased it would be the least pronounced tone
#	Output: dict_lines_assigned - updated dictionary, without the deleted tones (keys) if any
#			list_ft_audib_aux - updated list of audible tones, without the deleted tones (keys) if any
#			dict_aud - updated dictionary of audibilities, without the deleted tones (keys) if any
def _single_addition_sp_lines(dict_lines_assigned, dict_aud, list_ft_audib, list_freqs, list_Li):
	list_aux1=[]
	list_aux2=[]
	list_ft_audib_aux=list_ft_audib
	for m in range (0, len(list_ft_audib)-1):
		key1=list_ft_audib[m]
		key2=list_ft_audib[m+1]
		#Get list of Lis used to get each of teh tones Lt
		list_aux1=dict_lines_assigned.get(key1)
		list_aux2=dict_lines_assigned.get(key2)
		index_tone1=list_freqs.index(key1)
		index_tone2=list_freqs.index(key2)
		Li_tone1=list_Li[index_tone1]
		Li_tone2=list_Li[index_tone2]
		#Counter is used to Compare if unordered lists have the same elements
		#(what if the lists don't have the exact same Lis? how likeky is this?)
		if(Counter(list_aux1)==Counter(list_aux2))==True:
			#In case they have the same lines, keep only the most pronounced tone
			if(Li_tone1>Li_tone2):
				list_ft_audib_aux.remove(list_ft_audib[m+1])
				del dict_lines_assigned[key2]
				del dict_aud[key2]
				print("Deleted f=", key2, "because of the single addition criteria")
			else : #(list_Li[list_index_audib[m]]<list_Li[list_index_audib[m]]):
				list_ft_audib_aux.remove(list_ft_audib[m])
				del dict_lines_assigned[key1]
				del dict_aud[key1]
				print("Deleted f=", key1, "because of the single addition criteria")
	return dict_lines_assigned, list_ft_audib_aux, dict_aud


#"If exactly 2 tones with tone frequencies, fT1 and fT2, appear in one critical band, then they are evaluated
#separately if both tone frequencies lie below 1 000 Hz and the frequency difference, fD."
#This function is used to check whether two tones in the same CB should be evaluated separately, according to the standard.
#Param: 
#	Inputs: list_ft_audib - list of audible tonos in the spectra (after checking all criteria)
#			dict_aud - dictionary keys ft; values delta_L (audibilities, after checking all criteria)
#			list_freqs - list of all the frequencies in the spectra, necessary to determine the CB, f1 and f2,
#						and which tones lie within a CB
#	Output: list_ft_audib - updated list of audible tones, if two tones can´t be evaluated separately the lowest of those
#							is erased from the list
#			dict_aud_aux - updated dictionary of audibilities
def aud_tones_within_critical_band(list_ft_audib, dict_aud, list_freqs):
	dict_aud_aux=dict_aud.copy()
	for f in dict_aud:
		dict_CB={}
		delta_fc,f1,f2=_critical_band._critical_band(f, list_freqs)
		#check which of the possible tones to be evaluated are contained in the same critical band
		for f_key in dict_aud:
			if f_key>f1 and f_key<f2:
				dict_CB[f_key]=dict_aud.get(f_key)
		#Get the tone ft with the highest audibility
		ft=max(dict_CB, key=dict_CB.get)
		if ft>50 and ft<1000:
			fd=21*np.power(10,1.2*np.power(abs(np.log10(ft/212)),1.8))
			#to be evaluated separately both tones must be under 1000Hz and fd>(ft-f)
			for f_key2 in dict_CB: #check conditions for the tones within ft's CB
				if (f_key2<1000) and (ft!=f_key2) and (ft-f_key2<fd) and (f_key2 in dict_aud_aux):
					print("\n")
					print("Deleted f=", f_key2, "because of the fd criteria")
					del dict_aud_aux[f_key2]
					list_ft_audib.remove(f_key2)
	return list_ft_audib, dict_aud_aux
