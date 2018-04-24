import appex
import requests
import webbrowser


def main():
	if not appex.is_running_extension():
		url = 'http://arstechnica.com'
	else:
		url = appex.get_url()
	if url:
		webbrowser.get('safari').open(url)
	else:
		print('No input URL found.')


if __name__ == '__main__':
	main()

