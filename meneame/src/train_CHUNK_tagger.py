# -*- coding: utf-8 -*-
"""

"""

import nltk
import logging
import pickle


nltk.config_megam('megam_0.92/megam')

class BigramChunker(nltk.ChunkParserI):
    def __init__(self, train_sents): 
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)]
                      for sent in train_sents]
        self.tagger = nltk.UnigramTagger(train_data) 

    def parse(self, sentence): 
        pos_tags = [pos for (word,pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word,pos),chunktag)
                     in zip(sentence, chunktags)]
        return nltk.chunk.util.conlltags2tree(conlltags)


class ConsecutiveNPChunkTagger(nltk.TaggerI): 

    def __init__(self, train_sents):
        train_set = []
        for tagged_sent in train_sents:
            untagged_sent = nltk.tag.untag(tagged_sent)
            history = []
            for i, (word, tag) in enumerate(tagged_sent):
                featureset = npchunk_features(untagged_sent, i, history) 
                train_set.append( (featureset, tag) )
                history.append(tag)
        
        self.classifier = nltk.MaxentClassifier.train( 
            train_set, algorithm='megam', trace=0)

    def tag(self, sentence):
        history = []
        for i, word in enumerate(sentence):
            featureset = npchunk_features(sentence, i, history)
            tag = self.classifier.classify(featureset)
            history.append(tag)
        return zip(sentence, history)

class ConsecutiveNPChunker(nltk.ChunkParserI): 
    def __init__(self, train_sents):
        tagged_sents = [[((w.lower(),t),c) for (w,t,c) in
                         nltk.chunk.tree2conlltags(sent)]
                        for sent in train_sents]
        self.tagger = ConsecutiveNPChunkTagger(tagged_sents)

    def parse(self, sentence):
        tagged_sents = self.tagger.tag(sentence)
        conlltags = [(w,t,c) for ((w,t),c) in tagged_sents]
        return nltk.chunk.util.conlltags2tree(conlltags)

def npchunk_features(sentence, i, history):
    word, pos = sentence[i]
    if i == 0:
        prevword, prevpos = "<START>", "<START>"
    else:
        prevword, prevpos = sentence[i-1]
    
    if i == len(sentence)-1:
        nextword, nextpos = "<END>", "<END>"
    else:
        nextword, nextpos = sentence[i+1]
    return {"pos": pos,
            "word": word,
            "prevpos": prevpos,
            "nextpos": nextpos, 
            "prevpos+pos": "%s+%s" % (prevpos, pos),  
            "pos+nextpos": "%s+%s" % (pos, nextpos)
            # Further experimentation is needed. Test it with new corpus, AnCora
            ,"tags-since-dt": tags_since_dt(sentence, i)
            }  

def tags_since_dt(sentence, i):
    tags = set()
    for word, pos in sentence[:i]:
        if pos == 'DA' or pos=='DI' or pos=='DP' or pos=='DD' or pos=='DN':
            tags = set()
        else:
            tags.add(pos)
    return '+'.join(sorted(tags))


def main():

    # Train CHUNK with Spanish corpus: conll2002.chunked_sents('es')
    logging.error('training chunker')
    train_set = nltk.corpus.conll2002.chunked_sents('esp.train')
    chunker_es = ConsecutiveNPChunker(train_set)
    
    logging.error('Saving Chunker')
    pickle.dump(chunker_es, open( "tmp/CHUNK_tagger.p", "wb" ) )  

if __name__ == '__main__':
	main()



