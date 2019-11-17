# LauzHack2019

## Inspiration
Information is exploding. Time is money. We love saving money.

We want to summarize long textual information, and often it is not summarizable. Instead, we should extract key phrases only, like what we do for preparing an exam: highlighting what we think are important.

we TL;DR everything.

![highlight](https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcQXvk1X3xJAVaRvGmCzFZ55ljV83DzwxnrHNgw9mi8TGIwWRlcw)

## What it does
Given a txt or pdf file, it reads the content and extracts or highlights sentences related to the given keywords. If no keywords are given, it automatically extracts topics and gives key sentences. The results are shown in the application and can be saved to a txt file with markdown syntax that highlights the extracted information.

It also gives an interesting link related to the context, for some curious and diligent user, as additional materials.

## Implementation
These libraries should be installed in advance:
- numpy
- nltk
- gensim
- streamlit
- PyPDF2
- googlesearch
- mechanize

We also implement the 'GoogleNews-vector' word2vec language model, and the bin file could be downloaded [here](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit). 

Then we can run the 'LauzHack_streamlit.py' in the terminal to see the demo web viewer.
