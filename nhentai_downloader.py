from __future__ import unicode_literals
from threading import Thread, Condition
import queue
import time
import requests
from bs4 import BeautifulSoup
import shutil
import os
import math
import sys
import re
import argparse

class MyThread(Thread):
    def __init__(self, condition, i):
        Thread.__init__(self)
        self.cond = condition
        self.setName("Imgdownload_" + str(i))
        
    def run(self):
        global waitThreadStart, waitThreadEnd
        self.cond.acquire()
        
        print(self.getName() + ' start \n')
        waitThreadStart = waitThreadStart - 1
        time.sleep(0.05)
        self.cond.release()
        flagstate = True
        while (flagstate):
            self.cond.acquire()
            imgLink = threadPool.get()
            self.cond.release()
            
            if id != None:
                
                #self.cond.acquire()
                try:
                    splitName = imgLink.split('/')[-1].split('.')[0]
                    fileName = splitName.zfill(3) + ".jpg"
                    res2 = requests.get(imgLink, stream=True)
                    if res2.status_code is not 200:
                        imgLink = imgLink.replace(".jpg", ".png")
                        fileName = fileName.replace(".jpg", ".png")
                        res2 = requests.get(imgLink, stream=True)
                    if res2.status_code is not 200:
                        imgLink = imgLink.replace(".png", ".bmp")
                        fileName = fileName.replace(".png", ".bmp")
                        res2 = requests.get(imgLink, stream=True)
                    if res2.status_code is not 200:
                        raise Exception("Broke in connect...")
                    #print(res2)
                    #exit()
                    f = open(outputFolder + '/' + subFolder + '/' + fileName, 'wb')
                    shutil.copyfileobj(res2.raw, f)
                    f.close()
                    del res2
                    #print '{0}_{1}'.format(self.getName(), fileName)
                    precentShow = int(50 - (threadPool.qsize() * 50) / imgCount)
                    sys.stdout.write(' ' * 10 + '\r')
                    sys.stdout.flush()
                    sys.stdout.write("|" + " " * (50 - precentShow) + "#" * (precentShow) + "  " + str(precentShow*2) + "%" + '\r')
                    sys.stdout.flush()
                except:
                    print("ERROR Loading: " + splitName)
                    self.cond.acquire()
                    #threadPool.put(imgLink)
                    log_f.write(imgLink + '\n')
                    self.cond.release()
                
                
            #self.cond.release()
            threadPool.task_done()
            if threadPool.empty():
                sys.stdout.write(' ' * 120 + '\r')
                sys.stdout.flush()
                print('end_' + self.getName())
                sys.stdout.write("|" + " " * (50 - precentShow) + "#" * (precentShow) + "  " + str(precentShow*2) + "%" + '\r')
                sys.stdout.flush()
                waitThreadEnd += 1
                flagstate = False
 

parser = argparse.ArgumentParser()
parser.add_argument('--l', default = '0', type = str)
args = parser.parse_args()

total_outer_code = []
total_task = 0
outputFolder = "./output"
logFolder = "./nheitai_log"
threadPool = []

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)
if not os.path.exists(logFolder):
    os.makedirs(logFolder)

log_f = open(logFolder + "/output.log", 'w')

if args.l == "0":
    outer_code = input(">>> Input: ")
    total_outer_code.append(outer_code)
    total_task = len(total_outer_code)

if args.l == "1":
    print("Submit \'e\' to finish building list")
    while(True):
        outer_code = input(">>> Input: ")
        if outer_code == 'e' or outer_code == 'E':
            break
        total_outer_code.append(outer_code)
    total_task = len(total_outer_code)
    print("\nTotal has {} task in list\n".format(total_task))


for i, outer_code in list(enumerate(total_outer_code)):

    start = time.time()
    print("task [{}/{}] starting...".format(i + 1, total_task))

    log_f.write("outer_code: " + outer_code + '\n')
    source_addr = "https://nhentai.net/g/" + str(outer_code)
    #source_addr = "https://i.nhentai.net/galleries/" + source_addr
    #236226
    res = requests.get(source_addr)
    soup = BeautifulSoup(res.text, "html.parser")

    pattern_page = re.compile(r'<span class="name">(.*?)</span></a></span></div><div class="tag-container field-name">')
    pages = int(pattern_page.findall(res.text)[-1])
    print(pages)


    pattern_code = re.compile(r'<img class="lazyload" width="200" height="282" data-src="https://t.nhentai.net/galleries/(.*?)/')
    inter_code = int(pattern_code.findall(res.text)[0])
    print(inter_code)


    pattern_dir = re.compile(r'<h2 class="title">(.*?)</h2>')
    dir_name_set = str(pattern_dir.findall(res.text)[0])
    #print(subFolder)

    subFolder = ""
    pattern_three_name = re.compile(r'>(.*?)</span>')
    three_name = pattern_three_name.findall(dir_name_set)
    for single_name in three_name:
        subFolder += single_name

    print(subFolder)

    subFolder = subFolder.replace('?', '')
    subFolder = subFolder.replace('!', '')
    subFolder = subFolder.replace('*', '')
    subFolder = subFolder.replace('"', '')
    subFolder = subFolder.replace(':', '')
    subFolder = subFolder.replace('/', ' ')
    subFolder = subFolder.replace("	", "")
    #subFolder = subFolder.replace(' ', '_')
    #subFolder = subFolder.replace('.', '')

    #soup.find_all('div', id = 'info')
    # if not os.path.exists(outputFolder):
    #     os.makedirs(outputFolder)

    print("Manga name: " + subFolder)
    if not os.path.exists(outputFolder + '/' + subFolder):
        os.makedirs(outputFolder + '/' + subFolder)

    ThreadCount = 8

    if ThreadCount >= pages:
        ThreadCount = pages

    waitThreadStart = ThreadCount
    waitThreadEnd = 0
    threadPool = queue.Queue(0)
    condition = Condition()

    for count in range(1, pages + 1):
        target_path = "https://i.nhentai.net/galleries/" + str(inter_code) + "/" + str(count) + ".jpg"
        threadPool.put(target_path)

    #exit()

    # subFolder = subFolder.replace('?', '')
    # subFolder = subFolder.replace('!', '')
    # subFolder = subFolder.replace('*', '')
    # subFolder = subFolder.replace('"', '')
    # subFolder = subFolder.replace("| Hitomi.la", '');
    # subFolder = subFolder.replace(' ', '_');
    # subFolder = subFolder.replace('.', '');

    for i in range(1, ThreadCount + 1):
        MyThread(condition, i).start()

    imgCount = pages

    while(waitThreadStart > 0):
        imgCount = imgCount
        
    print ("Find image {:d}.".format(imgCount))
    print ("==========  Start download  ==========")
    threadPool.join()

    while(waitThreadEnd < ThreadCount):
        imgCount = imgCount

    time.sleep(0.05)
    print ("|")
    print ("Complete!")
    print (" " + '\n')
    print ("Total Time: {:.0f} min {:.0f} sec".format( math.floor((time.time() - start)/60), math.floor( (time.time() - start)%60 ) ))