# Functions in the todo app

import os
os.chdir('/Users/shanki/Documents/notesofdabbler/simpleTODO')

import pandas as pd

# load todo list
tododf = pd.read_csv('db/todolist.csv')

# search for keyword in list
descsrch = 'ACTIVE'
keywdsrch = 'pr:1'
lvlpick = 1

todofilt = tododf[tododf.l3_key == 0]

if descsrch != '':
    todofilt = todofilt[tododf.keywd.str.contains(descsrch, na = False)]
    
if keywdsrch != '':
    todofilt = todofilt[todofilt.keywd.str.contains(keywdsrch, na = False)]
    
if lvlpick == 1:
    todofilt = todofilt[todofilt.l2_key == 0]
    



