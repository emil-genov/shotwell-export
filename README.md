Shotwell Export
===============

This is a fork of [original script made by Robert Koehler](https://bitbucket.org/robertkoehler/shotwell-export). I've made a super small change, that for the Shotwell events, that does not have their own name defined, files end in the base folder, instead of in a separate folder. That way You can have named folders for the important stuff and all not so important photos will end up in the base extraction folder

Following is direct copy from original with few changes: 

Shotwell Export is a small tool for exporting your whole [Shotwell][1] photo library to a simple but still intuitive file structure.

By default, it will generate a file structure similiar to:

    shotwell-export/
        2012/
            2012-05-01 Dinner At Zuni/
            2012-04-21 Brunch/
            2012-04-11 Botanical Garden/
            2012-04-07 Our new Kitten/
        2011/
            2011-03-05 Egypt/
            ...

Getting Started
---------------

Currently, the easiest way is to download the file directly from github.com:

    sudo wget -O /usr/bin/shotwell-export https://raw.githubusercontent.com/emil-genov/shotwell-export/master/shotwell-export.py
    sudo chmod a+x /usr/bin/shotwell-export

If you want better date support, download this EXIF library. This is optional.

    sudo wget -O /usr/bin/EXIF.py https://raw.github.com/ianare/exif-py/master/EXIF.py

Now, you can invoke the help:

    # shotwell-export --help
    usage: shotwell-export.py [-h] [-d DB] [-o OUTPUT_DIR] [-n FILENAME] [-m] [-s]
                              [-r REPLACE REPLACE]
    
    Exports all Shotwell photos and videos into a directory structure.
    
    optional arguments:
      -h, --help            show this help message and exit
      -d DB, --db DB        location of photo.db, defaults to local user's
      -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            output location, defaults to shotwell-export
      -n FILENAME, --filename FILENAME
                            template for file path, defaults to {y}/{y}-{m}-{d}
                            {event}/{file}
      -m, --move            move files instead of copying. CONSIDER A BACKUP
      -s, --stars           add ratings: IMG_1234 +++.JPG
      -r REPLACE REPLACE, --replace REPLACE REPLACE
                            replace source path parts, try --replace
                            /media/OldDrive/ /media/NewDrive/
    
    For more information, see http://bitbucket.org/robertkoehler/shotwell-export/


By default, `shotwell-export` will load the photo database of the local user and copy all files known to shotwell into the directory `shotwell-export`.

To extract all photos from a backup location, this command would be a good choice:

    shotwell-export --db /media/Drive/Backups/Shotwell/data/photo.db --replace /home/user/Photos/ /media/Drive/Backups/Shotwell/ --stars

Some extra switches are documented in the next section.

Command Line
------------

Some arguments explained.

### Location of photo.db

`-d DB`, `--db DB` allow to specify a different location than `~/.local/share/shotwell/data/photo.db` 

### Broken paths in photo.db

Sometimes, you had to move the pictures from one drive to another and shotwell does not find its photos anymore. Apply this argument if a lot of `NOT FOUND:` messages pop up. You can let `shotwell-export` know the new location:

`--replace /media/MyOldDrive/Photos/ /media/NewDrive/Media/Photos/`

### Keep the rating

You can have the rating appended as a sequence of plussed appended to the original filename. Rating `-1` to `5` will become `+` to `+++++`. 


Known Issues
--------------

* Using python3 the EXIF.py library will fail to work. The script runs fine.


Credits
-------

This code based on the [Stackoverflow reply of Dan][2].


[1]: http://www.yorba.org/projects/shotwell/
[2]: http://askubuntu.com/questions/111290/how-can-i-export-my-shotwell-gallery
