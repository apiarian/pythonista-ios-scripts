# create a nicely formatted location string and push it back to Workflow

#coding: utf-8
import location
import clipboard
import webbrowser
import time
import sys
import urllib

# the callback workflow name
workflow = sys.argv[1]

def decdeg2dmsz(dd):
	is_positive = dd >= 0
	dd = abs(dd)
	minutes,seconds = divmod(dd*3600,60)
	degrees,minutes = divmod(minutes,60)
	degrees = degrees if is_positive else -degrees
	degrees = int(degrees)
	minutes = int(minutes)
	z = int((seconds - int(seconds)) * 1e5)
	seconds = int(seconds)
	return [degrees,minutes,seconds,z]


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
	place = 'Unknown'

else:
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
		
	latlon = "{0[0]}˚{0[1]}'{0[2]}.{0[3]:05}\" {1}, {2[0]}˚{2[1]}'{2[2]}.{2[3]:05}\" {3}".format(lat_dms, lat_ns, lon_dms, lon_ew)
	
	
	geo = location.reverse_geocode(loc)
	if len(geo) == 0:
		geo = {}
	else:
		geo = geo[0]
	
	addr_bits = [
		geo.get(bit, None)
		for bit in 'Street City State Country'.split()
	]
	addr_bits = filter(
		lambda b: b is not None,
		addr_bits,
	)
	addr = ', '.join(addr_bits)
	
	
	if addr != '':
		place = '{} ({})'.format(addr, latlon)
	else:
		place = latlon

webbrowser.open(
	'workflow://run-workflow?name={}&input=text&text={}'.format(
		urllib.parse.quote(workflow),
		urllib.parse.quote(place),
	),
)

