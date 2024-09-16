import requests
from nltk.tokenize import word_tokenize
import datetime
import json
import re
import nltk
timestamp = datetime.datetime.now()
from faker import Faker 
fake = Faker() 
import streamlit as st
import pyperclip
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(layout="wide", page_title="Email Anonymization")
st.markdown("<h4 align='center'><u>Email Anonymization</u></h4>", unsafe_allow_html=True)
st.markdown("""
<style>
.stTextArea [data-baseweb=base-input] {
     border: 2px solid blue;
     border-radius: 5px;
 }          
            
            </style>

""", unsafe_allow_html=True)
def hash1(term):
     if term[1] == 'email':
          return fake.email()
     elif term[1] == 'PERSON':
          return fake.name()
     elif term[1] == 'ORGANIZATION':
          return fake.company()
     elif term[1] == 'mobileNumber':
          return fake.phone_number()
     elif term[1] == 'creditCardNumber':
          return fake.credit_card_number()
     elif term[1] == 'IPAddress':
          return fake.ipv4_public()
     elif term[1] == 'cvv':
          return fake.credit_card_security_code()
     elif term[1] == 'time':
          return fake.time()
     elif term[1] == 'GPE':
          return fake.country()
        

     # return base64.b64encode(s.encode('utf-8')).decode('utf-8')
     # alpha= ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '@','.','_','-', ' ',':','|','é','ö']
     # nword = []
     # for c in str(s):
     #      nword.append(str(alpha.index(c)))
     # # print("".join(nword))
     # return "".join(nword)

@st.cache_data
def mask(text, words, output, mapping):
     # right.write(words)
     res = { ele[0]: hash1(ele) for ele in words}
     # print(res)
     mapping.write(json.dumps(res))
     mapping.close()
     for (t, v) in zip(res.keys(), res.values()):
         text = text.replace(t, '<span style="color:red">{}</span>'.format(v))
     #     right.write(t+"=="+v)
     output.write(text)
     output.close()
     return text


ticket = st.text_input(label='Ticket Number')
if ticket not in st.session_state:
     st.session_state['ticketno'] = ticket
left, right = st.columns(2)


text = left.text_area(label="Email Content", height=500)
items = []


# local_file_path='D:\\RCS\\PII\\{}.txt'.format(ticket)
mapfile = 'D:\\RCS\\PII\\{}_map.txt'.format(ticket)
outfile = 'D:\\RCS\\PII\\{}_out.txt'.format(ticket)
infile = 'D:\\RCS\\PII\\{}_in.txt'.format(ticket)
ofile = open(outfile, 'w', encoding='utf-8')
mfile = open(mapfile, 'w', encoding='utf-8')
orfile = open(infile, 'w', encoding='utf-8')
# sfile = open(local_file_path, 'r', encoding='utf-8')
# text = sfile.read()
text = text.replace("""Springer Nature Group
www.springernature.com
--
Visit Springer Nature Support for answers to our most frequently asked questions.
If you would like to contact Open Research Support via chat, please visit BMC Support Portal.
--
Every day around the globe, our imprints, books, journals, platforms and technology solutions reach millions of people – opening the doors to discovery for our communities by enabling them to access, trust and make sense of the latest research, so that they can improve outcomes, make progress, and benefit the generations that follow.
--
In the Americas: Springer Nature Customer Service Center LLC, 200 Hudson Street, Suite 503, Jersey City, NJ 07311, USA
Registered Agent: Corporation Service Company, 251 Little Falls Drive, Wilmington, DE 19808, USA
State of Incorporation: Delaware, Reg. No. 4538065
Outside the Americas: Springer Nature Customer Service Center GmbH, Tiergartenstraße 15 – 17, 69121 Heidelberg, Germany
Registered Office: Heidelberg | Amtsgericht Mannheim, HRB 336546
Managing Directors: Alexandra Dambeck, Harald Wirsching
""", "")
text = re.sub('\n+', '\n', text)
# files = {'Input File': (os.path.basename(local_file_path), open(local_file_path, 'rb'),
#                  'multipart/form-data')}
# response1 = requests.post('https://explore-sdp.straive.com:8091/piiscanner/file/identify', files=files)
# for ffield in response1.json()['piiFields']:
#         print(ffield['word']+"="+hash1(ffield['word']))
# response1 = requests.get('https://explore-sdp.straive.com:8091/piiscanner/testdata')
# print(response1.json())
data = {'chatContent': [{'Timestamp': '{}'.format(timestamp), 'speakerRole': 'Agent', 'Message': '{}'.format(text), 'piiFields': []}]}
response1 = requests.post('https://localhost:8085/piiscanner/identify', data=json.dumps(data), headers={'Accept':'application/json', 'Content-type':'application/json'}, verify=False)
print(response1.status_code)
d=[]
abc = set()
for word in response1.json()['chatContent'][0]['piiFields']:
     d.append((word['word'], word['PII'].replace('<','').replace('>','')))
     abc.add(word['PII'])
tokenized_text = word_tokenize(text)
tagged = nltk.pos_tag(tokenized_text)
entities = nltk.chunk.ne_chunk(tagged)
x=[]
# 
for entity in entities:
     # right.write(entity)
     if hasattr(entity, 'label')and (entity.label() == 'ORGANIZATION' or entity.label() == 'GPE' or entity.label() == 'PERSON'):
        for c in entity:
            if 'Dear' not in c and 'Good' not in c and 'English' not in c and 'Hi' not in c and 'Hello' not in c and 'Thanks' not in c:   
               # right.write((c[0], entity.label()))
               x.append((c[0], entity.label()))
items = d + x

annon = left.button(label="Anonymize")
if annon and text != "":
     st.session_state['otext'] = text
     anontext = mask(text, items, ofile, mfile)
     right.markdown("<b>Anonymized Text</b>", unsafe_allow_html=True)
     right.markdown(anontext, unsafe_allow_html=True)
     right.code(anontext.replace('</span>','').replace('<span style="color:red">',''), language='cshtml')
     st.session_state['antext'] = anontext
