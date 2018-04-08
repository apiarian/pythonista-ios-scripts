# generate html pages for all of the journal entries in Working Copy

import webbrowser
import console
from urllib.parse import quote, unquote
import sys
import easywebdav
from os.path import basename, join
import re
import io
import markdown2

console.clear()

key = ''
with open('working_copy_key.txt') as f:
	key = f.readline().strip()

webdavPassword = ''
with open('working_copy_webdav_password.txt') as f:
	webdavPassword = f.readline().strip()

repository = 'journal'


def main():
	if len(sys.argv) < 2:
		webbrowser.open(
			'working-copy://x-callback-url/webdav?key={}&x-success={}&x-error={}&x-cancel={}'.
			format(
				quote(key),
				quote(
					'pythonista://Journal/{}?action=run&argv=webdavStarted'.format(
						quote('Generate HTML.py'),
					)
				),
				quote(
					'pythonista://Journal/{}?action=run&argv=webdavFailed'.format(
						quote('Generate HTML.py'),
					)
				),
				quote(
					'pythonista://Journal/{}?action=run&argv=webdavCancelled'.format(
						quote('Generate HTML.py'),
					)
				),
			),
		)
		return

	data = sys.argv[1]
	if data == 'webdavFailed':
		console.alert('failed to start webdav')
		return
	elif data == 'webdavCancelled':
		console.alert('webdav start cancelled')
		return
	elif data == 'webdavStarted':
		handleWebdav()


year_dir_re = re.compile(r'\d{4}')


def handleWebdav():
	wd = easywebdav.connect(
		'localhost',
		username='webdav',
		password=webdavPassword,
		port=8080,
		auth_mode=easywebdav.AUTH_MODE_DIGEST,
	)
	path = [repository]
	html_path = join('/', path[0], 'HTML')

	wdcd(wd, path)

	found = False
	for p in wdls(wd):
		if p == 'HTML':
			found = True
	if not found:
		wd.mkdir(html_path)

	files = []
	for p in wdls(wd):
		if year_dir_re.match(p):
			year_files = handleYearDir(wd, path, p)
			files.extend(year_files)
	files = sorted(files)

	for i, f in enumerate(files):
		prev = None
		if i > 0:
			prev = files[i - 1]
		next = None
		if i < len(files) - 1:
			next = files[i + 1]

		handleMarkdownFile(wd, f, prev, next)

	print('done!')

	webbrowser.open(
		'working-copy://',
	)


def wdcd(wd, path):
	wd.cd(join('/', *path))


def wdls(wd):
	parts = wd.ls()
	for (i, p) in enumerate(parts):
		parts[i] = unquote(basename(p.name))
	return parts


month_dir_re = re.compile(r'\d{2} - \w+')


def handleYearDir(wd, path, year):
	files = []

	path.append(year)
	wdcd(wd, path)
	for p in wdls(wd):
		if month_dir_re.match(p):
			month_files = handleMonthDir(wd, path, p)
			files.extend(month_files)
	path.pop()
	return files


interesting_file_re = re.compile(
	r'\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2} \w{3}\.(.+)',
)


def handleMonthDir(wd, path, month):
	files = []

	path.append(month)
	wdcd(wd, path)
	for p in wdls(wd):
		m = interesting_file_re.match(p)
		if m is None:
			continue
		ft = m.group(1)
		if ft != 'md':
			continue
		fp = path.copy()
		fp.append(p)
		files.append(fp)

	path.pop()
	return files


def handleMarkdownFile(wd, path, prev, next):
	mdbuf = io.BytesIO()
	wd.download(join('/', *path), mdbuf)
	mdbuf.seek(0)
	html = markdown2.markdown(
		mdbuf.read(),
	)
	html_path = join(
		'/',
		path[0],
		'HTML',
		path[-1].replace(
			'.md',
			'.html',
		),
	)

	prev_path = None
	if prev is not None:
		prev_path = quote(join(
			'.',
			prev[-1].replace('.md', '.html'),
		))
	next_path = None
	if next is not None:
		next_path = quote(join(
			'.',
			next[-1].replace('.md', '.html'),
		))

	nextprev = '''<div>
	<span style="display:inline-block; float:left">
	<a href="{}">{}</a>
	</span>
	&nbsp;
	<span style="float:right">
	<a href="{}">{}</a>
	</span>
	</div>'''.format(
		prev_path,
		'previous' if prev_path is not None else '',
		next_path,
		'next' if next_path is not None else '',
	)

	html = html.replace(
		'src="./',
		'src="{}/'.format(join('..', *path[1:-1])),
	)

	html = nextprev + html + nextprev

	html = '''
	<!DOCTYPE html>
	<head>
	<title>{}</title>
	<meta
		name="viewport" 
		content="user-scalable=no,width=device-width"
	/>
	<meta
		http-equiv="Content-Type"
		content="text/html; charset=UTF-8"
	/>
	<style>
	img {{
		max-width: 100%;
	}}
	</style>
	</head>
	<body>
	'''.format(
		path[-1].replace('.md', ''),
	) + html + '''
	</body>
	</html>
	'''

	htmlbuf = io.BytesIO()
	htmlbuf.write(html.encode())
	htmlbuf.seek(0)
	wd.upload(htmlbuf, html_path)

	print('wrote', quote(html_path))


if __name__ == '__main__':
	main()

