import xbmc,xbmcaddon,xbmcgui,xbmcplugin,urllib,urllib2,os,re,sys,urlresolver,random
from resources.libs.common_addon import Addon

addon_id        = 'plugin.video.speedway'
selfAddon       = xbmcaddon.Addon(id=addon_id)
addon           = Addon(addon_id, sys.argv)
fanart          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon            = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))

def Index():
        xbmc.Player().play('http://metalkettle.co/Speedway/INFO%20MOVIE.mp4')
        link=open_url('http://metalkettle.co/Speedway/Index.txt')	
	match=re.compile('<title>(.+?)</title>.+?url>(.+?)</url>.+?thumb>(.+?)</thumb>',re.DOTALL).findall(link)
	for name,url,iconimage in match:
                name = name.replace(' - ',' ')
                iconimage = iconimage.replace(' ','%20') 
                url = url.replace(' ','%20')
                addDir(name,url,1,iconimage,fanart)
        addLink('[COLOR blue][B]News[/COLOR][/B]','http://metalkettle.co/Speedway/NEWS.txt',4,icon,fanart)
        addLink('[COLOR blue][B]Twitter Feed[/COLOR][/B]','url',2,icon,fanart)
        addLink('[COLOR blue][B]Upcoming Live TV Coverage Information[/COLOR][/B]','http://metalkettle.co/Speedway/COVERAGE_INFO.txt',4,icon,fanart)

        
def Coverage(url,name):
        text = open_url(url)
        showText(name, text)

        
def GetChans(url):
        if 'Index' in url:
                CatIndex(url)
        else:
                link=open_url(url)
                match=re.compile('<title>(.+?)</title>.+?url>(.+?)</url>.+?thumb>(.+?)</thumb>',re.DOTALL).findall(link)
                print match
                for name,url,iconimage in match:
                        name = name.replace(' - ',' ')
                        iconimage = iconimage.replace(' ','%20') 
                        url = url.replace(' ','%20')
                        if 'Parts' in url:
                                addDir(name,url,1,iconimage,fanart)
                        else:
                                addLink(name,url,3,iconimage,fanart)
        
def CatIndex(url):
        link=open_url(url)	
	match=re.compile('<title>(.+?)</title>.+?url>(.+?)</url>.+?thumb>(.+?)</thumb>',re.DOTALL).findall(link)
	for name,url,iconimage in match:
                name = name.replace(' - ',' ')
                iconimage = iconimage.replace(' ','%20') 
                url = url.replace(' ','%20')
                addDir(name,url,1,iconimage,fanart)

def PLAYLINK(url):
            xbmc.Player ().play(urlresolver.HostedMediaFile(url).resolve())
         
def open_url(url):
        url += '?%d=%d' % (random.randint(1, 10000), random.randint(1, 10000))
        print url
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        link = link.replace('\r','').replace('\t','').replace('&nbsp;','').replace('\'','')
        response.close()
        return link

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                               
        return param

def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def showText(heading, text):
    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass

def twitter():
        text = ''
        twit = 'https://script.google.com/macros/s/AKfycbyBcUa5TlEQudk6Y_0o0ZubnmhGL_-b7Up8kQt11xgVwz3ErTo/exec?625794194884444160'
        link = open_url(twit)
        link = link.replace('/n','')
        link = link.decode('utf-8').encode('utf-8').replace('&#39;','\'').replace('&#10;',' - ').replace('&#x2026;','')
        match=re.compile("<title>(.+?)</title>.+?<pubDate>(.+?)</pubDate>",re.DOTALL).findall(link)[1:]
        for status, dte in match:
            dte = dte[:-15]
            dte = '[COLOR blue][B]'+dte+'[/B][/COLOR]'
            text = text+dte+'\n'+status+'\n'+'\n'
        showText('[COLOR blue][B]@SpeedwayPortal[/B][/COLOR]', text)

               
def addDir(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

params=get_params(); url=None; name=None; mode=None; site=None; iconimage=None
try: site=urllib.unquote_plus(params["site"])
except: pass
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
 
print "Site: "+str(site); print "Mode: "+str(mode); print "URL: "+str(url); print "Name: "+str(name)
 
if mode==None or url==None or len(url)<1: Index()
elif mode==1:GetChans(url)
elif mode==2:twitter()
elif mode==3:PLAYLINK(url)
elif mode==4:Coverage(url,name)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
