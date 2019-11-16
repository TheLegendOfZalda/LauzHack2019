#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 15:29:57 2019

@author: zhantao
"""

import os
import re
import glob
import streamlit as st
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

OUTPUT_FORMAT = ['Sentences', 'Highlight text']
CAREER_TUPLE  = ('Employee', 'Employer', 'Student', 'Manager', 'Professor')
KEYWORD_TUPLE = np.array(['Salary', 'Privacy policy', 'Signal processing', 'Deep learning'])

# In[0]
## functions definitions

def file_selector(folder_path='.'):
    filenames = glob.glob( os.path.join(folder_path, '*.txt' ) )
    selected_filename = st.sidebar.selectbox('Select a file to analyse:', filenames)
    return selected_filename

def load_file(file):
    """Given a file path, load textual file"""
    with open(file, "r") as f:
        text = [line.strip() for line in f.readlines()]
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
    model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', 
                                          limit=50000, binary=True)
    related_words = []
    for key in keywords:
        related_words += model.similar_by_word(key, topn=topn)
        related_words += [(key, 1.)]

    related_words = dict(related_words)
    return related_words

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

def get_important_sentences(file, keywords, show, topn_word=200, num_sentence=5):
    """
    Extract important sentences from file
    
    show: Highlight text: show original text with highlight
          Sentences: show only the sentences
    """
    
    sentences = load_data(file)
    related_words = get_related_words(keywords, topn=topn_word)
    scores = get_score(sentences, related_words)
    most_related_sentences_id = np.argsort(scores)[::-1]

    related_sentences = []
    for i in range(len(sentences)):
        if i in most_related_sentences_id[:5]:
            related_sentences += [sentences[i]]
            
    sentences_show = ""
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

def textAnalyzer(filename, outputFormat, career, keywords):
    
    text = get_important_sentences(filename, keywords, show = outputFormat)
    return text

# In[1]
## input paras
st.title('LauzHack 2019, AXA')

filename = file_selector()
st.write('The file is loaded `%s`' % filename)

outFormat = st.sidebar.selectbox('Select an output format:', OUTPUT_FORMAT)

career = st.sidebar.multiselect( 'Career', CAREER_TUPLE)
st.write('You career', career)

keywordList = st.sidebar.text_input('Keywords', ' ')
keywordList = re.findall(r"[\w']+", keywordList)

showAll = st.sidebar.checkbox( 'Show all', ('Show all results'))

# In[1]
## processing
text = textAnalyzer(filename, outFormat, career, keywordList)

# In[2]
## ouotput 
st.header('Related information')
st.markdown(text.replace('<br>', '\n'))


