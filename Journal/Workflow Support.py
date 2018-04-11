# create a nicely formatted location string and push it back to Workflow. also tell Workflow which file to show in Working Copy. 

#coding: utf-8
import location
import webbrowser
import time
import sys
from urllib.parse import quote
import json
import easywebdav
import os
import console

console.clear()

LOCAL_TEST = 'fake_workflow'
if len(sys.argv) == 1:
	sys.argv.append(LOCAL_TEST)

key = ''
with open('working_copy_key.txt') as f:
	key = f.readline().strip()

webdavPassword = ''
with open('working_copy_webdav_password.txt') as f:
	webdavPassword = f.readline().strip()

repository = 'journal'


def direct_from_workflow(workflow):
	def decdeg2dmsz(dd):
		is_positive = dd >= 0
		dd = abs(dd)
		minutes, seconds = divmod(dd * 3600, 60)
		degrees, minutes = divmod(minutes, 60)
		degrees = degrees if is_positive else -degrees
		degrees = int(degrees)
		minutes = int(minutes)
		z = int((seconds - int(seconds)) * 1e5)
		seconds = int(seconds)
		return [degrees, minutes, seconds, z]

	location.start_updates()

	gotloc = False
	for _ in range(30):
		loc = location.get_location()
		if (time.time() - loc['timestamp']) < 5:
			gotloc = True
			break

		time.sleep(0.5)

	location.stop_updates()

	if not gotloc:
		return 'Unknown'

	lat_dms = decdeg2dmsz(loc['latitude'])
	lat_ns = 'N'
	if lat_dms[0] < 0:
		lat_ns = 'S'
		lat_dms[0] *= -1

	lon_dms = decdeg2dmsz(loc['longitude'])
	lon_ew = 'E'
	if lon_dms[0] < 0:
		lon_ew = 'W'
		lon_dms[0] *= -1

	latlon = "{0[0]}˚{0[1]}'{0[2]}.{0[3]:05}\" {1}, {2[0]}˚{2[1]}'{2[2]}.{2[3]:05}\" {3}".format(
		lat_dms, lat_ns, lon_dms, lon_ew
	)

	geo = location.reverse_geocode(loc)
	if len(geo) == 0:
		geo = {}
	else:
		geo = geo[0]

	addr_bits = [geo.get(bit, None) for bit in 'Street City State Country'.split()]
	addr_bits = filter(
		lambda b: b is not None,
		addr_bits,
	)
	addr = ', '.join(addr_bits)

	if addr != '':
		place = '{} ({})'.format(addr, latlon)
	else:
		place = latlon

	return place


def get_newest_entry_path():
	wd = easywebdav.connect(
		'localhost',
		username='webdav',
		password=webdavPassword,
		port=8080,
		auth_mode=easywebdav.AUTH_MODE_DIGEST,
	)
	html_path = os.path.join('/', repository, 'HTML')
	wd.cd(quote(html_path))
	files = sorted([os.path.basename(x.name) for x in wd.ls()])
	return os.path.join('/HTML', files[-1])


def main():
	# the callback workflow name
	workflow = sys.argv[1]

	if len(sys.argv) >= 3:
		place = sys.argv[2]
	else:
		place = direct_from_workflow(workflow)

	if len(sys.argv) >= 4:
		workflow_result = sys.argv[3]
	else:
		webbrowser.open(
			'working-copy://x-callback-url/webdav?key={}&x-success={}&x-error={}&x-cancel={}'.
			format(
				quote(key),
				quote(
					'pythonista://Journal/{}?action=run&argv={}&argv={}&argv=webdavStarted'.
					format(
						quote('Workflow Support.py'),
						quote(workflow),
						quote(place),
					)
				),
				quote(
					'pythonista://Journal/{}?action=run&argv={}&argv={}&argv=webdavFailed'.
					format(
						quote('Workflow Support.py'),
						quote(workflow),
						quote(place),
					)
				),
				quote(
					'pythonista://Journal/{}?action=run&argv={}&argv={}&argv=webdavCanceled'.
					format(
						quote('Workflow Support.py'),
						quote(workflow),
						quote(place),
					)
				),
			),
		)
		return

	path = None
	if workflow_result == 'webdavStarted':
		path = get_newest_entry_path()
	else:
		print(workflow_result)

	result = {
		'location': place,
	}

	if path is not None:
		result['last entry path'] = path

	if workflow != LOCAL_TEST:
		webbrowser.open(
			'workflow://run-workflow?name={}&input=text&text={}'.format(
				quote(workflow),
				quote(json.dumps(result)),
			),
		)
	else:
		print(result)


if __name__ == '__main__':
	main()

