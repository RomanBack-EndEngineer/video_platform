# Uses Andrew's captioning service to find captions for each keyframe

import requests
import os
import csv
from utils import returnVideoFramesFolder,returnVideoFolderName,OBJECTS_CSV,KEYFRAMES_CSV,KEYFRAMES_CSV,CAPTIONS_CSV

from dotenv import load_dotenv

def get_caption(filename):
	"""
	Gets a caption from the server given an image filename
	"""
	page = 'http://localhost:{}/upload'.format(os.getenv('GPU_LOCAL_PORT') or '5000')
	token = 'VVcVcuNLTwBAaxsb2FRYTYsTnfgLdxKmdDDxMQLvh7rac959eb96BCmmCrAY7Hc3'
	
	multipart_form_data = {
		'token': ('', str(token)),
		'img_file': (os.path.basename(filename), open(filename, 'rb')),
	}
	try:
		response = requests.post(page, files=multipart_form_data)
		if response.status_code != 200:
			print("Server returned status {}.".format(response.status_code))
			return []
		return response.text
	except:
		response = requests.post(page, files=multipart_form_data)
		if response.status_code != 200:
			print("Server returned status {}.".format(response.status_code))
			return []
		return response.text

def get_all_captions(video_name):
	"""
	Gets a caption for each extracted frame and returns a list of frame indices
	and the corresponding captions
	"""
	captions = []
	with open('{}/data.txt'.format(video_name), 'r') as datafile:
		data = datafile.readline().split()
		step = int(data[0])
		num_frames = int(data[1])
	
	for frame_index in range(0, num_frames, step):
		frame_filename = '{}/frame_{}.jpg'.format(video_name, frame_index)
		caption = get_caption(frame_filename)
		print(frame_index, caption)
		captions.append((frame_index, caption))
	
	return captions

def captions_to_csv(video_id, start=0):
	"""
	Gets a caption for each extracted frame and writes it to a csv file along with
	the frame index and a boolean indicating whether the frame is a keyframe or not
	"""
	video_frames_path = returnVideoFramesFolder(video_id)
	video_folder_path = returnVideoFolderName(video_id)
	with open('{}/data.txt'.format(video_frames_path), 'r') as datafile:
		data = datafile.readline().split()
		step = int(data[0])
		num_frames = int(data[1])
		frames_per_second = float(data[2])
	video_fps = step * frames_per_second
	seconds_per_frame = 1.0/video_fps
	
	with open(video_folder_path + '/'+ KEYFRAMES_CSV, newline='', encoding='utf-8') as incsvfile:
		reader = csv.reader(incsvfile)
		header = next(reader) # skip header
		keyframes = [int(row[0]) for row in reader]
	

	outcsvpath = video_folder_path + '/'+ CAPTIONS_CSV
	if os.path.exists(outcsvpath) :
		if os.stat(outcsvpath).st_size > 50:
			with open(outcsvpath, 'r', newline='', encoding='utf-8') as file:
				lines = file.readlines()
				lines.reverse()
				i = 0
				last_line = lines[i].split(",")[0]
				while not last_line.isnumeric():
					i+= 1
					last_line = lines[i].split(",")[0]
				start = int(last_line)+step
				file.close()

	mode = 'w'
	if start != 0:
		mode = 'a'

	with open(outcsvpath, mode, newline='', encoding='utf-8') as outcsvfile:
		writer = csv.writer(outcsvfile)
		if start == 0:
			writer.writerow(["Frame Index", "Timestamp", "Is Keyframe", "Caption"])
		for frame_index in range(start, num_frames, step):
			frame_filename = '{}/frame_{}.jpg'.format(video_frames_path, frame_index)
			caption = get_caption(frame_filename)
			print(frame_index, caption)
			row = [frame_index, float(frame_index) * seconds_per_frame, frame_index in keyframes, caption]
			writer.writerow(row)
			outcsvfile.flush()

def update_caption_keyframes(video_name):
	"""
	Updates the csv output by captions_to_csv in case the keyframes change
	"""

	with open('Keyframes.csv'.format(video_name), newline='', encoding='utf-8') as incsvkeyframes:
		reader = csv.reader(incsvkeyframes)
		header = next(reader) # skip header
		keyframes = [int(row[0]) for row in reader]
	with open('Captions.csv'.format(video_name), newline='', encoding='utf-8') as incsvcaptions:
		reader = csv.reader(incsvcaptions)
		header = next(reader) # skip header
		caption_rows = [row for row in reader]
	
	with open('Captions Updated.csv'.format(video_name), 'w', newline='', encoding='utf-8') as outcsvfile:
		writer = csv.writer(outcsvfile)
		writer.writerow(["Frame Index", "Timestamp", "Is Keyframe", "Caption"])
		for row in caption_rows:
			if row[0] != 'Frame Index':
				row[2] = int(row[0]) in keyframes
				writer.writerow(row)

if __name__ == "__main__":
	# video_name = 'A dog collapses and faints right in front of us I have never seen anything like it'
	# update_caption_keyframes(video_name)
	# video_name = 'Good Samaritans knew that this puppy needed extra help'
	# update_caption_keyframes(video_name)
	# video_name = 'Hope For Paws Stray dog walks into a yard and then collapses'
	# update_caption_keyframes(video_name)
	# video_name = 'This rescue was amazing - Im so happy I caught it on camera!!!'
	# update_caption_keyframes(video_name)
	# video_name = 'Oh wow this rescue turned to be INTENSE as the dog was fighting for her life!!!'
	# update_caption_keyframes(video_name)
	# video_name = 'Hope For Paws_ A homeless dog living in a trash pile gets rescued, and then does something amazing!'
	# update_caption_keyframes(video_name)
	
	video_name = 'Homeless German Shepherd cries like a human!  I have never heard anything like this!!!'
	captions_to_csv(video_name, start=3876)