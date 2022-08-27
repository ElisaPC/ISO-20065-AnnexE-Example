#pruebas
import _LS_spectral_lines
import _formula
import _critical_band
import _criteria
import _uncertainty

def _spectra_i_calculations(EXAMPLE_SPECTRUM_Li, EXAMPLE_SPECTRUM_FREQS,delta_f,delta_fe, ft, ft_index, dict_lines_assigned, list_aud_not_disticnt, dict_LS,dict_Lt, dict_Li_LS):
	Li_ft=EXAMPLE_SPECTRUM_Li[ft_index]
	print("Li of the tone ft(narrow band level)=", Li_ft)
		
	#To study the distinctness Lu and Lo are required, as well as their freq fu and fo
	fu=EXAMPLE_SPECTRUM_FREQS[ft_index-1] #f under ft
	fo=EXAMPLE_SPECTRUM_FREQS[ft_index+1] #f over ft
	Lu=EXAMPLE_SPECTRUM_Li[ft_index-1] 
	Lo=EXAMPLE_SPECTRUM_Li[ft_index+1] 
	print("Under ft. Lu=",Lu," en fu=", fu)	
	print("Over ft. Lo=",Lo," en fo=", fo)
	print("\n")	

	#Function called to determine the critic band bandwith as well as the corner frequencies
	#delta_fc,f1,f2=_critical_band_20065._critical_band_20065(ft)
	delta_fc,f1,f2=_critical_band._critical_band(ft, EXAMPLE_SPECTRUM_FREQS)
	print("Bandwidth of the Critical Band=", round(delta_fc,2))
	print("f1=",round(f1,2), "Hz")
	print("f2=",round(f2,2), "Hz")
	print("\n")

	#Function called to get a list of the levels of the spectral lines contained in the critical band, 
	#as well as their index and the value M, which is the count of the spectral lines on the list except 
	#for ft's spectral line, i.e. except the line under study
	list_Li, list_index, M=_LS_spectral_lines._list_levels_ini(ft,f1,f2,EXAMPLE_SPECTRUM_FREQS,EXAMPLE_SPECTRUM_Li)
	#list of spectral lines of a CB without counting ft
	print("List of Li of the spectral lines within the CB of",ft, "=", list_Li) 
	print("List of their respective indexes: ", list_index)
	print("number of lines to be averaged(M)=", M)

	#Function called to carry out the first iteration to determine LS
	LS=_formula._mean_narrow_band_level(M, list_Li, delta_f, delta_fe)
	print("Mean-Narrow Initial level for the critical band centred on",ft, ", LS=", round(LS,2), "dB")
	print("\n")
	list_iteration=[round(LS,2)]
	list_Li_inicial=list_Li
	list_LS_final=[]
	criteria=_criteria._iteration_criteria_LS(list_index,ft_index)
	criteria2=False #set to false until there are no values to compare

	while criteria==True and criteria2==False:
	#while in an iteration step, the new energy mean value isn´t equal within a tolerance of ±0,005 dB to that
	#of the previous iteration step and while the number of lines contributing to the mean narrow-band level to 
	#the right or left of the line under investigation stays over or equal to 5, the iteration continues
		list_aux=list_Li
		list_Li, list_index, M=_LS_spectral_lines._list_levels_LS(list_aux, list_index, delta_f, LS)
		print("List of Li of the spectral lines within the CB after it=", list_Li) 
		print("List of their respective indexes: ", list_index)

		LS=_formula._mean_narrow_band_level(M, list_Li, delta_f, delta_fe)
		list_iteration.append(round(LS,2))
		print("List of LS", list_iteration)
		print("\n")
		dict_LS[ft]=LS

		if len(list_iteration)>2:
			criteria2=_criteria._iteration_criteria_2(list_iteration)
			criteria=_criteria._iteration_criteria_LS(list_index, ft_index)
			if criteria2==True or criteria==False:
				list_LS_final=list_aux #lista anterior, al igual que LS anterior
				LS=list_iteration[len(list_iteration)-1]
		else:
			criteria=_criteria._iteration_criteria_LS(list_index,ft_index)

	print("After the iteration LS=",round(LS,2))
	print("list of spectral lines left", list_LS_final)
	dict_Li_LS[ft]=list_LS_final

	tone_criteria=_criteria.tone_criteria(LS, Li_ft)
	if tone_criteria==False:
		print("\nAs ft=",ft, " Li(ft)<LS+6, it can't be defined as a tone")
		delta_L=0
		#LS=0
		#LT=0
	else:
		#Function called to determine the tone level at the CB, which spectral lines contribute to the tone level
		#Careful not to introduce the list without the tone level, if so the results are not correct
		LT, Tone_BW, LT_max, dict_lines_assigned=_formula._tone_level(EXAMPLE_SPECTRUM_Li, delta_f, LS, ft, Li_ft, ft_index, delta_fe, dict_lines_assigned)
		print("LT en",ft, "es =", round(LT,2))
		print("\n")
		dict_Lt[ft]=LT
		#Function called to determine the tone's (ft) distinctness
		distinct_criteria=_criteria._distinctness_criteria(ft,Lu,Lo,fu,fo, LT_max, Tone_BW)
		print("Tone Bandwidth:", round(Tone_BW,2))
		print("LT_max:", LT_max)
		print("(If the distinctness function returns False, the tone is NOT audible for an individual with normal hearing)")
		print("Are the distinctness conditions for the tone fulfilled?", distinct_criteria)

		if distinct_criteria==True:
			#At last, functions called to find out the critical band level. the masking index and the audibility 
			LG=_formula._critical_band_level(LS,delta_f,delta_fc)
			av=_formula._masking_index(ft)
			delta_L=_formula.audibility(LT, LG, av)
			#uncertainty 
			U_ft=_uncertainty._uncertainty(list_LS_final, dict_lines_assigned[ft], delta_fc, delta_f)
			print("\n")
			print("ft=",ft, "Hz")
			print("After the iteration LS=",round(LS,2))
			print("LT=", round(LT,2))
			print("For a masking index of av=",round(av,2), "and a critical band level LG=",round(LG,2), "the audibility is", round(delta_L,2))
			print("Final result: ", round(delta_L,2),"U=", round(U_ft,2))
		else:
			list_aud_not_disticnt.append(ft)
			#Issue: should not be the case, according to the standard, if distinctness is not met, neither LG nor av is calculated 
			#(therefore aud is not calculated either).
			LG=_formula._critical_band_level(LS,delta_f,delta_fc)
			av=_formula._masking_index(ft)
			delta_L=_formula.audibility(LT, LG, av)
			print("\n")
			print("As the distinctness criteria are not met, the audibility of the tone ft=", ft,"Hz won't be studied.")
			print("But it can be considered for tone addition.")
	return delta_L, dict_lines_assigned, list_aud_not_disticnt, dict_LS, dict_Lt, dict_Li_LS

