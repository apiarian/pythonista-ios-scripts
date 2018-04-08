# untar a file into the current ditectory. indended to be used as a share widget

import tarfile
import appex
import console


def main():
	fn = None
	if appex.is_running_extension():
		fn = appex.get_file_path()

	if fn is None:
		print('no file to untar!')
		return

	with tarfile.open(fn) as f:
		console.clear()
		print(f.list())
		print(
			'ok to extract? [y/N]',
		)
		yn = input()
		if yn == 'y':
			f.extractall()
			print('extracted')
		else:
			print('did not extract')


if __name__ == '__main__':
	main()

