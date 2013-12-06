#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to train a chunk tokenizer to detect named entities\
    such as persons, locations and organizations in a given document.

    (For the purpose of the training an external maximun entropy model (megam)\
    is used.

After the chunker has been created, it is pickled for subsequent use.
"""

import nltk
import logging
import pickle

MEGAM_FOLDER = 'topics/megam_0.92/megam'

try:
    nltk.config_megam(MEGAM_FOLDER)
except LookupError:
    nltk.config_megam('megam_0.92/megam')


# define logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s')


class BigramChunker(nltk.ChunkParserI):
    """This class defines a bigram chunker"""
    def __init__(self, train_sents):
        """Construct a new BigramChunker instance.
            :param train_sents: Array of sentences with named entities tagged

        """
        train_data = [[(t, c) for w, t, c in nltk.chunk.tree2conlltags(sent)]
                      for sent in train_sents]
        self.tagger = nltk.UnigramTagger(train_data)

    def parse(self, sentence):
        """Converts the tag sequence provided by the tagger back into a\
        chunk tree

        :param sentence: Array of word and part of speech tag

        """
        pos_tags = [pos for (word, pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word, pos), chunktag)
                     in zip(sentence, chunktags)]
        return nltk.chunk.util.conlltags2tree(conlltags)


class ConsecutiveNPChunkTagger(nltk.TaggerI):
    """This class defines a chunker to tag named entities"""
    def __init__(self, train_sents):
        """Construct a new ConsecutiveNPChunkTagger instance.

        :param train_sents: Array of sentences with named entities tagged

        """
        train_set = []
        for tagged_sent in train_sents:
            untagged_sent = nltk.tag.untag(tagged_sent)
            history = []
            for i, (word, tag) in enumerate(tagged_sent):
                featureset = npchunk_features(untagged_sent, i)
                train_set.append((featureset, tag))
                history.append(tag)

        self.classifier = nltk.MaxentClassifier.train(
            train_set, algorithm='megam', trace=0)

    def tag(self, sentence):
        """Tag the provided sentence with named entities.

        :param sentence: Array of word and part of speech tag

        """
        history = []
        for i, word in enumerate(sentence):
            featureset = npchunk_features(sentence, i)
            tag = self.classifier.classify(featureset)
            history.append(tag)
        return zip(sentence, history)


class ConsecutiveNPChunker(nltk.ChunkParserI):
    """This class is a wrapper around the tagger class that turns it\
     into a chunker"""

    def __init__(self, train_sents):
        """Construct a new ConsecutiveNPChunker instance.

        :param train_sents: Array of sentences with named entities tagged

        """
        tagged_sents = [[((w.lower(), t), c) for (w, t, c) in
                         nltk.chunk.tree2conlltags(sent)]
                        for sent in train_sents]
        self.tagger = ConsecutiveNPChunkTagger(tagged_sents)

    def parse(self, sentence):
        """Converts the tag sequence provided by the tagger back into a\
        chunk tree

        :param sentence: Array of word and part of speech tag

        """
        tagged_sents = self.tagger.tag(sentence)
        conlltags = [(w, t, c) for ((w, t), c) in tagged_sents]
        return nltk.chunk.util.conlltags2tree(conlltags)


def npchunk_features(sentence, i):
    """Feature extractor

    :param sentence: Array of word and part of speech tag
    :param i: Index of the actual word

    """
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
            "pos+nextpos": "%s+%s" % (pos, nextpos),
            "tags-since-dt": tags_since_dt(sentence, i)
            }


def tags_since_dt(sentence, i):
    """Creates a string describing the set of all part-of-speech tags\
    that have been encountered since the most recent determiner.

    :param sentence: Array of word and part of speech tag
    :param i: Index of the actual word

    """
    tags = set()
    for word, pos in sentence[:i]:
        if pos == 'DA':
            tags = set()
        else:
            tags.add(pos)
    return '+'.join(sorted(tags))


def test_chunk_tagger():
    """
        Test Chunk tagger.
    """

    from nltk.tokenize import word_tokenize

    def traverse(t):
        try:
            t.node
        except AttributeError:
            print t,
        else:
            # Now we know that t.node is defined
            print '(', t.node,
            for child in t:
                traverse(child)
            print ')',

    logging.info('Loading PoS tagger')
    pos_tag = pickle.load(open("tmp/pos_tagger.p", "rb")).tag
    logging.info('Loading Chunk tagger')
    chunk_tag = pickle.load(open("tmp/chunk_tagger.p", "rb")).parse
    loc = nltk.Tree('LOC', [(u'santander', u'NC')])
    org = nltk.Tree('ORG', [(u'izquierda', u'NC')])

    test_tree = nltk.Tree('S', [org,
    (u'unida', u'AQ'),
    (u'de', u'SP'),
    loc,
    (unicode('presentó', 'utf-8'), u'VMI'),
    (u'hoy', u'RG'),
    (u'su', u'DP'),
    (u'nuevo', u'AQ'),
    (unicode('boletín', 'utf-8'), u'NC'),
    (u'trimestral', u'AQ')])

    string = unicode(
        """Izquierda Unida de Santander presentó hoy su nuevo boletín\
 trimestral""",
        'utf-8'
    )
    tokens = [token.lower() for token in word_tokenize(string)]
    pos_tokens = pos_tag(tokens)
    result = chunk_tag(pos_tokens)

    assert result == test_tree


def main():
    """ Main function. """

    logging.info('Starting training chunker...')
    train_set = nltk.corpus.conll2002.chunked_sents('esp.train')
    chunker_es = ConsecutiveNPChunker(train_set)

    logging.info('Pickling chunker...')
    pickle.dump(chunker_es, open("tmp/chunk_tagger.p", "wb"))

if __name__ == '__main__':
    main()
