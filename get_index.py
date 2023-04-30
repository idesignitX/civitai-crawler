import os
import shutil
import re
from urllib.parse import urljoin
import cloudscraper
from multiprocessing.dummy import Pool as ThreadPool
import click
import random

root_dir = "Civitai_getlinks"
civitai_url = "https://civitai.com/api/download/models/"
global_encoding = 'utf-8'
delimiter = "|        |"

scraper = cloudscraper.create_scraper(browser='chrome')

#Directory Operations
def mkdir(dir):
	os.makedirs(dir, exist_ok=True)

def remove_dir_recursive(dir):
	if not os.path.exists(dir):
		return
	shutil.rmtree(path=dir)

def walk_dir(dirname): #Generator
	for root, dirs, files in os.walk(dirname):
		for f in files:
			yield (os.path.join(root, f), root, f)

#Functions
def create_index(save_dir, l, r, pool_size):
	print(f"Save index from range {l} to {r}...")

	mkdir(save_dir)

	txt_name = f"{l}-{r}"
	txt_name_link = os.path.join(save_dir, f"{txt_name}_link.txt")
	txt_name_index = os.path.join(save_dir, f"{txt_name}_index.txt")

	url_links = list(range(l, r+1))
	random.shuffle(url_links)
	collected_url_links = []
	collected_index = []
	
	def task(uid):
		file_name, byte_size = get_info(uid)
		if file_name is not None:
			print(f"File_name: {file_name}, Byte_size: {byte_size}")
			collected_url_links.append(uid)
			collected_index.append((uid, file_name, byte_size))

	with open(txt_name_link, 'wb') as f1, open(txt_name_index, 'wb') as f2:
		pool = ThreadPool(pool_size)
		pool.map(task, url_links)
		pool.close()
		pool.join()

		collected_url_links.sort()
		collected_index.sort()

		for uid in collected_url_links:
			f1.write(bytes(f"{civitai_url}{uid}\n", global_encoding))
		for uid, file_name, byte_size in collected_index:
			f2.write(bytes(f"{uid}{delimiter}{file_name}{delimiter}{byte_size}\n", global_encoding))

def get_info(uid):
	url = f"{civitai_url}{uid}"
	print(f"Getting {url}...")
	with scraper.get(url, stream=True) as r:
		r.encoding = 'utf-8'
		print(r.headers)
		if "Content-Disposition" not in r.headers:
			print(f"[INFO] {url} not found, return.")
			return (None, None)
		headers_utf8 = r.headers["Content-Disposition"].encode('ISO-8859-1').decode()
		file_name = re.search(r'filename=\"(.*)\"', headers_utf8).group(1)
		file_name = file_name.replace(":", "_")
		file_name = file_name.replace("<", "(")
		file_name = file_name.replace(">", ")")
		byte_size = r.headers["Content-Length"]
		return (file_name, byte_size)

@click.command()
@click.option('--l', help='Minimum_id', type=click.IntRange(min=0), default = 1)
@click.option('--r', help='Maximum_id', type=click.IntRange(min=0), default = 0)
@click.option('--save_dir', help='Directory to save models', type=str)
@click.option('--pool_size', help='Size of multithread pools', type=click.IntRange(min=0), default = 16)
def main(l, r, save_dir, pool_size):
	print(f"[START] Program Start!")
	create_index(save_dir, l, r, pool_size)

if __name__ == '__main__':
	main()
