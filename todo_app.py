# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 23:38:17 2016

@author: shanki
"""

import pandas as pd

import sys  

# this is to deal with some utf-8 issue that was preventing output 
# http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
reload(sys)  
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)

#global keywd
#keywd =''

# load todo file
def load_todo(todofile):
    todolist = []

    with open(todofile,'r') as f:
        for line in f:
            linec = line.rstrip()
            todolist.append(linec)
    
    l1 = 0
    l2 = 0
    idx1 = []
    idx2 = []
    idx3 = []
    
    for entry in todolist:
        if entry.split()[0] == '*':
            l1 = l1+1
            l2 = 0
            l3 = 0
        elif entry.split()[0] == '**':
            l2 = l2+1
            l3 = 0
        elif entry.split()[0] == '***':
            l3 = l3+1
        idx1.append(l1)
        idx2.append(l2)
        idx3.append(l3)
        
    tododf = pd.DataFrame({'idx1':idx1, 'idx2':idx2, 'idx3':idx3, 'todolist': todolist})  

    return tododf
    
def priorityColor(task):
    if 'pr:1'in task:
        return 'blue'
    elif 'pr:2' in task:
        return 'green'
    elif 'pr:3' in task:
        return 'brown'
    else:
        return 'nocolor'

#tmp = load_todo('todo.txt')

@app.route('/todo_list/<lvl>')
def todo_list(lvl):
    tododf = load_todo('todo.txt')
    tododf['color'] = tododf['todolist'].apply(priorityColor)
    
    if lvl == '1':
        todofilt = tododf[tododf['idx2'] == 0]
    elif lvl == '2':
        todofilt = tododf[tododf['idx3'] == 0]
    else:
        todofilt = tododf
        
    todo_list = todofilt[['todolist','color']].to_dict('records')
    return render_template('list_todo.html',items = todo_list)
    
@app.route('/keywdSrch', methods = ['GET','POST'])
def keywdSrch():
    #global keywd
    if request.method == 'POST':
        keywd = request.form['keywd']
        return redirect(url_for('keywdSrchList',keywd = keywd))
    else:
        return render_template('keywdSrch.html')

@app.route('/keywdSrchList/<keywd>', methods = ['GET','POST'])    
def keywdSrchList(keywd):
    tododf = load_todo('todo.txt')
    tododf['color'] = tododf['todolist'].apply(priorityColor)

    #keywd = 'ACTIVE'

    todofilt = tododf[tododf['todolist'].str.contains(keywd)]

    todo_parent1 = tododf[tododf.idx2 == 0]
    todo_parent1 = todo_parent1.merge(todofilt[['idx1']],how = 'inner')

    todo_parent2 = tododf[(tododf.idx2 > 0) & (tododf.idx3 == 0)]
    todo_parent2 = todo_parent2.merge(todofilt[['idx1','idx2']],how = 'inner')

    todofilt2 = todofilt.append(todo_parent1).append(todo_parent2).drop_duplicates()
    todofilt2 = todofilt2.sort_values(['idx1','idx2','idx3'])

    todo_list = todofilt2[['todolist','color']].to_dict('records')
    return render_template('list_todo.html',items = todo_list)

    
if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
    
    
    