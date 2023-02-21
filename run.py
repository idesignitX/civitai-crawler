import requests
from multiprocessing.dummy import Pool as ThreadPool
import json
import cloudscraper
import re
import click
import os

scraper = cloudscraper.create_scraper(browser='chrome')

def mkdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

def download_civitai_by_id(save_dir, model_id):
	# Make dir if not exists
	mkdir(save_dir)
	url = f"https://civitai.com/api/download/models/{model_id}"
	print(f"Downloading {url}...")
	tmp_filename = os.path.join(save_dir, f"{model_id}.tmp")
	with scraper.get(url, stream=True) as r:
		# Set encoding to utf-8 to avoid character issues
		r.encoding = 'utf-8'
		with open(tmp_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192): 
				# If you have chunk encoded response uncomment if
				# and set chunk_size parameter to None.
				#if chunk:
				f.write(chunk)
		print(r.headers)
		if "Content-Disposition" not in r.headers:
			os.remove(tmp_filename)
			print(f"[INFO] {url} not found, return.")
			return
		headers_utf8 = r.headers["Content-Disposition"].encode('ISO-8859-1').decode()
		print(headers_utf8)
		header_match = re.search(r'filename=\"(.*?)\"', headers_utf8)
		# Encode it into ISO-8859-1 and then return it to utf-8 (https://www.rfc-editor.org/rfc/rfc5987.txt)
		save_name = os.path.join(save_dir, f"{model_id}_{header_match.group(1)}")
	# Rename temporary files to filename
	if os.path.exists(save_name):
		os.remove(save_name)
	os.rename(tmp_filename, save_name)
	# Download finished
	print(f"[INFO] Downloaded {url} to {save_name}!")

@click.command()
@click.option('--l', help='Minimum_id', type=click.IntRange(min=0), default = 1)
@click.option('--r', help='Maximum_id', type=click.IntRange(min=0), default = 0)
@click.option('--save_dir', help='Directory to save models', type=str)
def main(l, r, save_dir):
	print(f"[START] Program Start!")
	for model_id in range(l, r+1):
		download_civitai_by_id(save_dir, model_id)
	print(f"[FINISH] Program Finished!")

if __name__ == "__main__":
    main()
