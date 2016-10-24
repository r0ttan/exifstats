import exifread, json, os, glob

# list of desired image information keys (EXIF tags)
mytags = ['EXIF ApertureValue', 'EXIF FNumber', 'Image Software',
          'Image Model', 'Image Orientation', 'EXIF MeteringMode',
          'EXIF Flash', 'EXIF ISOSpeedRatings', 'EXIF ExposureTime',
          'EXIF ExposureMode',
          'EXIF FocalLength', 'EXIF ExposureProgram']

def exifbatch(path, sufflst, statsd):
    '''
    param path = path to image dir
    param pathlist = list of absolute pathnames
    param tagset = set of unique exif tags
    param statsd = empty dictionary to store statistics
    '''
    
    ignore=[]#'JPEGThumbnail', 'EXIF UserComment', 'MakerNote Tag 0x4015', 'Image Tag 0xC715', 'Image Tag 0xC7A7',
            #'Image Tag 0xC65D', 'Image Tag 0xC621', 'Image Tag 0xC719', 'Image Tag 0xC714', 'MakerNote Tag 0x0099',
            #'MakerNote Tag 0x4011', 'MakerNote Tag 0x00E0', 'MakerNote Tag 0x4019', 'MakerNote Tag 0x00A0',
            #'MakerNote Tag 0x0003', 'MakerNote Tag 0x00A0', 'Image Tag 0xC622', 'Image Tag 0xC623', 'Image Tag 0xC624',
            #'MakerNote Tag 0x4013', 'MakerNote Tag 0x00AA', 'MakerNote MultiExposure', 'MakerNote Tag 0x0035',
            #'MakerNote Tag 0x4016', 'MakerNote MultiExposure', 'IFD 2 Tag 0xC5D9', 'Image Copyright', 'EXIF FocalPlaneXResolution',
            #'MakerNote Tag 0x4001', 'Image Tag 0xC634', 'MakerNote Tag 0x0004', 'MakerNote Tag 0x4010', 'MakerNote LensData',
            #'Image Tag 0xC62A', 'MakerNote Tag 0x0019', 'MakerNote Tag 0x00A3', 'Thumbnail JPEGInterchangeFormat',
            #'IFD 3 Tag 0xC5D8', 'Image Tag 0x9216', 'Image Tag 0xC62F', 'IFD 2 Tag 0xC6DC', 'MakerNote Tag 0x4012',
            #'Image Tag 0xC628', 'MakerNote ThumbnailImageValidArea', 'MakerNote Tag 0x4009', 'IFD 2 ImageLength',
            #'MakerNote Tag 0x0007', 'MakerNote Tag 0x0005', 'Image Tag 0xC717', 'MakerNote FlashInfo', 'Image Tag 0xC613',
            #'MakerNote Tag 0x4018', 'Image Tag 0xC6FD', 'Image Tag 0xC627', 'MakerNote ShotInfo', 'MakerNote Tag 0x4005',
            #'Image Tag 0xC614', 'Image StripByteCounts', 'EXIF MakerNote', 'Image Tag 0xC68B', 'Image Tag 0xC630',
            #'Image Tag 0xC71B', 'IFD 3 Tag 0xC5E0', 'MakerNote Tag 0x00A4', 'Image Tag 0x000B', 'IFD 3 Tag 0xC640',
            #'Image Tag 0xC633', 'MakerNote ImageType', 'IFD 3 Tag 0xC6C5', 'MakerNote Tag 0x00D0', 'IFD 2 StripByteCounts',
            #'Image Tag 0xC62B', 'IFD 2 Tag 0xC6C5', 'Image Tag 0xC62E', 'EXIF ImageUniqueID', 'MakerNote Tag 0x4008',
            #'Image StripOffsets', 'Image Tag 0xC62C', 'MakerNote AutoFlashMode', 'Image Tag 0x014A', 'MakerNote Tag 0x0083',
            #'Image GPSInfo', 'Image Tag 0xC6FE', 'MakerNote Tag 0x0008', 'Image Tag 0xC6F4', 'Image ExifOffset', 'Image Tag 0xC71A',
            #'Image Tag 0xC6F3', 'IFD 3 StripOffsets', 'MakerNote AFInfo2', 'MakerNote Tag 0x002C', 'MakerNote WorldTime',
            #'Image ImageWidth', 'Image Tag 0x9211', 'EXIF LensSerialNumber', 'Image Tag 0xC725', 'MakerNote FlashSetting',
            #'Image Tag 0xC65A', 'EXIF SubSecTime', 'IFD 2 StripOffsets', 'MakerNote FileNumber', 'IFD 3 StripByteCounts',
            #'Thumbnail JPEGInterchangeFormatLength', 'EXIF CVAPattern', 'GPS GPSVersionID', 'IFD 2 ImageWidth',
            #'Image Tag 0xC612', 'Image Tag 0xC65B', 'Image Tag 0xC6F8', 'Image Tag 0xC716', 'MakerNote NEFCurve1',
            #'MakerNote NEFCurve2', 'MakerNote Tag 0x0001', 'MakerNote Tag 0x0006', 'MakerNote Tag 0x000E', 'MakerNote Tag 0x0014',
            #'MakerNote Tag 0x002A', 'MakerNote Tag 0x002B', 'MakerNote Tag 0x003B', 'MakerNote Tag 0x003C', 'MakerNote Tag 0x003D',
            #'MakerNote Tag 0x003E', 'MakerNote Tag 0x003F', 'MakerNote Tag 0x0040', 'MakerNote Tag 0x0042', 'MakerNote Tag 0x00BA',
            #'MakerNote Tag 0x00BB', 'MakerNote Tag 0x00BC', 'MakerNote Tag 0x00BF', 'MakerNote Tag 0x00C0', 'MakerNote Tag 0x4002',
            #'MakerNote Tag 0x4017', 'MakerNote TotalShutterReleases', 'GPS GPSDOP', 'GPS GPSAltitudeRef', 'GPS GPSAltitude',
            #'GPS GPSLongitude', 'GPS GPSMeasureMode', 'Image PrintIM', 'Interoperability InteroperabilityVersion',
            #'GPS GPSTimeStamp', 'GPS GPSTrackRef', 'GPS GPSSpeedRef', 'GPS GPSLatitudeRef', 'GPS GPSDate', 'GPS GPSLatitude',
            #'MakerNote LightingType', 'GPS GPSDestBearing', 'GPS GPSLongitudeRef', 'EXIF SubSecTimeDigitized', 'MakerNote VRInfo',
            #'GPS GPSImgDirectionRef', 'MakerNote Tag 0x62D9', 'MakerNote Tag 0xDBFF', 'MakerNote Tag 0x5EFF', 'MakerNote Tag 0x4630',
            #'MakerNote Tag 0x391A', 'MakerNote Tag 0x0200', 'GPS GPSDestBearingRef', 'MakerNote Tag 0x1F00', 'Thumbnail YResolution',
            #'MakerNote Tag 0x0000', 'GPS GPSImgDirection', 'EXIF SubSecTimeOriginal', 'MakerNote Tag 0x5AFF', 'MakerNote Tag 0x0AF2',
            #'MakerNote ColorBalance', 'GPS GPSSpeed', 'MakerNote Tag 0x2FFF', 'EXIF BrightnessValue', 'MakerNote Tag 0x0708',
            #'Thumbnail XResolution', 'GPS Tag 0x001F', 'Image Tag 0xC635', 'MakerNote Tag 0x0111', 'MakerNote Tag 0x0800',
            #'MakerNote Tag 0xA5FF', 'MakerNote Tag 0x0122']
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
            for ig in ignore:
                tags.pop(ig, None)   #in an early version the result was stripped from unwanted tags already here, could be removed?
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

#this was for early testing
imagelist = [r"C:\Some\Images\PythonProjects\exifstat\sampleimg\HUD_7H7A9886DG.jpg",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\Hud_PN.jpg",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\Porträtt_PN.jpg",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\HUD_PÖpg.jpg",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\hud_SN.jpg",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\HUD_0163TG.jpg",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\IMG_8836 (1).CR2",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\IMG_8834.dng",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\DSC_0614.NEF",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\DSC_0615.NEF",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\DSC_0616.NEF",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\DSC_0617.NEF",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\DSC_0618.NEF",
             r"C:\Some\Images\PythonProjects\exifstat\sampleimg\DSC_0452.NEF"]
suff=['NEF', 'CR2', 'dng', 'jpg']   #raw file types currently tested
imgp = 'C:\\Users\\Tobias\\PythonProjects\\exifstat\\sampleimg\\'
imgp2 = 'C:\\Some\\Images\\Pictures\\20150411'
imgp3 = 'C:\\Some\\Images\\Pictures\\hammock\\hammock'
imgp4 = 'C:\\Some\\Images\\Pictures\\'
imgp5 = r'C:\Users\Tobias\Dropbox\Photos\fotomara16'
#print(listimg(imgp4, suff))
exifset = set()
statis={}  #empty dictionary to be populated by exifbatch
print("NrofFiles: ", exifbatch(imgp5, suff, statis))
#print("Length of tagset = {}".format(len(exifset)))
print("Length of statis = {}".format(len(statis)))
#storestat(statis)
#presdic={x:v for x, v in statis.items() if x in mytags}
presdic = filtertag(mytags, statis)
#print(presdic)
for p,v in presdic.items():
    sv = sortexif(v)
    print(p, end=" : ")
    for s in sv:
        print(s, end=",")
    print()
#d = {"aa": 3, "bb": 4, "cc": 2, "dd": 1}
#print(sortexif(d))
#for entry in presdic.items():
#    print(entry)
