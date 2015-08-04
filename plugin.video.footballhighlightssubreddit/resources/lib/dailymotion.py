import urllib2
import re
import json

def _get_video_links_json(video_id):
	url = "http://www.dailymotion.com/embed/video/" + video_id
	header = {'Cookie' : 'lang=en_EN; family_filter=on'}
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
		if '"statusCode":' in response_data:
			raise RuntimeError('Video not found')
			return ""
		video_info =  re.compile(r'info = (.+?)(?:,|;)\n').findall(response_data)
		video_json = json.loads(video_info[0])
		return video_json

def get_quality_video_link(quality, video_id):
	video_json = _get_video_links_json(video_id)
	hd_1080_url = video_json['stream_h264_hd1080_url']
	hd_720_url = video_json['stream_h264_hd_url']
	hq_480_url = video_json['stream_h264_hq_url']
	sd_360_url = video_json['stream_h264_url']
	ld_240_url = video_json['stream_h264_ld_url']
	if hd_1080_url and quality == 1080:
		url = hd_1080_url
	elif hd_720_url and quality >= 720:
		url = hd_720_url
	elif hq_480_url and quality >= 480:
		url = hq_480_url
	elif sd_360_url and quality >= 360:
		url = sd_360_url
	elif ld_240_url:
		url = ld_240_url
	url = url.replace("\\", "")
	return url