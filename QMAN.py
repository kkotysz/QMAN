#! /usr/bin/env python                                         
# -*- coding: utf-8 -*-

#TO DO: ERROR MANAGEMENT; DEFAULT CCDOBS DIR

import sys
import numpy as np
# import matplotlib.pyplot as plt
import itertools as it
import datetime
import Tkinter as Tk
import tkFont
import os
import fileinput
from colorama import Fore, init, Style

class ccdobs_Object:
    objCount = 0

    def __init__(self, name, n_exp, filter_type, img_type, exp_t, readout_time):
        self.name = name
        self.n_exp = n_exp
        self.filter_type = filter_type
        self.img_type = img_type
        self.exp_t = exp_t
        self.readout_time = readout_time
        ccdobs_Object.objCount += 1
    
    def displayCount(self):
        print "Total Objects %d" % ccdobs_Object.objCount
        return
    def displayObject(self):
        print "Name : ", self.name,  "\nExposure Times: ", self.exp_t
        return
    def countQTime(self):
        total_exp_t = [a*b for a,b in zip(self.n_exp,self.exp_t)]
        total_readout_time = [a*b*1e-6*n_px for a,b in zip(self.n_exp,self.readout_time)]
        return np.sum(total_exp_t) + np.sum(total_readout_time)
    def textQueue(self):
        obj_arr = np.array([self.n_exp, self.filter_type, self.img_type, self.exp_t, self.readout_time]).T
        obj_str = '\n'.join('\t'.join(x for x in y) for y in obj_arr)
        obj_str2 = '\n'.join('{:>3}  {:5}  {:9}  {:>6}  {:>2}'.format(*y) for y in obj_arr)
        return obj_str2
        
def create_curr_obj(current_queue):
    current_queue = filter(len, current_queue)
    ne = [int(current_queue[i].split()[0]) for i in range(len(current_queue))]
    it = [str(current_queue[i].split()[1]) for i in range(len(current_queue))]
    fi = [str(current_queue[i].split()[2]) for i in range(len(current_queue))]
    et = [float(current_queue[i].split()[3]) for i in range(len(current_queue))]
    rt = [int(current_queue[i].split()[4]) for i in range(len(current_queue))]


    return ccdobs_Object('0_CURRENT_QUEUE',ne,it,fi,et,rt)    

def immediately(event):
    global value
    w = event.widget
    try:
        index = int(w.curselection()[0])
        value = w.get(index)
        Tb1.delete(1.0, Tk.END)
        Tb2.config(state=Tk.NORMAL)
        Tb2.delete(1.0, Tk.END)
        try:
            Tb1.insert(Tk.INSERT, objects[value].textQueue())
            Tb2.insert(Tk.INSERT, '{:<8.2f}sec\n'.format(objects[value].countQTime()))
            h,m,s = str(datetime.timedelta(seconds=objects[value].countQTime())).split(':')
        except KeyError:
            if value == '0_CURRENT_QUEUE':
                Tb1.insert(Tk.INSERT, curr_obj.textQueue())
                Tb2.insert(Tk.INSERT, '{:<8.2f}sec\n'.format(curr_obj.countQTime()))
                h,m,s = str(datetime.timedelta(seconds=curr_obj.countQTime())).split(':')
        Tb2.insert(Tk.INSERT, '{:02d}h {:02d}m {:2.2f}s'.format(int(h),int(m),float(s)))
        Tb2.config(state=Tk.DISABLED)
    except IndexError:
        pass

def edit_oname():
    new_name = str(obj_name.get())
    if new_name not in objects.keys() and new_name != '0_CURRENT_QUEUE':
        try:
            objects[value].name = new_name
            objects[new_name] = objects.pop(value)
            with open(ccdobs) as f, open("ccdobs_temp.txt", "w") as out:
                for line in f:
                    if 'Han' in line:
                        line = line.replace('Han      ', 'Ha narrow')
                    if 'Haw' in line:
                        line = line.replace('Haw    ', 'Ha wide')
                    if value == line.strip('%').strip():
                        line = line.replace(value, new_name)
                    out.write(line)
            os.remove(ccdobs)
            os.rename("ccdobs_temp.txt", ccdobs)
            sort_list()
        except KeyError:
            print "#ERROR: OPERATION NOT ALLOWED"
    else:
        print "#ERROR: NAME ALREADY TAKEN"
def set_queue():
    global curr_obj
    new_queue = Tb1.get('1.0',Tk.END)
    new_queue2 = new_queue.replace('Han      ', 'Ha narrow')
    new_queue2 = new_queue2.replace('Haw    ', 'Ha wide')
             
    lookup = '%'
    with open(ccdobs) as f:
        for num, line in enumerate(f, 1):
            if lookup in line:
                line_n = num-1
                break
    
    nfirstlines = []
    
    with open(ccdobs) as f, open("ccdobs_temp.txt", "w") as out:
        for x in xrange(line_n):
            nfirstlines.append(next(f))
        for line in f:
            if 'Han' in line:
                line = line.replace('Han      ', 'Ha narrow')
            if 'Haw' in line:
                line = line.replace('Haw    ', 'Ha wide')
            out.write(line)
    os.remove(ccdobs)
    os.rename("ccdobs_temp.txt", ccdobs)


    with open(ccdobs, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(new_queue2.rstrip('\r\n') + '\n\n' + content)
    
    Tb2.config(state=Tk.NORMAL)
    Tb2.delete(1.0, Tk.END)
    curr_obj = create_curr_obj(new_queue.strip().splitlines())
    Tb2.insert(Tk.INSERT, '{:<8.2f}sec\n'.format(curr_obj.countQTime()))
    h,m,s = str(datetime.timedelta(seconds=curr_obj.countQTime())).split(':')
    Tb2.insert(Tk.INSERT, '{:02d}h {:02d}m {:2.2f}s'.format(int(h),int(m),float(s)))
    Tb2.config(state=Tk.DISABLED)
    
def sort_list():
    Lb1.delete(0,Tk.END)
    for item in objects.keys():
        Lb1.insert(Tk.END, item)
    Lb1.insert(Tk.END, curr_obj.name)
    temp_list = list(Lb1.get(0, Tk.END))
    temp_list.sort(key=str.lower)
    # delete contents of present listbox
    Lb1.delete(0, Tk.END)
    # load listbox with sorted data
    for item in temp_list:
        Lb1.insert(Tk.END, item)
    Lb1.itemconfig(0, background='red', foreground='yellow')
    
def open_queue():
    global curr_obj
    try:
        with open(ccdobs) as f:
            contents = f.read()
            for entry in contents.split('%')[:1]:
                # print entry
                if 'Ha wide' or 'Ha narrow' in entry:
                    entry=entry.replace('Ha wide','Haw')
                    entry=entry.replace('Ha narrow','Han')
                current_queue = entry.strip().splitlines()
            for entry in contents.split('%')[1:]:
                if 'Ha wide' or 'Ha narrow' in entry:
                    entry=entry.replace('Ha wide','Haw')
                    entry=entry.replace('Ha narrow','Han')
                queue.append(entry.strip().splitlines())
    except IOError:
        print " # ERROR! Problem loading data from '" + ccdobs + "'!"
        sys.exit(1)
        
    curr_obj = create_curr_obj(current_queue)
    for q in queue:
        ne = [int(q[1:][i].split()[0]) for i in range(len(q[1:]))]
        it = [str(q[1:][i].split()[1]) for i in range(len(q[1:]))]
        fi = [str(q[1:][i].split()[2]) for i in range(len(q[1:]))]
        et = [float(q[1:][i].split()[3]) for i in range(len(q[1:]))]
        rt = [int(q[1:][i].split()[4]) for i in range(len(q[1:]))]
        objects[q[0]] = ccdobs_Object(q[0],ne,it,fi,et,rt)
    
    print "Queue time:"
    print '{:<8.2f}sec'.format(curr_obj.countQTime())
    h,m,s = str(datetime.timedelta(seconds=curr_obj.countQTime())).split(':')
    print '{:02d}h {:02d}m {:2.2f}s'.format(int(h),int(m),float(s))
def delete_object():
    lookup = '% '+value
    
    try:
        objects.pop(value)
        new_queue = Tb1.get('1.0',Tk.END)
        
        line_n = []
        with open(ccdobs) as f:
            for num, line in enumerate(f, 1):
                if lookup in line:
                    line_n.append(num-1)
                    lookup = '%'
                if len(line_n) == 2:
                    break
        
        nfirstlines = []
        
        with open(ccdobs) as f, open("ccdobs_temp.txt", "w") as out:
            for num, line in enumerate(f,1):
                if 'Han' in line:
                    line = line.replace('Han      ', 'Ha narrow')
                if 'Haw' in line:
                    line = line.replace('Haw    ', 'Ha wide')
                out.write(line)
                if num == line_n[0]:
                    break
            if len(line_n) == 2:
                for x in xrange(abs(line_n[0]-line_n[1])):
                    nfirstlines.append(next(f))
                for line in f:
                    out.write(line)
        os.remove(ccdobs)
        os.rename("ccdobs_temp.txt", ccdobs)
    
        sort_list()
        objc.set("Total number of objects: "+str(len(objects)))
    except KeyError:
        print "#ERROR: OPERATION NOT ALLOWED"
    root.update_idletasks()
    
def add_new():
    new_name = str(add_name.get())
    lookup = '% '+new_name
    if new_name not in objects.keys() and new_name != '0_CURRENT_QUEUE':
        new_queue = Tb1.get('1.0',Tk.END)
        new_queue2 = new_queue.replace('Han      ', 'Ha narrow')
        new_queue2 = new_queue2.replace('Haw    ', 'Ha wide')
        with open(ccdobs, 'r+') as f:
            #content = f.read()
            f.seek(0, 2)
            f.write('\n% '+new_name+'\n')
            f.write(new_queue2.rstrip('\r\n') + '\n')
        objects[new_name] = create_curr_obj(new_queue.strip().splitlines())
        Tb2.config(state=Tk.NORMAL)
        Tb2.delete(1.0, Tk.END)
        Tb2.insert(Tk.INSERT, '{:<8.2f}sec\n'.format(objects[new_name].countQTime()))
        h,m,s = str(datetime.timedelta(seconds=objects[new_name].countQTime())).split(':')
        Tb2.insert(Tk.INSERT, '{:02d}h {:02d}m {:2.2f}s'.format(int(h),int(m),float(s)))
        Tb2.config(state=Tk.DISABLED)
        sort_list()
        objc.set("Total number of objects: "+str(len(objects)))
        root.update_idletasks()
    else:
        print "#ERROR: OBJECT ALREADY EXISTS"
        
def create_color_scheme(c1,c2,c3,c4,bw,btbw):
    bg = c1     #1
    hbg = 'black'    #1
    lbfg = bw    #black or white
    lbafg = bw   #black or white
    lbbg = c1    #1
    lbabg = c3   #3
    sbfg = c2    #2
    sbbg = c1    #1
    tbfg = bw    #black or white
    tbbg = c2    #2
    btfg = btbw    #black or white
    btafg = btbw   #black or white
    btbg = c3    #3
    btabg = c4   #4
    bthbg = 'black'
    etfg = bw    #black or white
    etbg = c2    #2
    return bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg

if __name__ == "__main__":          
    if len(sys.argv) < 2 or len(sys.argv) > 5:
        init(autoreset=True)
        print Fore.RED+Style.BRIGHT+"\n 'QMAN.py'\n                                                                                    "
        print Fore.RED+Style.BRIGHT+" Q"+Style.RESET_ALL+"ueue ", Fore.RED+Style.BRIGHT+"MAN"+Style.RESET_ALL+"ager for CCDOBS program."
        print " Usage: QMAN.py <ccdobs.lst> [<obj_name> -o] [<color_scheme>]\n                                                         "
        print " Option '<obj_name> -o': count queue time for <obj_name> \n                                                             "
        print " Option '<color_scheme>': if not specified -> default. Possible color options: \n                                       "
        print " from cl1 to cl14  Example: QMAN.py ccdobs.lst cl12 \n                                                                "
        print " Version of 29.03.2018 by K. Kotysz: k.kotysz(at)gmail.com"
        print "                          P. Mikolajczyk(at)astro.uni.wroc.pl                                                           "
        sys.exit(1)
    
    n_px = 1252*1152
    ccdobs = sys.argv[1]
    queue = []
    objects = {}
    bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#324851','#7DA3A1','#86AC41','#34675C','black','black')
    lbfg = 'white'
    if 'cl1' in sys.argv:
        bg = 'black'
        lbfg = 'white'
        lbafg = 'black'
        sbfg = 'white'
        tbfg = 'white'
        btfg = 'white'
        btafg = 'black'
        btabg = 'white'
        bthbg = 'white'
        etfg = 'white'
        lbbg = 'black'
        lbabg = 'white'
        sbbg = 'black'
        tbfg = 'white'
        tbbg = 'black'
        btbg = 'black'
        etbg = 'black'
        hbg = 'white'
    if 'cl2' in sys.argv:
        bg = 'white'
        lbfg = 'black'
        lbafg = 'white'
        sbfg = 'black'
        tbfg = 'black'
        btfg = 'black'
        btafg = 'white'
        btabg = 'black'
        bthbg = 'black'
        etfg = 'black'
        lbbg = 'white'
        lbabg = 'black'
        sbbg = 'white'
        tbfg = 'black'
        tbbg = 'white'
        btbg = 'white'
        etbg = 'white'
        hbg = 'black'
    if 'cl3' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#F1F1F2','#BCBABE','#A1D6E2','#1995AD','#232B2B','#232B2B')
    if 'cl4' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#011A27','#063852','#F0810F','#E6DF44','white','black')
    if 'cl5' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#626D71','#CDCDC0','#DDBC95','#B38867','black','black')
    if 'cl6' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#AF4425','#662E1C','#EBDCB2','#C9A66B','white','black')
        lbafg = 'black'
    if 'cl7' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#C1E1DC','#FFCCAC','#FFEB94','#FDD475','black','black')
    if 'cl8' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#805A3B','#FEF2E4','#FD974F','#C60000','black','black')
    if 'cl9' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#D5C3AA','#EAE2D6','#867666','#E1B80D','black','black')
    if 'cl10' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#68A225','#B3DE81','#FDFFFF','#265C00','black','black')
    if 'cl11' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#2A2922','#7D5642','#506D2F','#F3EBDD','white','black')
    if 'cl12' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#353C3F','#D5D6D2','#756867','#FF8D3F','black','black')
        lbfg = 'white'
        lbafg = 'white'
    if 'cl13' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#282623','#A3A599','#FBCD4B','#FF8D3F','black','black')
        lbfg = 'white'
    if 'cl14' in sys.argv:
        bg,hbg,lbfg,lbafg,sbfg,tbfg,btfg,btafg,bthbg,etfg,lbbg,lbabg,sbbg,tbbg,btbg,btabg,etbg = create_color_scheme('#232122','#DDDEDE','#A5C05B','#7BA4A8','black','black')
        lbfg = 'white'
    font = 'EversonMono 11 bold'
    fontbt = 'Impact 18'
    fontla = 'Impact 12'
    font2 = 'EversonMono 11 bold'
    
    if '-o' in sys.argv:
        open_queue()
        
        obj_name = sys.argv[2]
        print "\nQueue time for",obj_name+":"
        try:
            print '{:<8.2f}sec'.format(objects[obj_name].countQTime())
            h,m,s = str(datetime.timedelta(seconds=objects[obj_name].countQTime())).split(':')
            print '{:02d}h {:02d}m {:2.2f}s'.format(int(h),int(m),float(s))
        except KeyError:
            print "# ERROR! Object name not in ccdobs.lst!"
    if '-o' not in sys.argv:
        root = Tk.Tk()
        open_queue()
        root.title('QMAN.py (Queue MANager for CCDOBS program)')
        root.configure(background=bg)
        root.geometry('960x540')
        obj_name = Tk.StringVar()
        add_name = Tk.StringVar()
        
        Sb1 = Tk.Scrollbar(root)
        Sb2 = Tk.Scrollbar(root)
        
        Lb1 = Tk.Listbox(root)
        for item in objects.keys():
            Lb1.insert(Tk.END, item)
        Lb1.insert(Tk.END, curr_obj.name)
        sort_list()
        Lb1.bind('<<ListboxSelect>>', immediately)
        
        
        Tb1 = Tk.Text(root)
        Tb1.insert(Tk.INSERT, curr_obj.textQueue())
        
        Tb2 = Tk.Text(root)
        Tb2.insert(Tk.INSERT, '{:<8.2f}sec\n'.format(curr_obj.countQTime()))
        h,m,s = str(datetime.timedelta(seconds=curr_obj.countQTime())).split(':')
        Tb2.insert(Tk.INSERT, '{:02d}h {:02d}m {:2.2f}s'.format(int(h),int(m),float(s)))
        Tb2.config(state=Tk.DISABLED)
        
        Bt1 = Tk.Button(root, text='SET QUEUE', command = set_queue)
        Bt2 = Tk.Button(root, text='CHANGE NAME', command = edit_oname)
        Bt3 = Tk.Button(root, text='DELETE', command = delete_object)
        Bt4 = Tk.Button(root, text='ADD NEW', command = add_new)
        Et1 = Tk.Entry(root, textvariable = obj_name)
        Et2 = Tk.Entry(root, textvariable = add_name)
        objc = Tk.StringVar()
        objc.set("Total number of objects: "+str(len(objects)))
        La1 = Tk.Label(root, textvariable=objc)
        
        pdx = 3
        pdy = 3
        Lb1.grid(row=0,  column=0,  columnspan=1,  rowspan=4, padx = pdx, pady = pdy, sticky = 'nsew')
        Sb1.grid(row=0,  column=1,  columnspan=1,  rowspan=4, padx = pdx, pady = pdy, sticky = 'nsw')
        Tb1.grid(row=0,  column=2,  columnspan=4,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew', ipady = 80)
        Sb2.grid(row=0,  column=6,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsw')
        Tb2.grid(row=1,  column=2,  columnspan=4,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew')
        Bt1.grid(row=2,  column=3,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew', ipady = 10)
        Bt2.grid(row=2,  column=2,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew', ipady = 10)
        Bt3.grid(row=2,  column=4,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew', ipady = 10)
        Bt4.grid(row=2,  column=5,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew', ipady = 10)
        Et1.grid(row=3,  column=2,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew')
        Et2.grid(row=3,  column=5,  columnspan=1,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew')
        La1.grid(row=3,  column=3,  columnspan=2,  rowspan=1, padx = pdx, pady = pdy, sticky = 'nsew', ipady = 4)
        
        Lb1.config(yscrollcommand=Sb1.set, font=font, bg=lbbg, fg=lbfg, selectbackground=lbabg, selectforeground=lbafg, activestyle=Tk.NONE, width = 20, height = 28, borderwidth = 0, highlightthickness=0)
        Lb1.itemconfig(0, background = 'red', foreground='yellow')
        Sb1.config(command=Lb1.yview, bg=sbbg, troughcolor=sbfg)
        Sb2.config(command=Tb1.yview, bg=sbbg, troughcolor=sbfg)
        Tb1.config(yscrollcommand=Sb2.set, font=font2, bg=tbbg, fg=tbfg, width = 75, height = 10, insertbackground = tbfg, borderwidth = 0, highlightbackground=hbg, highlightcolor=hbg, highlightthickness=1, selectbackground=btabg, selectforeground=btafg)
        Tb2.config(font=font2, bg=tbbg, fg=tbfg, width = 75, height = 3, borderwidth = 0, highlightbackground=hbg, highlightcolor=hbg, highlightthickness=1, selectbackground=btabg, selectforeground=btafg)
        Bt1.config(font=fontbt, bg=btbg, fg=btfg, activebackground=btabg, activeforeground=btafg, width = 10, height = 2, borderwidth = 0, highlightbackground=bthbg, highlightthickness=2)
        Bt2.config(font=fontbt, bg=btbg, fg=btfg, activebackground=btabg, activeforeground=btafg, width = 10, height = 2, borderwidth = 0, highlightbackground=bthbg, highlightthickness=2)
        Bt3.config(font=fontbt, bg=btbg, fg=btfg, activebackground=btabg, activeforeground=btafg, width = 10, height = 2, borderwidth = 0, highlightbackground=bthbg, highlightthickness=2)
        Bt4.config(font=fontbt, bg=btbg, fg=btfg, activebackground=btabg, activeforeground=btafg, width = 10, height = 2, borderwidth = 0, highlightbackground=bthbg, highlightthickness=2)
        Et1.config(font=font, bg=etbg, fg=etfg, width = 15, insertbackground = etfg, borderwidth = 0, highlightbackground=hbg, highlightcolor=hbg, highlightthickness=1, selectbackground=btabg, selectforeground=btafg)
        Et2.config(font=font, bg=etbg, fg=etfg, width = 15, insertbackground = etfg, borderwidth = 0, highlightbackground=hbg, highlightcolor=hbg, highlightthickness=1, selectbackground=btabg, selectforeground=btafg)
        La1.config(font=fontla, bg=etbg, fg=etfg, width = 25, height = 1, borderwidth = 0, highlightbackground=hbg, highlightthickness=1)
        for x, w in zip([0,2,3,4,5],[12,10,10,10,10]):
            Tk.Grid.columnconfigure(root, x, weight=w)
        for y, w in zip([0,1,2,3],[10,1,2,1]):
            Tk.Grid.rowconfigure(root, y, weight=w)
        root.mainloop()
        

