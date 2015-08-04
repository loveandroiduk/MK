import sys
import urllib
import urllib2
import urlparse
import json
import re
import xbmcgui
import xbmcplugin
import xbmcaddon
import os

from resources.lib.common_addon import Addon
from resources.lib import gdrive
from resources.lib import dailymotion
from resources.lib import youtube
from resources.lib import cloudyvideos


addon_id = 'plugin.video.footballhighlightssubreddit'
addon = Addon(addon_id, sys.argv)
icon = addon.queries.get('icon', '')
art = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/'))
my_addon = xbmcaddon.Addon(addon_id)
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
 
xbmcplugin.setContent(addon_handle, 'movies')
data=None

CVRef = 'http://reddit.com/footballhighlights'
CVUA = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:36.0) Gecko/20100101 Firefox/36.0'
CVHeader = {
 'Referer': CVRef,
 'User-Agent': CVUA,
}

__settings__ = xbmcaddon.Addon(id='plugin.video.footballhighlightssubreddit')
max_video_quality = __settings__.getSetting('max_video_quality')
qual = [360, 480, 720, 1080]
max_video_quality = qual[int(max_video_quality)]
DASH = __settings__.getSetting('DASH')
saved_searches = __settings__.getSetting('saved_searches_1') + ','\
	+ __settings__.getSetting('saved_searches_2') + ','\
	+ __settings__.getSetting('saved_searches_3')
saved_searches = [s.strip() for s in saved_searches.split(',')]
saved_searches = [s for s in saved_searches if s != '']
if saved_searches == []:
	saved_searches = None

 
def log(message):
	xbmc.log('plugin.video.footballhighlightssubreddit: %s' % message)

def build_url(query):
	return base_url + '?' + urllib.urlencode(query)
 
mode = args.get('mode', None)

def get_reddit_json(url, raw=0):
	header = {'User-Agent' : 'XBMC plugin for /r/footballhighlights'}
	req = urllib2.Request(url, None, header)
	try:
		response = urllib2.urlopen(req)
	except urllib2.URLError as e:
		if hasattr(e, 'reason'):
			log('URLError, %s' % str(e.reason))
			xbmc.executebuiltin('Notification(URLError, Could not reach server)')
		elif hasattr(e, 'code'):
			log('HTTPError, %s' % str(e.code))
			xbmc.executebuiltin('Notification(HTTPError, %s)' % str(e.code))
	else:
		response_data = response.read()
		if not raw:
			response_data = json.loads(response_data)
		return response_data

def display_posts(json_data, to_filter, reddit_base_url):
	if json_data:	
		for p in json_data['data']['children']:
			post_title = p['data']['title'].encode('utf8', 'replace')
			post_url = urllib2.quote(p['data']['url'].encode('utf-8'), ':/')
			if to_filter == 'true':
				log(str(post_url))
				comments_contents = get_reddit_json(post_url, 1)

				video_found = re_video.search(comments_contents)
				
				if video_found:
					url = build_url({'mode': 'folder', 'foldername': post_title, 'comments_contents': comments_contents})
					li = xbmcgui.ListItem(post_title, iconImage='icon')
					li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
					xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
			else:
				url = build_url({'mode': 'folder', 'foldername': post_title, 'post_url': post_url})
				li = xbmcgui.ListItem(post_title, iconImage='icon')
				li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
		after_post = json_data['data']['after']
		url = build_url({'mode': 'next_page', 'after_post': after_post, 'to_filter': to_filter, 'reddit_base_url': reddit_base_url})
		li = xbmcgui.ListItem('>> Next Page >>', iconImage='icon')
		li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
		xbmc.executebuiltin('Container.SetViewMode(51)')
		xbmcplugin.endOfDirectory(addon_handle)


subreddit_base_url = 'http://www.reddit.com/r/footballhighlights/.json?after='

re_video = re.compile(r'<a href="(?:(https?://(?:www.)?(?:docs|drive).google.com/file/d/[\w-]+/(?:preview|edit))[^#]*?|'
									'https?://(?:www.)?dailymotion.com/video/([\w-]+).*?|'
								   '(https?://(?:www.)?youtube.com/watch\?v=[\w-]+).*?|'
								   '(https?://(?:www.)?cloudyvideos.com/[\w-]+).*?)">(.*?)</a>')


if mode is None:
	#url = build_url({'mode': 'all_posts'})
	#li = xbmcgui.ListItem('All Posts', iconImage='DefaultFolder.png')
	#xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	url = build_url({'mode': 'filtered_posts'})
	li = xbmcgui.ListItem('All Videos', iconImage=art+'vod.JPG')
	li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	if saved_searches:
		for s in saved_searches:
			url = build_url({'mode': 'saved_search', 'query': s})
                        icon = art+'search.JPG'
                        if s == 'BBC Match of the Day':
                                icon = art+'motd.PNG'
                        if s == 'UEFA Champions League':
                                icon = art+'champ.JPG'
                        if s == 'Monday Night Football':
                                icon = art+'mnf.PNG'
                        if s == 'Revista de La Liga':
                                icon = art+'liga.JPG'
			li = xbmcgui.ListItem(s, iconImage=icon)
			li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	xbmc.executebuiltin('Container.SetViewMode(50)')
	xbmcplugin.endOfDirectory(addon_handle)

#elif mode[0] == 'all_posts':
#	json_data = get_reddit_json('http://www.reddit.com/r/footballhighlights/.json')
#	display_posts(json_data, 'false', subreddit_base_url)

elif mode[0] == 'filtered_posts':
	json_data = get_reddit_json('http://www.reddit.com/r/footballhighlights/.json')
	display_posts(json_data, 'true', subreddit_base_url)

elif mode[0] == 'saved_search':
	query = urllib.quote(args['query'][0])
	query_base_url = 'http://www.reddit.com/search/.json?q=' + query + '+subreddit%3Afootballhighlights&sort=new&t=all&limit=10&after='
	query_json_data = get_reddit_json(query_base_url)
	display_posts(query_json_data, 'false', query_base_url)
 
elif mode[0] == 'folder':
	try:
		comments_contents = args['comments_contents'][0]
	except:
		post_url = args['post_url'][0]
		comments_contents = get_reddit_json(post_url, 1)
	video_list = re.findall(re_video, comments_contents)
	for v in video_list:
		title = re.sub(r'<.*?>', '', v[4])
		if v[0]:
			id = v[0]
			try:
				url = gdrive.get_quality_video_link(max_video_quality, id, DASH)
			except:
				title = '[COLOR red]Unavailable[/COLOR]: ' + title
				url = ''
		elif v[1]:
			id = v[1]
			try:
				url = dailymotion.get_quality_video_link(max_video_quality, id)
			except:
				title = '[COLOR red]Unavailable[/COLOR]: ' + title
				url = ''
		elif v[2]:
			id = v[2]
			try:
				url = youtube.get_quality_video_link(max_video_quality, id, DASH)
			except:
				title = '[COLOR red]Unavailable[/COLOR]: ' + title
				url = ''
		elif v[3]:
			id = v[3]
			if '/embed-' in id:
				continue
			try:
				url = cloudyvideos.get_quality_video_link(id,None,CVHeader) + '|User-Agent=%s&Referer=%s' % (CVUA,CVRef)

			except:
				title = '[COLOR red]Unavailable[/COLOR]: ' + title
				url = ''
		else:
			continue
		li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
		li.setProperty('IsPlayable', 'true')
		if url is None:
			url = ''
		log(url)
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'next_page':
	after_post = args['after_post'][0]
	to_filter = args['to_filter'][0]
	reddit_base_url = args['reddit_base_url'][0]
	json_data = get_reddit_json(reddit_base_url + after_post)
	display_posts(json_data, to_filter, reddit_base_url)
