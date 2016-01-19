import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os,shutil,glob,downloader,extract
from resources.libs.common_addon import Addon

addon_id 	= 'plugin.program.oepia'
addon_name  = 'VPN for [COLOR grey]Open[/COLOR][COLOR blue]ELEC[/COLOR]'
selfAddon 	= xbmcaddon.Addon(id=addon_id)
user 		= selfAddon.getSetting('piauser')
passw 		= selfAddon.getSetting('piapass')
testbin		= selfAddon.getSetting('test_bin')
fanart      = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'fanart.jpg'))
icon        = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
pia         = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/PIA/', ''))
ipvanish    = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/IPVanish/', ''))
vypr        = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/Vypr/', ''))
destfol     = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/WorkingFolder', ''))
dialog      = xbmcgui.Dialog()
repoxml 	='/storage/.kodi/addons/repository.unofficial.addon.pro/addon.xml'
openvpnurl 	='/network.openvpn/network.openvpn-6.0.0.zip'
binpath 	='/storage/.kodi/addons/network.openvpn/bin/openvpn'

def Index():
    current_server = selfAddon.getSetting('connected')
    startup_server = selfAddon.getSetting('startup')
    if not startup_server=='':
        selfAddon.setSetting('connected',startup_server)
    addDir('[COLOR white]Setup VPN Provider[/COLOR]','url',9,icon,'',fanart)
    addDir('[COLOR white]Configure VPN Provider[/COLOR]','url',4,icon,'',fanart)
    addLink('[COLOR white]VPN Status[/COLOR]','url',3,icon,'',fanart)

def dlopenvpn():
    if testbin=='true':
        addonurl='http://metalkettle.co/STORAGE/network.openvpn.zip'
    else:
        data = open(repoxml,'r').read()
        datadir=re.compile('<datadir zip="true">(.+?)</datadir>').findall(data)[-1]
        addonurl=datadir+openvpnurl
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create(addon_name,"Downloading required files",'', 'Please Wait...')
    lib=os.path.join(path, 'network.openvpn.zip')
    downloader.download(addonurl, lib, dp)
    addonfolder = xbmc.translatePath(os.path.join('special://home','addons'))
    dp.update(0,"", "Extracting...")
    extract.all(lib,addonfolder,dp)
    os.chmod(binpath, 0o777)
    xbmc.executebuiltin('UpdateLocalAddons')

def providers():
    addLink('[COLOR white]Setup Private Internet Access[/COLOR]',pia,1,'special://home/addons/'+addon_id+'/pia.jpg','',fanart)
    #addLink('[COLOR white]Setup IPVanish[/COLOR]',ipvanish,1,'special://home/addons/'+addon_id+'/ipvanish.jpg','',fanart)
    #addLink('[COLOR white]Setup VyprVPN[/COLOR]',vypr,1,'special://home/addons/'+addon_id+'/vypr.jpg','',fanart)
   
def setup(url):
    dlopenvpn()
    ovpnpath=url
    dialog = xbmcgui.Dialog() 
    ret = dialog.yesno(addon_name, 'Click continue to enter your account details','','','Cancel','Continue')
    if ret == 1:
            keyb = xbmc.Keyboard('', 'Enter Username')
            keyb.doModal()
            if (keyb.isConfirmed()):
                username = keyb.getText()
                keyb = xbmc.Keyboard('', 'Enter Password')
                keyb.doModal()
            else:return
            if (keyb.isConfirmed()):
                password = keyb.getText()
                selfAddon.setSetting('piauser',username)
                selfAddon.setSetting('piapass',password)
                user = selfAddon.getSetting('piauser')
                passw = selfAddon.getSetting('piapass')
            else:return
    else:return
    destfol2 = destfol + '/*.*'
    files = glob.glob(destfol2)
    for f in files:
        if not 'DUMMY' in f:
            os.remove(f)
    for filename in glob.glob(os.path.join(ovpnpath, '*.*')): shutil.copy(filename, destfol)
    passpath = destfol + '/pass.txt'
    auth = open(passpath,'w')
    auth.truncate()
    auth.close()
    auth = open(passpath,'a')
    auth.write(user)
    auth.write('\n')
    auth.write(passw)
    auth.close()
    dialog.ok(addon_name,'Setup Complete', 'Configure from the "VPN Configuration" option in the main menu')

def config():
    current_server = selfAddon.getSetting('connected')
    startup_server = selfAddon.getSetting('startup')
    addLink('[COLOR red][B]Disconnect from VPN[/B][/COLOR]','url',5,'iconimage','description',fanart)
    for filename in glob.glob(os.path.join(destfol, '*.ovpn')):
        server='Connect to - '+filename.split('\\')[-1].replace('.ovpn','').replace('/storage/.kodi/addons/plugin.program.oepia/WorkingFolder/','')
        server2=server
        if server==current_server: server=server+' [COLOR green][B] [Connected][/B][/COLOR]'
        if server2==startup_server: server=server+' [COLOR blue][B] [Auto][/B][/COLOR]'
        addServer(server,filename,6,'iconimage','description',fanart)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        
def disconnect():
    os.system('killall openvpn &')
    handle_wait(3,addon_name,'Closing any current connections')
    selfAddon.setSetting('connected','')
    xbmc.executebuiltin('Container.Refresh')
    ret = dialog.yesno(addon_name, 'You are now disconnected from the VPN','Any server set to auto is not affected','','OK','VPN Status')
    if ret==1:
        myip()
    else:return

def connect_to_server(name,url):
    selfAddon.setSetting('connected','')
    xbmc.executebuiltin('Container.Refresh')
    os.system('killall openvpn &')
    handle_wait(3,addon_name,'Closing any current connections')
    selfAddon.setSetting('connected',name)
    name=name.replace('Connect to - ','')
    string='/storage/.kodi/addons/network.openvpn/bin/openvpn '+url+' &'   
    os.system(string)                               
    handle_wait(5,addon_name,'Connecting')
    xbmc.executebuiltin('Container.Refresh')
    ret = dialog.yesno(addon_name, 'You are now connected to',name,'','OK','VPN Status')
    if ret==1:
        myip()
    else:return
    
def set_as_default(name,url):
    selfAddon.setSetting('connected',name)
    selfAddon.setSetting('startup',name)
    xbmc.executebuiltin('Container.Refresh')
    connect_to_server(name,url)
    name2=name.replace('Connect to - ','')
    script = open('/storage/.config/autostart.sh','w')
    command='(\nsleep 10\nopenvpn '+destfol+name2+'.ovpn\n)&'
    script.write(command)
    dialog.ok(addon_name,'Default connection set to '+name2, 'This will be auto set when booting your device')

def remove_default(name,url):
    selfAddon.setSetting('startup','')
    xbmc.executebuiltin('Container.Refresh')
    name2=name.replace('Connect to - ','')
    script = open('/storage/.config/autostart.sh','w')
    script.truncate()
    dialog.ok(addon_name,'Default connection reset', 'No VPN will be auto set when booting your device')

def myip():
    url = 'http://www.iplocation.net/'
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = re.compile("<td width='80'>(.+?)</td><td>(.+?)</td><td>(.+?)</td><td>.+?</td><td>(.+?)</td>").findall(link)
    inc = 1
    startup_server = selfAddon.getSetting('startup')
    startup_server=startup_server.replace('Connect to - ','')
    if startup_server=="":startup_server="None"
    for ip, region, country, isp in match:
        if inc <2: dialog.ok(addon_name,'[B][COLOR green]Your IP Address Is:  [/COLOR][/B]'+ip+'  ('+country+')','','[B][COLOR blue]Auto Start Set To:  [/COLOR][/B]'+startup_server)
        inc=inc+1
	
def handle_wait(time_to_wait,title,text):
    mensagemprogresso = xbmcgui.DialogProgress()
    ret = mensagemprogresso.create(' '+title)
    secs=0
    percent=0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment*secs
        secs_left = str((time_to_wait - secs))
        remaining_display = str(secs_left)+' seconds remaining'
        mensagemprogresso.update(percent,text,remaining_display)
        xbmc.sleep(1000)
        if (mensagemprogresso.iscanceled()):
            cancelled = True
            break
    if cancelled == True:
        return False
    else:
        mensagemprogresso.close()
        return False    

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
      
def addServer(name,url,mode,iconimage,description,fanart):
        u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)+'&description='+str(description)
        ok=True
        cmenu=[]
        cmenu.append(('[COLOR red]Remove Connection On Startup[/COLOR]','XBMC.RunPlugin(%s?mode=8&name=%s&url=%s)'% (sys.argv[0],name,url)))
        cmenu.append(('[COLOR green]Set As Connection On Startup[/COLOR]','XBMC.RunPlugin(%s?mode=7&name=%s&url=%s)'% (sys.argv[0],name,url)))
        liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
        liz.setInfo( type='Video', infoLabels={ 'Title': name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        liz.addContextMenuItems(items=cmenu, replaceItems=True,)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
    
def addLink(name,url,mode,iconimage,description,fanart):
        u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)+'&description='+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
        liz.setInfo( type='Video', infoLabels={ 'Title': name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
    
def addDir(name,url,mode,iconimage,description,fanart):
        u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)+'&description='+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
        liz.setInfo( type='Video', infoLabels={ 'Title': name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok 
 
params=get_params(); url=None; name=None; mode=None; site=None
try: site=urllib.unquote_plus(params['site'])
except: pass
try: url=urllib.unquote_plus(params['url'])
except: pass
try: name=urllib.unquote_plus(params['name'])
except: pass
try: mode=int(params['mode'])
except: pass
 
if mode==None or url==None or len(url)<1: Index()
elif mode==1: setup(url)
elif mode==2: remove()
elif mode==3: myip()
elif mode==4: config()
elif mode==5: disconnect()
elif mode==6: connect_to_server(name,url)
elif mode==7: set_as_default(name,url)
elif mode==8: remove_default(name,url)
elif mode==9: providers()
elif mode==10: fix()
elif mode==11: revertfix()
elif mode==12: dlopenvpn()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
