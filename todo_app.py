# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 23:38:17 2016

@author: notesofdabbler
"""

import pandas as pd
import sys  

from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)

global descsrch, keywdsrch, keywdsrchexcl,lvlpick
descsrch = ''
keywdsrch = ''
keywdexcl = ''

    
def priorityColor(task):
    if 'pr:1'in task:
        return 'red'
    elif 'pr:2' in task:
        return 'green'
    elif 'pr:3' in task:
        return 'blue'
    else:
        return 'nocolor'

@app.route('/keywdSrch', methods = ['GET','POST'])
def keywdSrch():
    global descsrch, keywdsrch, keywdsrchexcl, lvlpick
    if request.method == 'POST':
        descsrch = request.form['descsrch']
        keywdsrch = request.form['keywdsrch']
        keywdsrchexcl = request.form['keywdsrchexcl']
        
        if 'lvl' in request.form:
            lvlpick = 1
        else:
            lvlpick = 2
            
        return redirect(url_for('keywdSrchList'))
    else:
        return render_template('keywdSrch.html')

@app.route('/keywdSrchList', methods = ['GET','POST'])    
def keywdSrchList():
    global descsrch, keywdsrch, keywdsrchexcl, lvlpick
    
    # load todo list
    tododf = pd.read_csv('db/todolist.csv')
    tododf = tododf.fillna('')
    tododf['color'] = tododf['keywd'].apply(priorityColor)

    # search for keyword in list
    #descsrch = ''
    #keywdsrch = 'pr:1|ACTIVE'
    #lvlpick = 2

    todofilt = tododf[tododf.l3_key == 0]

    if descsrch != '':
        todofilt = todofilt[todofilt.desc.str.contains(descsrch, na = False)]
    
    if keywdsrch != '':
        todofilt = todofilt[todofilt.keywd.str.contains(keywdsrch, na = False)]
        
    if keywdsrchexcl != '':
        todofiltexcl = todofilt[todofilt.keywd.str.contains(keywdsrchexcl, na = False)]
        todofiltexcl['excl'] = 1
        todofiltexcl = todofiltexcl[["l1_key","l2_key","l3_key","excl"]]
        todofilt = todofilt.merge(todofiltexcl, on = ['l1_key','l2_key','l3_key'], how = 'left')
        todofilt = todofilt[todofilt.excl != 1]
    
    # Get top level description for filtered tasks
    l1_key_list = todofilt.drop_duplicates(subset = 'l1_key')[['l1_key']]
    todofilt_l1 = tododf[tododf.l2_key == 0]
    todofilt_l1 = todofilt_l1.merge(l1_key_list, on = "l1_key", how = "inner")
    
    # Get tasks who top level got returned
    lvl1only = todofilt.loc[(todofilt.l2_key == 0)][['l1_key']]
    lvl2only = tododf.loc[(tododf.l2_key > 0) & (tododf.l3_key == 0)]
    lvl2only = lvl2only.merge(lvl1only, on = "l1_key", how = "inner")

    todofilt = todofilt.append(todofilt_l1)
    todofilt = todofilt.append(lvl2only)
    todofilt = todofilt.drop_duplicates()
    
    if lvlpick == 1:
        todofilt = todofilt[todofilt.l2_key == 0]

    todofilt = todofilt.sort_values(['l1_key','l2_key'])
    todo_list = todofilt[['l1_key','l2_key','desc','keywd','color']].to_dict('records')
    return render_template('list_todo.html',items = todo_list)

@app.route('/taskupdate/<int:l1_key>/<int:l2_key>/', methods = ['GET','POST'])
def taskupdate(l1_key, l2_key):
    # load todo list
    tododf = pd.read_csv('db/todolist.csv')
    tododf = tododf.fillna('')
    if request.method == 'POST':
        desc = request.form['descupdt']
        keywd = request.form['keywdupdt']
        tododf.loc[(tododf.l1_key == l1_key) & (tododf.l2_key == l2_key) & (tododf.l3_key == 0),'desc'] = desc
        tododf.loc[(tododf.l1_key == l1_key) & (tododf.l2_key == l2_key) & (tododf.l3_key == 0),'keywd'] = keywd
        tododf.to_csv("db/todolist.csv", index = False)
        return redirect(url_for('keywdSrch'))
    else:
        item = tododf[(tododf.l1_key == l1_key) & (tododf.l2_key == l2_key)].to_dict(orient = 'records')
        return render_template('taskupdate.html', item = item[0])
        
@app.route('/newtask/<int:l1_key>/', methods = ['GET','POST'])
def newtask(l1_key):
    
    tododf = pd.read_csv('db/todolist.csv')
    tododf = tododf.fillna('')
    
    if l1_key == 0:
        l1_keynew = max(tododf["l1_key"]) + 1
        l2_keynew = 0
        l3_keynew = 0
    else:
        l1_keynew = l1_key
        l2_keynew = max(tododf[tododf.l1_key == l1_key]["l2_key"]) + 1
        l3_keynew = 0
        
    if request.method == 'POST':
        desc = request.form['descnew']
        keywd = request.form['keywdnew']
        newtaskinfo = {'l1_key':l1_keynew, 'l2_key':l2_keynew, 'l3_key':l3_keynew,
                   'desc':desc, 'keywd':keywd}
        tododf = tododf.append(newtaskinfo, ignore_index=True)
        tododf.to_csv("db/todolist.csv", index = False)
        return redirect(url_for('keywdSrch'))
    else:
        return render_template('newtask.html', l1_key = l1_key)

@app.route('/details/<int:l1_key>/<int:l2_key>/', methods = ['GET','POST'])
def details(l1_key,l2_key):  
    # load todo list
    tododf = pd.read_csv('db/todolist.csv')
    tododf = tododf.fillna('')
    todofilt = tododf[(tododf.l1_key == l1_key) & (tododf.l2_key == l2_key)]
    details_list = todofilt[['l1_key','l2_key','desc']].to_dict('records')
    print(details_list)
    return render_template('details.html', items = details_list)
    
@app.route('/details/<int:l1_key>/<int:l2_key>/newdetails', methods = ['GET','POST'])
def newdetails(l1_key,l2_key):
    
    tododf = pd.read_csv('db/todolist.csv')
    tododf = tododf.fillna('')
    
    l3_keynew = max(tododf[(tododf.l1_key == l1_key) & (tododf.l2_key == l2_key)]["l3_key"])+1
    
    if request.method == 'POST':
        detailsnew = request.form['detailsnew']
        newdetailsinfo = {'l1_key':l1_key, 'l2_key':l2_key, 'l3_key':l3_keynew,
                    'desc':detailsnew, 'keywd':''}
        tododf = tododf.append(newdetailsinfo, ignore_index=True)
        tododf.to_csv("db/todolist.csv", index = False)
        return redirect(url_for('keywdSrch'))
    else:
        return render_template('newdetails.html',l1_key = l1_key, l2_key = l2_key)
    
if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0', port = 9999)
    
    
    