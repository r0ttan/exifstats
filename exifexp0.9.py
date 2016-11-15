import exifread, json, os, glob, argparse

# list of desired image information keys (EXIF tags)
mytags = ['EXIF ApertureValue', 'EXIF FNumber', 'Image Software',
          'Image Model', 'Image Orientation', 'EXIF MeteringMode',
          'EXIF Flash', 'EXIF ISOSpeedRatings', 'EXIF ExposureTime',
          'EXIF ExposureMode', 'EXIF FocalLength',
          'EXIF ExposureProgram', 'EXIF LightSource', 'EXIF WhiteBalance',
          'MakerNote FocusMode', 'MakerNote FlashMode', 'MakerNote Saturation',
          'EXIF FocalLengthIn35mmFilm', 'Image ImageWidth', 'Image ImageLength'
          ]

def exifbatch(path, sufflst, statsd):
    '''
    param path = path to image dir
    param sufflst = file suffix to process
    param statsd = empty dictionary to store statistics
    '''
    ino=0  #store number of images processed
    tno=[]
    sno={}
    pathlist = listimg(path, sufflst)  #build list of image files with suffix [sufflst] in directory [path] 
    workdir = os.getcwd()
    os.chdir(path)
    for i in pathlist:
        print(".", end="")   #just a cheap progress bar
        with open ( os.path.realpath(i), 'rb' ) as fil:
            tags=exifread.process_file(fil) #exifread.proc...returns dictionary
            tags=filtertag(mytags, tags)
            #for ig in ignore:
            #    tags.pop(ig, None)   #in an early version the result was stripped from unwanted tags already here, could be removed?
        stats(tags, statsd)    #tags = dictionary of all images exif info, statsd = empty dictionary to be populated
        ino+=1
    os.chdir(workdir)
    return ino

def stats(allexif, ddic):
    '''
    Build dictionary of dictionaries by adding tags as key from allexif and add value to key:val1
    or if tag already present in ddic just add value,
    or if tag:value already present, just add one to the value
    Return dictionary like {exiftag1:{value1:nrofoccur, value2:nrofoccur, ...}, eiftag2:{...}}
    
    param allexif = dictionary of exif tag:value
    param ddic = dictionary of form exiftag:{tagval:counter, tagval:counter}
    '''
    tagcount=0
    for key, val in allexif.items():
        v=str(val)
        if key not in ddic:
            ddic.setdefault(key)    #add missing exiftag
            ddic[key]={v:1}         #add missing exiftag-value
        elif v not in ddic[key]:
            ddic[key].setdefault(v)  #exiftag present but not corresponding value, add value as key
            ddic[key][v]=1           #add one to key added above
        else:
            ddic[key][v]+=1          #exiftag present, corresponding value present, just add one occurrence
    
def storestat(mydick):
    '''
    Store results on disk. Consider pickle?
    '''
    with open('exifdatastat2.json', 'w') as exfil:
        json.dump(mydick, exfil)
    print("Stored in ", os.getcwd())

def listimg(picpath, suffixlist):
    '''
    param picpath = string representation of path to image dir
    param suffixlist = e.g. ['jpg','png','dng'...]
    '''
    workdir = os.getcwd()
    os.chdir(picpath)
    piclist=[]
    for s in suffixlist:
        rst='**/*.' + s
        piclist.extend(glob.glob(rst, recursive=True))
    os.chdir(workdir)
    return piclist

def filtertag(filterlist, taglist):
    return {x:v for x, v in taglist.items() if x in filterlist}

def readone(path, filename):
    with open (os.path.join(path , filename)) as fil:
               exf=exifread.process_file(fil)
    return exf

def sortexif(mydick):
    sortdic = ((k, mydick[k]) for k in sorted(mydick, key=mydick.get, reverse=True))
    #sortdic = sorted(mydick.items())
    return sortdic
#--------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("imagefolder", help="folder containing images to process, may contain subfolders")
args = parser.parse_args()

suff=['NEF', 'CR2', 'dng', 'jpg']   #raw file types currently tested
exifset = set()
statis={}  #empty dictionary to be populated by exifbatch
print("NrofFiles: ", exifbatch(args.imagefolder, suff, statis))
storestat(statis)
for p,v in statis.items():
    sv = sortexif(v)
    print(p, end=" : ")
    for s in sv:
        print(s, end=",")
    print()
