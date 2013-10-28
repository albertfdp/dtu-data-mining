from nltk.stem import SnowballStemmer

languages = SnowballStemmer.languages

class Anew():

    def __init__(self):
        # Stemmer
        stemmer_es = SnowballStemmer("spanish")
        stemmer_en = SnowballStemmer("english") 
        stemmer_da = SnowballStemmer("danish") 
    	# define anew dictionary
    	anew_dict_es = {}
    	for line in open('/Users/bellodcisneros/Dropbox/MSC/SenseMail/django/SenseMail/spanish_anew.txt','rU'):
        #Number, E_Word, S_Word, Val_Mn_All, Val_Sd_All, Aro_Mn_All, Aro_Sd_All, Dom_Mn_All, Dom_Sd_All, Val_Mn_Fem, Val_Sd_Fem,    Aro_Mn_Fem, Aro,Sd_Fem, Dom_Mn_Fem, Dom_Sd_Fem, Val_Mn_Mal, Val_Sd_Mal, Aro_Mn_Mal, Aro_Sd_Mal, Dom_Mn_Mal, Dom_Sd_Mal, Nlett, Nsyll, GClass, Freq, Neigh, Fam, Con, Imag = line.strip().split()
    	    aux = line.strip().split()
    	    #print aux
    	    score = {}
    	    score['valence'] = float(aux[3])
    	    score['arousal'] = float(aux[5])
#     	    print {'x':aux[2]}
    	    anew_dict_es[stemmer_es.stem(unicode(aux[2],'utf-8'))] = score