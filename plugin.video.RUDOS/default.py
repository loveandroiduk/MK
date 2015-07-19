import urllib,urllib2,re,cookielib,string,os,xbmc,xbmcgui,xbmcaddon,xbmcplugin,mknet
from resources.libs.common_addon import Addon

addon_id        = 'plugin.video.RUDOS'
selfAddon       = xbmcaddon.Addon(id=addon_id)
datapath        = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
fanart          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon            = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
art 		= xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/'))
user            = selfAddon.getSetting('hqusername')
passw           = selfAddon.getSetting('hqpassword')
cookie_file     = os.path.join(os.path.join(datapath,''), 'rudos.lwp')
net             = mknet.Net()

if user == '' or passw == '':
    if os.path.exists(cookie_file):
        os.remove(cookie_file)
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('RUDOS.tv', 'Please enter your account details','','','Cancel','Login')
    if ret == 1:
        keyb = xbmc.Keyboard('', 'Enter Username')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search = keyb.getText()
            username=search
            keyb = xbmc.Keyboard('', 'Enter Password:')
            keyb.doModal()
            if (keyb.isConfirmed()):
                search = keyb.getText()
                password=search
                selfAddon.setSetting('hqusername',username)
                selfAddon.setSetting('hqpassword',password)
    else:quit()
user = selfAddon.getSetting('hqusername')
passw = selfAddon.getSetting('hqpassword')

#############################################################################################################################

def setCookie(srDomain):
    html = net.http_GET(srDomain).content
    r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
    post_data = {}
    post_data['amember_login'] = user
    post_data['amember_pass'] = passw
    for name, value in r:
        value = value.replace('https','http')
        post_data[name] = value
    net.http_GET('http://rudos.tv/site/login')
    net.http_POST('http://rudos.tv/site/login',post_data)
    net.save_cookies(cookie_file)
    net.set_cookies(cookie_file)
   
def Index():
    setCookie('http://rudos.tv/site/login')
    response = net.http_GET('http://rudos.tv/site/live/')
    if not 'http://rudos.tv/site/logout' in response.content:
        dialog = xbmcgui.Dialog()
        dialog.ok('RUDOS.tv', 'Login Error','An error ocurred logging in. Please check your details','')
        quit()
    channels=re.compile("<li><div class='link'><a href='(.+?)'>(.+?)</a></div></li>").findall(response.content)
    for url,name in channels:
        url = 'http://rudos.tv/site/live/' +url
        addLink(name,url,1,icon,fanart)
                    
def playstream(url,name):
    setCookie('http://rudos.tv/site/live/')
    response = net.http_GET(url)
    link = response.content
    strurl=re.compile("file: '(.+?)',").findall(link)[0]
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=icon,thumbnailImage=icon); liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    if 'rtmp' in strurl:
        strurl=strurl + ' live=true timeout=20'
    xbmc.Player ().play(strurl, liz, False)

def addLink(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
    
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
              
params=get_params(); url=None; name=None; mode=None; iconimage=None
try:url=urllib.unquote_plus(params["url"])
except:pass
try:name=urllib.unquote_plus(params["name"])
except:pass
try:mode=int(params["mode"])
except:pass
try:iconimage=urllib.unquote_plus(params["iconimage"])
except:pass

print "Mode: "+str(mode); print "Name: "+str(name); print "Thumb: "+str(iconimage)
if mode==None or url==None or len(url)<1:Index()
elif mode==1:playstream(url,name)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))
