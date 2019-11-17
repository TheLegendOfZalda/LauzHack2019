#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 15:29:57 2019

@author: zhantao
"""

import os
import re
import glob
import nltk
import warnings
import streamlit as st
import numpy as np
import PyPDF2
import gensim
from gensim.models import KeyedVectors
from nltk.tokenize import word_tokenize
from gensim import corpora
from itertools import combinations
from googlesearch import search 
from mechanize import Browser
  

OUTPUT_FORMAT = ['Sentences', 'Highlight text']
CAREER_TUPLE  = ('Employee', 'Employer', 'Student', 'Manager', 'Professor')
KEYWORD_TUPLE = np.array(['Salary', 'Privacy policy', 'Signal processing', 'Deep learning'])
WORDTOVEC_MODEL = ''

# In[0]
## functions definitions

def file_selector(folder_path='.'):
    filenames = glob.glob( os.path.join(folder_path, '*.txt') ) + glob.glob( os.path.join(folder_path, '*.pdf'))
    selected_filename = st.sidebar.selectbox('Select a file to analyse:', filenames)
    return selected_filename

def load_file(file, show_origin: bool = False):
    """Given a file path, load the file (pdf, txt supported)"""
    text = ''
    if file is not None:
        if(file.endswith('.txt')):
            if not show_origin:
                with open(file, "r") as f:
                    text = [line.strip() for line in f.readlines()]
            else:
                with open(file, 'r') as content_file:
                    text = content_file.read()     
        elif(file.endswith('.pdf')):
            pdfFileObj = open(file, 'rb')
            pdfReader  = PyPDF2.PdfFileReader(pdfFileObj)
            for NumIter in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(NumIter)
                text += pageObj.extractText()
            if not show_origin:
                text = [text]
        else:
            warnings.warn('Format not supported.')
    else:
         warnings.warn('No file found.')
    return text   
    
def load_data(file):
    """Given a file path, process textual file and return a list of sentences"""
    text = load_file(file)
    text = [s for s in text if s != '']
    sentences = [re.split("(?<=[.!?])\s+", p)  for p in text]
    sentences = [item for sublist in sentences for item in sublist]
    return sentences

def get_related_words(keywords, topn=200):
    """Given a list of keywords, return dictionary of words and its weight"""
    global WORDTOVEC_MODEL 
    WORDTOVEC_MODEL = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', 
                                          limit=50000, binary=True)
    related_words = []
    nonsence = []
    for key in keywords:
        if key not in WORDTOVEC_MODEL.vocab.keys():
            nonsence += [key]
            continue
        related_words += WORDTOVEC_MODEL.similar_by_word(key, topn=topn)
        related_words += [(key, 1.)]

    related_words = dict(related_words)
    return related_words, nonsence

def get_score(sentences, related_words):
    """Get scores for sentences"""
    scores = []
    for sent in sentences:
        score = 0.
        words = sent.split(" ")
        for word in words:
            if word in related_words.keys():
                score += related_words[word]
        scores += [score]
    scores = np.array(scores)
    return scores


def find_topic_words(file, num_topics = 1, num_words = 10):
    """ Extract the unique topic words based on LDA model"""
    global WORDTOVEC_MODEL
    en_stop = set(nltk.corpus.stopwords.words('english'))
    
    sentences = load_data(file)
    text_data = []
    for i in sentences:
        tokens = word_tokenize(i)
        tokens = [token for token in tokens if len(token) > 4]
        tokens = [token for token in tokens if token not in en_stop]

        text_data.append(tokens)
    
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]
    
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = num_topics, id2word=dictionary, passes=15)
    topics = ldamodel.print_topics(num_words)
    
    topic_words = []
    for i, k in topics:
        pattern = re.compile('"(.*)"')
        topic_words.append(pattern.findall(k)[0])
    
    topic_words = np.unique(topic_words)
    
    unique_word = topic_words.tolist()
    for i, j in combinations(topic_words, 2):
        sim = WORDTOVEC_MODEL.similarity(i, j)
        if sim > 0.5:
            unique_word.remove(i)
            
    return unique_word


def get_important_sentences(file, keywords, show, topn_word=200, show_all=False):
    """
    Extract important sentences from file
    
    show: Highlight text: show original text with highlight
          Sentences: show only the sentences
    """
    
    sentences = load_data(file)
    topics = find_topic_words(file)
    if keywords == []:
        keywords = topics[:2]
        
    related_words, nonsence = get_related_words(keywords, topn=topn_word)
    scores = get_score(sentences, related_words)
    most_related_sentences_id = np.argsort(scores)[::-1]
    

    num_sentence = 5
    if show_all:
        num_sentence = len(scores[scores > 0])
    
    related_sentences = []
    for i in range(len(sentences)):
        if i in most_related_sentences_id[:num_sentence]:
            related_sentences += [sentences[i]]
            
    query = topics[:3] 
    site = None
    for j in search(query, num=1, stop=1, pause=2): 
        site = j
    br = Browser()
    br.open(site)
    title = br.title()

    sentences_show = ""
    if nonsence:
        sentences_show += "_There is no sentences related to {}_ <br><br>".format(", ".join(nonsence))
        
    sentences_show += "You might be interested in [{}]({}) <br>".format(title, site)
    if show == "Highlight text":
        texts = load_file(file)
        for t in texts:
            for s in related_sentences:
                t = t.replace(s, "**"+s+"**")
            sentences_show += t + "<br>"    
    elif show == "Sentences":
        for i,s in enumerate(related_sentences):
            sentences_show += "<br>" + str(i+1) + ". " + s
    else:
        return "invalid value for show"
    
    sentences_show.replace("$", "\\$")
    return sentences_show


def textAnalyzer(filename, outputFormat, keywords, showAll):
    
    text = get_important_sentences(filename, keywords, show = outputFormat, show_all = showAll)
    return text

def saveAs(text):
    if outFormat == 'Sentences':
        text_file = open("Related_Info.txt", "w")
    else:
        text_file = open("Highted_text.txt", "w")
    text_file.write(text)
    text_file.close()
        
# In[1]
## input paras
st.title('LauzHack 2019, AXA')

filename  = file_selector()

outFormat = st.sidebar.selectbox('Select an output format:', OUTPUT_FORMAT)

keywordList = st.sidebar.text_input('Keywords', ' ')
keywordList = re.findall(r"[\w']+", keywordList)

showAll = st.sidebar.checkbox( 'Show all', ('Show all results'))

saveFile = st.sidebar.button('Save')

st.sidebar.markdown(load_file(filename, show_origin=True))

# In[1]
## processing
text = textAnalyzer(filename, outFormat, keywordList, showAll)

# In[2]
## output 
st.header('Related information')
st.markdown(text.replace('<br>', '\n'))

if saveFile:
    if len(text) > 0:
        saveAs(text.replace('<br>', '\n'))
        st.write('File has been saved.')
    else:
        st.write('No text to save.')
        

    
    
