#!/usr/bin/env python3
# encoding: utf-8
#
# © 2017 Benjamin Mintz
# https://bmintz.mit-license.org/@2017
#

"""
techmeme: class that turns videos into dank technical may-mays
"""

import os

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import VideoClip
from moviepy.video.fx.speedx import speedx

from .config import TechnicalMemeConfig


class TechnicalMeme:
	def __init__(self, source_filename, config_filename):
		self.source_video = VideoFileClip(source_filename)
		self.config = TechnicalMemeConfig(config_filename)
		self._fix_up_timestamps()
	
	
	def _fix_up_timestamps(self):
		self.config.timestamps = [0] + self.config.timestamps + [self.source_video.end]
	
	
	def _get_subclip(self, timestamp_number):
		"""get a subclip at the timestamp given by self.config.timestamps[timestamp_number]"""
		
		if 0 <= timestamp_number < len(self.config.timestamps):
			return self.source_video.subclip(*self.config.timestamps[timestamp_number:timestamp_number+2])
		else:
			raise IndexError("timestamp number out of range")
	
	
	def _get_sped_up_subclip(self, timestamp_number):
		try:
			return self._get_subclip(timestamp_number)\
				.fx(speedx, self.config.multiplier**timestamp_number)
		except:
			raise
	
	
	def _write_subclip(self, timestamp_number):
		try:
			self._get_sped_up_subclip(timestamp_number)\
				.write_videofile("TMP_techmeme_{}.mp4"
					.format(timestamp_number))
		except IndexError:
			raise
		# moviepy is buggy and often returns index errors (raised as OSErrors)
		# when trying to save the last clip
		except OSError as ex:
			print(ex)
	
	
	def _write_all_subclips(self):
		for timestamp_number in range(len(self.config.timestamps)):
			
			print("{}...".format(timestamp_number), end=" ")
			
			try:
				self._write_subclip(timestamp_number)
			except IndexError:
				print("failed!")
				raise
			else:
				print("done.")
	
	
	def _silence(self, func, *args, **kwargs):
		"""silence the output of func(*args, **kwargs)"""
		
		import sys
		
		# save a copy of out and err so we can restore them later
		# TODO: see if this is necessary
		stdout, stderr = sys.stdout, sys.stderr
		
		sys.stdout = open(os.devnull, 'w')
		sys.stderr = open(os.devnull, 'w')
		
		try:
			func(*args, **kwargs)
			sys.stdout, sys.stderr = stdout, stderr
		except:
			raise
	
	
	def save(self, output_name):
		import pathlib
	
		try:
			self._write_all_subclips()
		except:
			raise
		
		with open("TMP_techmeme_concat_list.txt", "w") as ffmpeg_config:
			for i in range(len(self.config.timestamps)):
				filename = './TMP_techmeme_{}.mp4'.format(i)
				
				# if there was an error saving the video
				# (again, usually the last one)
				# so only build the concat list out of existing files
				try:
					with open(filename): # don't care about the file itself, only if it exists
						ffmpeg_config.write("file '{}'".format(filename))
				except OSError:
					pass
			
		
			try:
				os.system("ffmpeg -safe 0 -f concat -i {} -c copy {}".format(ffmpeg_config.name, output_name))
			except:
				raise
