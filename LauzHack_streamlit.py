#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 15:29:57 2019

@author: zhantao
"""

import os
import re
import glob
import warnings
import streamlit as st
import numpy as np
import pandas as pd
import PyPDF2
from gensim.models import KeyedVectors

OUTPUT_FORMAT = ['Sentences', 'Highlight text']
CAREER_TUPLE  = ('Employee', 'Employer', 'Student', 'Manager', 'Professor')
KEYWORD_TUPLE = np.array(['Salary', 'Privacy policy', 'Signal processing', 'Deep learning'])

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
    model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', 
                                          limit=50000, binary=True)
    related_words = []
    nonsence = []
    for key in keywords:
        if key not in model.vocab.keys():
            nonsence += [key]
            continue
        related_words += model.similar_by_word(key, topn=topn)
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

def get_important_sentences(file, keywords, show, topn_word=200, show_all=False):
    """
    Extract important sentences from file
    
    show: Highlight text: show original text with highlight
          Sentences: show only the sentences
    """
    
    sentences = load_data(file)
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
            
    sentences_show = ""
    if nonsence:
        sentences_show += "_There is no sentences related to {}_ <br><br>".format(", ".join(nonsence))
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
        

    
    
