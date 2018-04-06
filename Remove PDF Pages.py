# Install as a share sheet extension for Pythonista to remove pages from a PDF. The trimmed PDF is shown in a final quicklook view for sharing or saving.

import appex
import PyPDF2
import tempfile
import console
import os

if appex.is_running_extension():
	src_path = appex.get_file_path()
else:
	src_path = './testpdf.pdf'

src = PyPDF2.PdfFileReader(src_path)

dst = PyPDF2.PdfFileWriter()

for i in range(src.getNumPages()):
	p = src.getPage(i)

	with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
		tmp = PyPDF2.PdfFileWriter()
		tmp.addPage(p)
		tmp.write(f)
		f.close()
		console.quicklook(f.name)

	if console.alert(
		'Keep?',
		'Keep that page?',
		'Yes',
		'No',
	) == 1:
		dst.addPage(p)

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
	dst.write(f)
	f.close()
	console.alert('Done', 'Show the results!', 'OK', hide_cancel_button=True)
	console.quicklook(f.name)
	os.remove(f.name)

