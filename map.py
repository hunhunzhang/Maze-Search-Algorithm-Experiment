from tkinter import*
from tkinter import ttk
from tkinter import messagebox
import heapq
import time
import numpy as np
import random
import copy
import sys
import os
from collections import deque
sys.setrecursionlimit(1000000)

class Man:
    x=0
    y=0
    color='red'
    def __init__(self,a,b):
        x=a
        y=b
    def __init__(self):
        x=0
        y=0
    def move(self,dir):
        if(dir=='Up'):
            self.y-=1
        elif(dir=='Down'):
            self.y+=1
        elif(dir=='Left'):
            self.x-=1
        elif(dir=='Right'):
            self.x+=1
        else:
            print('error!')
class Map:
    map=[]
    map2=[]
    mwsize=50#地图长度
    mhsize=50#地图高度
    ww=1600#窗口长度
    wh=900#窗口高度
    bcolor='blue'#画布背景颜色
    kcolor='yellow'#墙颜色
    file_path=os.getcwd()
    view=Tk()
    canvas=Canvas()
    man=Man()
    man2=Man()
    cbox=ttk.Combobox()
    speedent=Entry()
    speed=0.01#自动搜索速度
    stak=0#路程代价
    isget=0#是否找到终点
    stakstr=StringVar(value='%d'%(stak))
    speedstr=StringVar(value='%.4f'%(speed))
    #选择地图文件
    def cboxfun(self):
        self.getmapfile(self.cbox.get())
    def getmapfile(self,fname):
        size=0
        self.map.clear()
        with open('map\\'+fname,'r') as f:
            line=f.readline()
            while line:
                line=line.strip()
                line=line.split(',')
                self.map.append([])
                self.map[size].extend(line)
                size+=1
                line=f.readline()
        self.mhsize=len(self.map)
        self.mwsize=len(self.map[0])
        self.resetman(self.man)
        self.showmap()
        self.showman(self.man)

    #生成随机地图
    def createanwser(self,x,y,lastdir):#每次随机选择方向并确保宽度搜索
        # global map
        if(x<=0 or x>=len(self.map[0])-1 or y<=0 or y>=len(self.map)-1):
            return
        if(not((self.map[y-1][x]=='1'and self.map[y+1][x]=='1')or(self.map[y][x-1]=='1'and self.map[y][x+1]=='1'))):
            return
        dirs=['up','down','left','right']
        random.shuffle(dirs)
        self.map[y][x]='0'
        for dir in dirs:
            if(dir=='up' and lastdir!='down'):
                self.createanwser(x,y-1,dir)
            elif(dir=='left'and lastdir!='right'):
                self.createanwser(x-1,y,dir)
            elif(dir=='down'and lastdir!='up'):
                self.createanwser(x,y+1,dir)
            elif(dir=='right'and lastdir!='left'):
                self.createanwser(x+1,y,dir)
            else:
                continue
    def createrandommap(self):
        # global map
        self.map.clear()
        for i in range(self.mhsize):
            self.map.append([])
            for j in range(self.mwsize):
                self.map[i].append('1')
        #确定起点
        x=0
        y=0
        tx=0
        ty=0
        t=random.choice([0,1])
        if(t):
            x=random.choice([0,self.mwsize-1])
            y=random.randint(1,self.mhsize-2)
            if(x==0):
                tx=x+1
            else:
                tx=x-1
            ty=y
        else:
            x=random.randint(1,self.mwsize-2)
            y=random.choice([0,self.mhsize-1])
            if(y==0):
                ty=y+1
            else:
                ty=y-1
            tx=x
        self.map[y][x]='@'
        #生成道路
        self.createanwser(tx,ty,'')
        #选取终点（不与起点重合且有通道能抵达）
        while(self.map[y][x]=='@'or(self.map[ty][tx]=='1')): 
            x=0
            y=0
            tx=0
            ty=0
            t=random.choice([0,1])
            if(t):
                x=random.choice([0,self.mwsize-1])
                y=random.randint(1,self.mhsize-2)
                if(x==0):
                    tx=x+1
                else:
                    tx=x-1
                ty=y
            else:
                x=random.randint(1,self.mwsize-2)
                y=random.choice([0,self.mhsize-1])
                if(y==0):
                    ty=y+1
                else:
                    ty=y-1
                tx=x
        self.map[y][x]='$'
        #生成地图文件
        fmap=[]
        for i in range(len(self.map)):
            fmap.append([])
            for j in self.map[i]:
                fmap[i].append(j)
                fmap[i].append(',')
            fmap[i].pop()
        # for i in fmap:
        #     for j in i:
        #         print(j,end=' ')
        #     print()
        self.file_path=os.getcwd()
        with open ('test.map','w') as f:
            for i in fmap:
                for j in i:
                    f.write(j)
                f.write('\n')
        file_list=os.listdir(self.file_path)
        if('map' not in file_list):
            os.mkdir('map')
        num_map=len(os.listdir(self.file_path+'\map'))
        os.rename('test.map','map\map%d.map'%(num_map))
        self.resetman(self.man)
        self.showmap()
        self.showman(self.man)
        self.cbox['value']=os.listdir(self.file_path+'\map')

    #自动深度优先搜索
    def audfs(self):
        self.view.unbind('<Key>')
        self.isget=0
        self.stak=0
        self.map2.clear()
        self.map2=copy.deepcopy(self.map)
        self.man2=copy.deepcopy(self.man)
        self.af(self.man2.x,self.man2.y)
        self.showman(self.man)
        self.view.bind('<Key>',self.moveman)
    def af(self,x,y):
        if(self.isget):
            return
        if(x<0 or x>len(self.map[0])-1 or y<0 or y>len(self.map)-1):
            return
        if(self.map2[y][x]=='1'):
            return
        if(self.map2[y][x]=='$'):
            messagebox.showinfo(' ','到达终点')
            self.isget=1
            return
        self.stak+=1
        self.showstak()
        self.man2.x,self.man2.y=x,y
        self.showman(self.man2)
        self.view.update()
        time.sleep(self.speed)
        self.map2[y][x]='1'
        dirs=['Up','Right','Down','Left']
        for dir in dirs:
            if(dir=='Up'):
                self.af(x,y-1)
            elif(dir=='Left'):
                self.af(x-1,y)
            elif(dir=='Down'):
                self.af(x,y+1)
            elif(dir=='Right'):
                self.af(x+1,y)
            else:
                continue
        self.stak-=1
        self.showstak()
        self.imshow(x,y)
    #显示路程代价与stak变化绑定
    def showstak(self):
        self.stakstr.set(f'{self.stak}')

    #自动宽度优先搜索
    def aubfs(self):
        self.view.unbind('<Key>')
        self.isget=0
        self.stak=0
        self.map2.clear()
        self.map2=copy.deepcopy(self.map)
        self.man2=copy.deepcopy(self.man)
        dirs=[(0,-1),(1,0),(0,1),(-1,0)]

        que=deque([(self.man2.x,self.man2.y,0)])
        parent={(self.man2.x,self.man2.y):None} #回溯显示最终路径
        self.map2[self.man2.y][self.man2.x]='1'
        while que:
            current=que.popleft()
            x,y,z=current
            self.stak=z#路径耗散相当于bfs的深度
            self.showstak()
            self.man2.x,self.man2.y=x,y
            self.showman(self.man2)
            self.view.update()
            time.sleep(self.speed)
            if(self.map[y][x]=='$'):
                self.canvas.delete(all)
                self.showmap()
                self.showman(self.man2)
                cur=(x,y)
                cur=parent[cur]
                while cur is not None:
                    #显示最终路径
                    self.man2.x,self.man2.y=cur
                    self.showman(self.man2)
                    cur=parent[cur]
                    
                messagebox.showinfo(' ','到达终点')
                self.isget=1
                break
            for dir in dirs:
                nx,ny=x+dir[0],y+dir[1]
                nz=z+1
                if(self.isvalid(nx,ny)):
                    parent[(nx,ny)]=(x,y)
                    que.append((nx,ny,nz))#子节点的坐标和深度一起压入队列
                    self.map2[ny][nx]='1'
        self.canvas.delete(all)
        self.stak=0
        self.showstak()
        self.showmap()
        self.showman(self.man)
        self.view.bind('<Key>',self.moveman)
        return
    def isvalid(self,x,y):
        if(self.isget):
            return False
        if(x<0 or x>len(self.map[0])-1 or y<0 or y>len(self.map)-1):
            return False
        if(self.map2[y][x]=='1'):
            return False
        return True
        

    #一致代价
    def auyizhi(self):
        #初始化
        self.view.unbind('<Key>')
        self.isget=0
        self.stak=0
        self.map2.clear()
        self.map2=copy.deepcopy(self.map)
        self.man2=copy.deepcopy(self.man)
        
        start=(self.man.x,self.man.y)
        que=[]
        heapq.heappush(que,(0,start))
        costs={start:0}
        parent={start:None}
        dirs=[(0,-1),(1,0),(0,1),(-1,0)]
        while que:
            ccost,cnode=heapq.heappop(que)
            self.map2[cnode[1]][cnode[0]]='1'
            self.man2.x,self.man2.y=cnode[0],cnode[1]
            self.stak=ccost
            self.showstak()
            self.showman(self.man2)
            self.view.update()
            time.sleep(self.speed)
            if(self.map[cnode[1]][cnode[0]]=='$'):
                self.canvas.delete(all)
                self.showmap()
                self.showman(self.man2)
                cur=(self.man2.x,self.man2.y)
                cur=parent[cur]
                while cur is not None:
                    #显示最终路径
                    self.man2.x,self.man2.y=cur
                    self.showman(self.man2)
                    cur=parent[cur]
                messagebox.showinfo(' ','到达终点')
                self.isget=1
                break
            for dir in dirs:
                neib=(cnode[0]+dir[0],cnode[1]+dir[1])
                if(self.isvalid(neib[0],neib[1])):
                    newcost=ccost+1
                    if(neib not in costs or newcost<costs[neib]):
                        costs[neib]=newcost
                        heapq.heappush(que,(newcost,neib))
                        parent[neib]=cnode

        self.canvas.delete(all)
        self.stak=0
        self.showstak()
        self.showmap()
        self.showman(self.man)
        self.view.bind('<Key>',self.moveman)
        return
        
    #贪心
    def autanxin(self):
        self.view.unbind('<Key>')
        self.isget=0
        self.stak=0
        self.map2.clear()
        self.map2=copy.deepcopy(self.map)
        self.man2=copy.deepcopy(self.man)
        #获取终点坐标
        endx,endy=0,0
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if(self.map[i][j]=='$'):
                    endx,endy=j,i

        start=(self.man.x,self.man.y)
        que=[]
        heapq.heappush(que,(0,start,0))
        costs={start:0}
        parent={start:None}
        dirs=[(0,-1),(1,0),(0,1),(-1,0)]
        while que:
            ccost,cnode,st=heapq.heappop(que)
            self.map2[cnode[1]][cnode[0]]='1'
            self.man2.x,self.man2.y=cnode[0],cnode[1]
            self.stak=st
            self.showstak()
            self.showman(self.man2)
            self.view.update()
            time.sleep(self.speed)
            if(self.map[cnode[1]][cnode[0]]=='$'):
                self.canvas.delete(all)
                self.showmap()
                self.showman(self.man2)
                cur=(self.man2.x,self.man2.y)
                cur=parent[cur]
                while cur is not None:
                    #显示最终路径
                    self.man2.x,self.man2.y=cur
                    self.showman(self.man2)
                    cur=parent[cur]
                messagebox.showinfo(' ','到达终点')
                self.isget=1
                break
            for dir in dirs:
                neib=(cnode[0]+dir[0],cnode[1]+dir[1])
                if(self.isvalid(neib[0],neib[1])):
                    newcost=abs(endx-neib[0])+abs(endy-neib[1])
                    if(neib not in costs or newcost<costs[neib]):
                        costs[neib]=newcost
                        heapq.heappush(que,(newcost,neib,st+1))
                        parent[neib]=cnode

        self.canvas.delete(all)
        self.stak=0
        self.showstak()
        self.showmap()
        self.showman(self.man)
        self.view.bind('<Key>',self.moveman)
        return
    #A*搜索
    def auas(self):
        self.view.unbind('<Key>')
        self.isget=0
        self.stak=0
        self.map2.clear()
        self.map2=copy.deepcopy(self.map) 
        self.man2=copy.deepcopy(self.man)
        #获取终点坐标
        endx,endy=0,0
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if(self.map[i][j]=='$'):
                    endx,endy=j,i

        start=(self.man.x,self.man.y)
        que=[]
        heapq.heappush(que,(0,0,start,0))
        parent={start:None}
        dirs=[(0,-1),(1,0),(0,1),(-1,0)]
        while que:
            cfn,ccost,cnode,st=heapq.heappop(que)
            self.map2[cnode[1]][cnode[0]]='1'
            self.man2.x,self.man2.y=cnode[0],cnode[1]
            self.stak=st
            self.showstak()
            self.showman(self.man2)
            self.view.update()
            time.sleep(self.speed)
            if(self.map[cnode[1]][cnode[0]]=='$'):
                self.canvas.delete(all)
                self.showmap()
                self.showman(self.man2)
                cur=(self.man2.x,self.man2.y)
                cur=parent[cur]
                while cur is not None:
                    #显示最终路径
                    self.man2.x,self.man2.y=cur
                    self.showman(self.man2)
                    cur=parent[cur]
                messagebox.showinfo(' ','到达终点')
                self.isget=1
                break
            
            for dir in dirs:
                neib=(cnode[0]+dir[0],cnode[1]+dir[1])
                if(self.isvalid(neib[0],neib[1])):
                    newcost=abs(endx-neib[0])+abs(endy-neib[1])
                    fn=newcost+st
                    heapq.heappush(que,(fn,newcost,neib,st+1))
                    parent[neib]=cnode
            

        self.canvas.delete(all)
        self.stak=0
        self.showstak()
        self.showmap()
        self.showman(self.man)
        self.view.bind('<Key>',self.moveman)
        return
    def fcbox(self,event):
        self.canvas.focus_force()
    #窗口
    def show(self):
        #初始化
        # self.createrandommap()
        file_list1=os.listdir(self.file_path)
        if('map' not in file_list1):
            os.mkdir('map')
        file_list2=os.listdir(self.file_path+'\map')
        if(len(file_list2)==0):
            self.createrandommap()
            file_list2=os.listdir(self.file_path+'\map')
        self.getmapfile(file_list2[0])
        self.meu=LabelFrame(self.view,height=self.wh,width=self.ww)
        self.meu.pack(side='left',fill=X)
        button1=Button(self.meu,text="生成地图",command=self.createrandommap).grid(column=0,row=0)
        button2=Button(self.meu,text='打开地图',command=self.cboxfun).grid(column=0,row=1)
        self.cbox=ttk.Combobox(self.meu)
        self.cbox['state']='readonly'
        self.cbox['value']=os.listdir(self.file_path+'\map')
        self.cbox.current(0)
        self.cbox.grid(column=1,row=1)
        self.cbox.bind('<<ComboboxSelected>>',self.fcbox)
        button3=Button(self.meu,text='深度优先',command=self.audfs).grid(column=0,row=2)
        button4=Button(self.meu,text='宽度优先',command=self.aubfs).grid(column=0,row=3)
        button5=Button(self.meu,text='一致代价',command=self.auyizhi).grid(column=0,row=4)
        button6=Button(self.meu,text='贪心搜索',command=self.autanxin).grid(column=0,row=5)
        button7=Button(self.meu,text='A*搜索',command=self.auas).grid(column=0,row=6)
        
        self.speedent=Entry(self.meu,textvariable=self.speedstr).grid(column=1,row=7)
        self.label1=Button(self.meu,text='变速',command=self.changespeed).grid(column=0,row=7)
        Label(self.meu,text='路程消耗: ').grid(column=0,row=8)
        self.label2=Label(self.meu,textvariable=self.stakstr).grid(column=1,row=8)
        sw=self.view.winfo_screenwidth()
        sh=self.view.winfo_screenheight()
        sw=(sw-self.ww)/2
        sh=(sh-self.wh)/2
        self.view.title('四通八达迷宫')
        self.view.geometry('%dx%d+%d+%d' % (self.ww,self.wh,sw,sh))
        self.label2=LabelFrame(self.view,height=self.wh,width=self.ww/4*3)
        self.label2.pack(side='left')
        self.canvas=Canvas(self.label2,bg=self.bcolor,height=self.wh,width=self.ww/4*3)
        self.view.resizable(0,0)
        #显示
        self.showmap()
        self.showman(self.man)
        self.label2.bind('<Motion>',self.label2.focus_get)
        self.view.bind('<Key>',self.moveman)
        self.canvas.pack(side='left')                       
        self.view.mainloop()
   #改变自动搜索速度
    def changespeed(self):
        self.speed=float(self.speedstr.get())
        self.speedstr.set('%.4f'%(self.speed))
        self.canvas.focus_force()
        return
    
    def showmap(self):
        mh=self.wh/len(self.map)
        mw=self.ww/4*3/len(self.map[0])
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if(self.map[i][j]=='1'):
                    self.canvas.create_rectangle(j*mw,(i)*mh,(j+1)*mw,(i+1)*mh,fill=self.kcolor,outline=self.kcolor)
                elif(self.map[i][j]=='@'):
                    self.canvas.create_rectangle(j*mw,(i)*mh,(j+1)*mw,(i+1)*mh,fill='white',outline=self.kcolor)
                elif(self.map[i][j]=='$'):
                    self.canvas.create_rectangle(j*mw,(i)*mh,(j+1)*mw,(i+1)*mh,fill='green',outline=self.kcolor)
                elif(self.map[i][j]=='0'):
                    self.canvas.create_rectangle(j*mw,(i)*mh,(j+1)*mw,(i+1)*mh,fill=self.bcolor,outline=self.bcolor)
    def showman(self,man):
        mh=self.wh/len(self.map)
        mw=self.ww/4*3/len(self.map[0])
        self.canvas.create_rectangle(man.x*mw,(man.y)*mh,(man.x+1)*mw,(man.y+1)*mh,fill=man.color,outline=man.color)
    def resetman(self,man):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if(self.map[i][j]=='@'):
                    man.y=i
                    man.x=j

    def moveman(self,event):
        dir=event.keysym
        tx=0
        ty=0
        tx=self.man.x
        ty=self.man.y
        if(dir=='Up'):
            ty-=1
        elif(dir=='Down'):
            ty+=1
        elif(dir=='Left'):
            tx-=1
        elif(dir=='Right'):
            tx+=1
        if(tx>=0 and tx<len(self.map[0]) and ty>=0 and ty<len(self.map) and self.map[ty][tx]!='1'):
            self.imshowman(self.man)
            self.man.move(event.keysym)
            self.showman(self.man)
        if(self.map[self.man.y][self.man.x]=='$'):
            messagebox.showinfo(' ','到达终点')
    def imshowman(self,man):
        mh=self.wh/len(self.map)
        mw=self.ww/4*3/len(self.map[0])
        color=self.bcolor
        if(self.map[man.y][man.x]=='$'):
            color='green'
        self.canvas.create_rectangle(man.x*mw,(man.y)*mh,(man.x+1)*mw,(man.y+1)*mh,fill=color,outline=color)
    def imshow(self,x,y):
        mh=self.wh/len(self.map)
        mw=self.ww/4*3/len(self.map[0])
        color=self.bcolor
        if(self.map[y][x]=='$'):
            color='green'
        self.canvas.create_rectangle(x*mw,(y)*mh,(x+1)*mw,(y+1)*mh,fill=color,outline=color)


m=Map()
m.show()