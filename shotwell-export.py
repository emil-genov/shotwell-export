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
import sqlite3
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
	description='Exports all Shotwell photos and videos into a directory structure.',
	epilog='For more information, see http://bitbucket.org/robertkoehler/shotwell-export/')
parser.add_argument('-d', '--db', default='~/.local/share/shotwell/data/photo.db', help='location of photo.db, defaults to local user\'s')
parser.add_argument('-o', '--output-dir', default='shotwell-export', metavar='DIR', help='output location, defaults to shotwell-export')
parser.add_argument('-n', '--filename', default='{y}/{y}-{m}-{d} {event}/{file}', metavar='PATTERN', help='template for file path, defaults to {y}/{y}-{m}-{d} {event}/{file}')
parser.add_argument('-m', '--move', action='store_true', help='move files instead of copying. CONSIDER A BACKUP')
parser.add_argument('-s', '--stars', action='store_true', help='add ratings: IMG_1234 +++.JPG')
parser.add_argument('-r', '--replace', nargs=2, metavar=('SEARCH', 'REPLACE'), help='replace source path parts, try --replace /media/OldDrive/ /media/NewDrive/')

args = parser.parse_args()

if not os.path.exists(args.db):
	sys.stderr.write('could not find photo.db. Check option --db.\r\n')
	sys.exit()

db = sqlite3.connect(args.db)
db.row_factory = sqlite3.Row
cur = db.cursor()
cur.executescript('''
	CREATE TEMPORARY TABLE Media (
		id INTEGER,
		filename TEXT,
		timestamp INTEGER,
		rating INTERGER,
		event_id INTEGER
	);

	INSERT INTO Media SELECT id, filename, timestamp, rating, event_id FROM PhotoTable;
	INSERT INTO Media SELECT id, filename, timestamp, rating, event_id FROM VideoTable;
	CREATE INDEX MediaEventIDIndex ON Media (event_id);
''')

cur.execute('''
	SELECT 
		filename, 
		timestamp,
		rating,
		EventTable.name AS eventName, 
		(SELECT MIN(timestamp) FROM Media WHERE event_id = EventTable.id AND event_id != -1) AS eventTime 
	FROM 
		Media
	LEFT JOIN EventTable ON EventTable.id = event_id
''')

for row in cur:
	try:
		sourceFile = row['filename']
		if args.replace:
			sourceFile = sourceFile.replace(args.replace[0], args.replace[1])
	
		if row['eventTime']:
			date = datetime.datetime.fromtimestamp(row['eventTime'])
		else:
			date = getEXIFDate(sourceFile)
			if not date:
				date = datetime.datetime.fromtimestamp(row['timestamp'])
	
		filename = os.path.basename(row['filename'])
		if args.stars and row['rating'] > 0:
			filename, extension = os.path.splitext(filename)
			filename = filename + u' ' + (u'+' * row['rating']) + extension
		if row['eventName']:		
			targetFile = os.path.join(args.output_dir, args.filename.format(
				y='%04d' % date.year,
				m='%02d' % date.month,
				d='%02d' % date.day,
				event=row['eventName'].encode('utf-8') if row['eventName'] else '',
				file=filename.encode('utf-8')
			))
		else:
			targetFile = os.path.join(args.output_dir, filename.encode('utf-8'))
	
		targetFile = targetFile.replace('/ ', '/').replace(' /', '/')
		targetDir = os.path.dirname(targetFile)
		
		if not os.path.exists(sourceFile):
			sys.stderr.write(u'NOT FOUND: %s\r\n' % sourceFile)
		else:
			if not os.path.exists(targetDir):
				os.makedirs(targetDir)

			print(targetFile)
			if not os.path.exists(targetFile):
				if args.move:
					shutil.move(sourceFile, targetFile)
				else:
					shutil.copy2(sourceFile, targetFile)
	except Exception as e:
		sys.stderr.write(u'ERROR: Could not handle file\r\n')
		sys.stderr.write(u'(filename=%(filename)s, timestamp=%(timestamp)s, rating=%(rating)s, eventName=%(eventName)s, eventTime=%(eventTime)s)\r\n' % dict(zip(row.keys(), row)));
		raise e	

