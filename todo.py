
"""
A Simple todo app based on text file

Borrows heavily from journal app in Michael Kennedy's python jumpstart course
https://training.talkpython.fm/courses/explore_python_jumpstart/python-language-jumpstart-building-10-apps

"""


from colorama import Fore, Back, Style 
import sys, os
import pandas as pd

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
    
def list_todo(tododf):
    for line in tododf['todolist']:
        print line
               
def srch_keyword(tododf, keywd):
    todofilt = tododf[tododf['todolist'].str.contains(keywd)]

    todo_parent1 = tododf[tododf.idx2 == 0]
    todo_parent1 = todo_parent1.merge(todofilt[['idx1']],how = 'inner')

    todo_parent2 = tododf[(tododf.idx2 > 0) & (tododf.idx3 == 0)]
    todo_parent2 = todo_parent2.merge(todofilt[['idx1','idx2']],how = 'inner')

    todofilt2 = todofilt.append(todo_parent1).append(todo_parent2).drop_duplicates()
    todofilt2 = todofilt2.sort_values(['idx1','idx2','idx3'])

    for line in todofilt2['todolist']:
        print line
    
    
def main():
    # print header
    print_header()
    # run event loop
    run_event_loop()
    
def print_header():
    print '---------------------------'
    print '   SIMPLE TODO APP'
    print '---------------------------'    
    
def run_event_loop():
     
    cmd = 'start'
    todofile = 'todo.txt'
    tododf = load_todo(todofile)
    
    while cmd != 'exit':
        cmd = raw_input('give something: ') 
        if cmd.lower() == 'l':
            list_todo(tododf)
        else:
            print 'pay attention, give right input'

#def addTODO():
#    moretodo = 'Y'
#    while moretodo == 'Y':
#        todoitem = raw_input('Enter todoitem: \n')
#        with open(todofile,'a') as myfile:
#            myfile.write('\n' + todoitem)
#            moretodo = raw_input('Do you want to enter another todo item? (Y or N): ')
#            
if __name__ == '__main__':
    main()