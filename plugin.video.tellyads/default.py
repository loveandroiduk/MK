import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os

addon_id = 'plugin.video.tellyads'
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
art = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/', ''))
base = 'http://www.tellyads.com/'


def INDEX():
        addDir('Most Recent','http://www.tellyads.com/recent_additions/',1,icon,fanart)
        addDir('Top 20 Ads Of The Decade','http://www.tellyads.com/ad_of_the_decade/',1,icon,fanart)
        addDir('A-Z Recent Adverts','recent',3,icon,fanart)
        addDir('A-Z Vintage Adverts','vintage',3,icon,fanart)
        addDir('Search','http://www.tellyads.com/search/?q=',4,icon,fanart)
                
def GETADS(url):
        link = open_url(url)
        link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
        match=re.compile('<li class="advert"><a href="\.\./(.+?)"><img src="(.+?)" width=".+?" height=".+?"/><p>(.+?) <span class="info">(.+?)</span></p></a></li>').findall(link)
        for url,iconimage,name,info in match:
                url = base+url
                url=url.replace(' ','%20')
                addLink(name,url,2,iconimage,fanart)
        try:
                nextpage=re.compile("<li class='page'><a href='(.+?)'>Next</a>").findall(link)[0]
                nextpage=nextpage.split('href')[-1].replace('..','').replace("='","")
                nextpage=base+nextpage
                addDir('Next Page >>',nextpage,1,icon,fanart)
        except: pass
        
def AZ(url):
        link = open_url(base)
        match=re.compile('<li><a href="(.+?)">(.+?)</a></li>').findall(link)
        for azurl, name in match:
                azurl = base+azurl
                if url in azurl:
                        name=name.replace('<span style="color:#00DD45;">','').replace('</span>','')
                        addDir(name,azurl,1,icon,fanart)
                          
def SEARCH():
        search_entered =''
        keyboard = xbmc.Keyboard(search_entered, 'Search Ads')
        keyboard.doModal()
        if keyboard.isConfirmed():
                search_entered = keyboard.getText().replace(' ','+')
        if search_entered == None or len(search_entered)<1:
                quit()
        else:
                url = 'http://www.tellyads.com/search/?q='+ search_entered
                GETADS(url)
        

def PLAYADS(name,url):
        link = open_url(url)
        flv=re.compile("\&file=(.+?)\&").findall(link)[0]
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=icon,thumbnailImage=icon); liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        xbmc.Player ().play(flv, liz, False)
        
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

def addDir(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setProperty('fanart_image', fanart)

        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
        
def open_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if ADDON2.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON2.getSetting(viewType) )

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

if mode==None or url==None or len(url)<1: INDEX()
elif mode==1: GETADS(url)
elif mode==2: PLAYADS(name,url)
elif mode==3: AZ(url)
elif mode==4: SEARCH()
xbmcplugin.endOfDirectory(int(sys.argv[1]))

