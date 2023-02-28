import requests
from multiprocessing.dummy import Pool as ThreadPool
import json
import cloudscraper
import re
import click
import os
import random

scraper = cloudscraper.create_scraper(browser='chrome')

def mkdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

def file_exists(save_dir, model_id):
	for file in os.listdir(save_dir):
		if file.startswith(f"{model_id}_"):
			return True
	return False

def download_civitai_by_id(save_dir, model_id):
	# Make dir if not exists
	mkdir(save_dir)
	url = f"https://civitai.com/api/download/models/{model_id}"
	# Skip if downloaded
	if file_exists(save_dir, model_id):
		print(f"[NOTICE] {url} is downloaded, return.")
		return
	# Download file
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
		# Encode it into ISO-8859-1 and then return it to utf-8 (https://www.rfc-editor.org/rfc/rfc5987.txt)
		headers_utf8 = r.headers["Content-Disposition"].encode('ISO-8859-1').decode()
		print(headers_utf8)
		file_name_raw = re.search(r'filename=\"(.*)\"', headers_utf8).group(1)
		file_name = file_name_raw.replace(":", "_")
		save_name = os.path.join(save_dir, f"{model_id}_{file_name}")
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
@click.option('--pool_size', help='Size of multithread pools', type=click.IntRange(min=0), default = 16)
def main(l, r, save_dir, pool_size):
	print(f"[START] Program Start!")
	pool = ThreadPool(pool_size)
	def task(model_id):
		download_civitai_by_id(save_dir, model_id)
	download_list = list(range(l, r+1))
	random.shuffle(download_list)
	pool.map(task, download_list)
	pool.close()
	pool.join()
	print(f"[FINISH] Program Finished!")

if __name__ == "__main__":
    main()
