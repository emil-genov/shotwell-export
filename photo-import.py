#!/usr/bin/env python
# coding=utf-8

''' 

This file is part of shotwell-export.

Copyright 2013 Robert Koehler <robert.koehler@ee39.de>

shotwell-export is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

shotwell-export is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
shotwell-export. If not, see http://www.gnu.org/licenses/.

'''

import os
import sys
import shutil
import re
import datetime
import argparse

haveEXIF = False
try:
	import EXIF
	haveEXIF = True
except ImportError:
   	sys.stderr.write('Please note: Extended EXIF support not available.\r\n')

def getEXIFDate(filename):
	if haveEXIF:
		try:
			f = open(filename, 'rb')
			tags = EXIF.process_file(f, details=False, stop_tag='EXIF DateTimeOriginal')
			f.close();
	
			if 'EXIF DateTimeOriginal' in tags:
				tag = str(tags['EXIF DateTimeOriginal'])
				return datetime.date(int(tag[0:4]), int(tag[5:7]), int(tag[8:10]))
		except IOError:
			pass
		except ValueError:
			pass

	return None


parser = argparse.ArgumentParser(
	description='Imports photos and videos into a directory structure.',
	epilog='For more information, see http://bitbucket.org/robertkoehler/shotwell-export/')

parser.add_argument('source', metavar='SOURCE', nargs='+', help='location to search media in')
parser.add_argument('-o', '--output-dir', default='./', metavar='DIR', help='output location, defaults to current directory')
parser.add_argument('-n', '--filename', default='{y}/{y}-{m}-{d} {event}/{file}', help='template for file path, defaults to {y}/{y}-{m}-{d} {event}/{file}')
parser.add_argument('-p', '--pattern', default='.*\.((jp.?g)|(png)|(avi)|(mp4))$', help='pattern for file search, defaults to ...')
parser.add_argument('-m', '--move', action='store_true', help='move files instead of copying. CONSIDER A BACKUP')
parser.add_argument('-e', '--event', help='use this text as event description')

args = parser.parse_args()
prog = re.compile(args.pattern, flags=re.IGNORECASE)

for source in args.source:
	for dirpath, dirnames, filenames in os.walk(source):
		for filename in filenames:
			try:
				if prog.match(filename):
					sourceFile = os.path.join(dirpath, filename)
					date = getEXIFDate(sourceFile)
					if not date:
						date = datetime.datetime.fromtimestamp(os.path.getmtime(sourceFile))
			
					targetFile = os.path.join(args.output_dir, args.filename.format(
						y='%04d' % date.year,
						m='%02d' % date.month,
						d='%02d' % date.day,
						event=args.event if args.event else '',
						file=filename
					))
		
					targetFile = targetFile.replace('/ ', '/').replace(' /', '/')
					targetDir = os.path.dirname(targetFile)
			
					if not os.path.exists(targetDir):
						os.makedirs(targetDir)
		
					print(targetFile)
					if not os.path.exists(targetFile):
						if args.move:
							shutil.move(sourceFile, targetFile)
						else:
							shutil.copy2(sourceFile, targetFile)

			except Exception as e:
				sys.stderr.write(u'ERROR: Could not handle file %s\r\n' % sourceFile)
				raise e	

