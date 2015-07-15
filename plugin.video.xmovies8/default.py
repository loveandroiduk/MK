import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os,random,urlparse,time,net
from t0mm0.common.addon import Addon
from metahandler import metahandlers
net = net.Net()

addon_id = 'plugin.video.xmovies8'
selfAddon = xbmcaddon.Addon(id=addon_id)
datapath= xbmc.translatePath(selfAddon.getAddonInfo('profile'))
metaget = metahandlers.MetaData(preparezip=False)
addon = Addon(addon_id, sys.argv)
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
metaset = selfAddon.getSetting('enable_meta')

def CATEGORIES():
        addDir2('Cinema Movies','http://megashare9.tv/tag/hotnew/',1,icon,'',fanart)
        addDir2('New Movies','http://megashare9.tv/author/T9611412/',1,icon,'',fanart)
        addDir2('HD Movies','http://megashare9.tv/movie-quality/hd/',1,icon,'',fanart)
        addDir2('Movies By Year','http://megashare9.tv/',2,icon,'',fanart)
        addDir2('Movies By Genre','http://megashare9.tv/',4,icon,'',fanart)
        addDir2('Search','URL',3,icon,'',fanart)     
        xbmc.executebuiltin('Container.SetViewMode(50)')
        
def GETYEARS(url):
        link = open_url(url)
        link=link.replace('\n','').replace('  ','')
        match=re.compile('href="(.+?)">(.+?)</a></li>').findall(link)
        addDir2('2015','http://megashare9.tv/category/2015/',1,icon,'',fanart)
        for url,name in match:              
                if 'category' in url:addDir2(name,url,1,icon,'',fanart)
        xbmc.executebuiltin('Container.SetViewMode(50)')
                
def GETGENRES(url):                  
        link = open_url(url)
        link=link.replace('\n','').replace('  ','')
        match=re.compile('<li class="cat-item cat-item-.+?"><a href="(.+?)" >(.+?)</a>').findall(link)
        for url,name in match:
                if 'game-show' in name:name = 'Game Show'
                if 'genre' in url:addDir2(name,url,1,icon,'',fanart)
        xbmc.executebuiltin('Container.SetViewMode(50)')

def SEARCH():
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, 'Search Xmovies8')
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','+')
    if len(search_entered)>1:
        url = 'http://megashare9.tv/?s='+ search_entered
        link = open_url(url)
        match=re.compile('<h2><a href="(.+?)">(.+?)</a></h2>').findall(link)
        for url,name in match:
             addDir(name,url,100,'',len(match))
        if metaset=='true':
                setView('movies', 'MAIN')
        else: xbmc.executebuiltin('Container.SetViewMode(50)') 

def GETMOVIES(url,name):
        link = open_url(url)
        link=link.replace('\n','').replace('  ','')
        match=re.compile('<a class="thumbnail darken video" title="(.+?)" href="(.+?)">',re.DOTALL).findall(link)
        if len(match)>0:
                items = len(match)
                for name,url in match:
                        name2 = name.encode('ascii', 'ignore')
                        if not 'SEASON' in name2:
                             if not 'Season' in name2:   
                                if not 'nofollow' in name2:
                                        addDir(name2,url,100,'',len(match))
        if len(match)<1:
                match=re.compile('<a class="thumbnail darken video" href="(.+?)" title="(.+?)">',re.DOTALL).findall(link)
                items = len(match)
                for url,name in match:
                        name2 = name.decode("ascii", "ignore").encode("ascii")
                        if not 'Season' in name2:
                                if not 'SEASON' in name2:
                                        addDir(name2,url,100,'',len(match))
        try:
                match=re.compile('link rel="next" href="(.+?)"').findall(link)
                url= match[0]
                addDir2('Next Page>>',url,1,icon,'',fanart)
        except: pass
        if metaset=='true':
                setView('movies', 'MAIN')
        else: xbmc.executebuiltin('Container.SetViewMode(50)')

def PLAYLINK(name,url,iconimage):
        link = open_url(url)
        match=re.compile('<a target="_blank"  href="(.+?)" rel="nofollow">.+?.mp4').findall(link)[0]
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=icon,thumbnailImage=icon); liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        xbmc.Player ().play(match, liz, False)

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

def addDir2(name,url,mode,iconimage,description,fanart):
        xbmc.executebuiltin('Container.SetViewMode(50)')
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addDir(name,url,mode,iconimage,itemcount,isFolder=False):
        if metaset=='true':
            splitName=name.partition('(')
            simplename=""
            simpleyear=""
            if len(splitName)>0:
                simplename=splitName[0]
                simpleyear=splitName[2].partition(')')
            if len(simpleyear)>0:
                simpleyear=simpleyear[0]
            meta = metaget.get_meta('movie', simplename ,simpleyear)
            u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&site="+str(site)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
            ok=True
            liz=xbmcgui.ListItem(name, iconImage=meta['cover_url'], thumbnailImage=iconimage)
            liz.setInfo( type="Video", infoLabels= meta )
            contextMenuItems = []
            contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))
            liz.addContextMenuItems(contextMenuItems, replaceItems=True)
            if not meta['backdrop_url'] == '': liz.setProperty('fanart_image', meta['backdrop_url'])
            else: liz.setProperty('fanart_image', fanart)
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder,totalItems=itemcount)
            return ok
        else:
            u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&site="+str(site)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
            ok=True
            liz=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            liz.setInfo( type="Video", infoLabels={ "Title": name } )
            liz.setProperty('fanart_image', fanart)
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
            return ok
        
def open_url(url):
        response = net.http_GET(url).content
        return response

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if selfAddon.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % selfAddon.getSetting(viewType) )

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
print params

if mode==None or url==None or len(url)<1: CATEGORIES()
elif mode==1: GETMOVIES(url,name)
elif mode==2: GETYEARS(url)
elif mode==3: SEARCH()
elif mode==4: GETGENRES(url)
elif mode==100: PLAYLINK(name,url,iconimage)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

