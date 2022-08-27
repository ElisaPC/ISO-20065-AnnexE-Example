import numpy as np

#Function to determine the uncertainty of each audible tone and of the decisive tones 
#Param: 
#	Inputs: list_Li_LS - list of Lis to be averaged to determine LS for each tone
#			list_Li_Lt - list of Lis to be added to obtain LT for each tone
#			delta_fc - bandwith of the critical band
#			delta_f - line spacing
#	Output: Uncertainty with a cover factor k=1.645 for a 90 % coverage probability in a bilateral confidence interval
def _uncertainty(list_Li_LS, list_Li_LT, delta_fc, delta_f):
	#list of Li for ft's Lt calculation
	#list of Li that are averaged to form ft's LS
	#bandwidth of the CB
	num_LS=0
	denLS=0
	num_LT=0
	denLT=0
	sigma_L=3
	k=1.645
	for i in range(0,len(list_Li_LS)):
		num_LS=num_LS+(np.power(np.power(10,0.1*list_Li_LS[i]),2))
		denLS=denLS+(np.power(10,0.1*list_Li_LS[i]))
		den_LS=np.power(denLS,2)
	unc_p1=(num_LS/den_LS)
	for j in range(0,len(list_Li_LT)):
		num_LT=num_LT+(np.power(np.power(10,0.1*list_Li_LT[j]),2))
		denLT=denLT+(np.power(10,0.1*list_Li_LT[j]))
		den_LT=np.power(denLT,2)
	unc_p2=(num_LT/den_LT)
	unc_p3=np.power(4.34*(delta_f/delta_fc),2)
	sigma=np.sqrt((unc_p1+unc_p2)*np.power(sigma_L,2)+unc_p3)
	uncertainty=1.645*sigma
	return uncertainty


