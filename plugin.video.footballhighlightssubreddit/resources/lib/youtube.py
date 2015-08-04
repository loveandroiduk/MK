import urllib2
import re

def _get_video_link_dict(url):
	header = {'GData-Version' : '3.0' }
	req = urllib2.Request(url, None, header)
	try:
		response = urllib2.urlopen(req)
	except urllib2.URLError as e:
		if hasattr(e, 'reason'):
			raise RuntimeError(str(e.reason))
		elif hasattr(e, 'code'):
			raise RuntimeError(str(e.code))
	else:
		response_data = response.read()

	re_stream_map = re.compile(r'"url_encoded_fmt_stream_map": "(.+?)"')
	re_adaptive_fmts = re.compile(r'"adaptive_fmts": "(.+?)"')
	re_url = re.compile(r'url=(.+?)(?:,|\\)')
	re_itag = re.compile(r'itag=(\d+)')

	stream_map = re.search(re_stream_map, response_data).group(1)
	adaptive_fmts = re.search(re_adaptive_fmts, response_data).group(1)

	video_info = stream_map + adaptive_fmts
	
	urls = re.findall(re_url, video_info)

	url_dict = {}

	for u in urls:
		u = urllib2.unquote(urllib2.unquote(u))
		itag = re.search(re_itag, u).group(1)
		url_dict[str(itag)] = u
	
	return url_dict

def _check_if_quality(itag_dict, url_dict):
	if list(itag_dict):
		max_qual = max(list(itag_dict))
		for itag in itag_dict[max_qual]:
			if itag in url_dict:
				return url_dict[itag]
		else:
			max_qual = max(list(itag_dict))
			del itag_dict[max_qual]
			return _check_if_quality(itag_dict, url_dict)
	else:
		return None

def get_quality_video_link(quality, url, DASH):
	# itag code reference http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs
	# 					  https://github.com/rg3/youtube-dl/pull/1279
	itag_dict = {1080: ['37', '46'], 720: ['22', '45'],
				480: ['59', '44', '35'], 360: ['43', '34', '18', '6'],
				240: ['5', '36'], 144: ['17']}
	if DASH == 'true':
		itag_dict[1080].extend(['137', '248'])
		itag_dict[720].extend(['136', '247'])
		itag_dict[480].extend(['135', '246', '245', '244'])
		itag_dict[360].extend(['134', '243'])
		itag_dict[240].extend(['133', '242'])
		itag_dict[144].extend(['160'])

	
	quals = list(itag_dict)
	for qual in quals:
		if qual > quality:
			del itag_dict[qual]
			
	url_dict = _get_video_link_dict(url)
	
	return _check_if_quality(itag_dict, url_dict)