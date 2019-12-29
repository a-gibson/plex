#!/usr/bin/env python3

import argparse
import os
import re


def _moveFiles(files, disc_dirs, path):
    '''
    For a single disc album, rename the files in place (to include a hyphen separator between track number and name).
    For a multi disc album, also move the file to the corresponding 'Disc xx' directory.
    '''

    for f in files:
        m = re.match('(\d+)-\d+.*', f)
        src = os.path.join(path, f)

        if m:
            # This is a multi disc album, so move the file to a new directory in addition to renaming
            new_name = re.sub('^\d+-(\d+)\s(.*)', '\g<1> - \g<2>', f)
            dest = os.path.join(path, os.path.join(disc_dirs[m.group(1)], new_name))
        else:
            # This is a single disc album, so just rename the file
            new_name = re.sub('^(\d+)\s(.*)', '\g<1> - \g<2>', f)
            dest = os.path.join(path, new_name)

        os.rename(src, dest)


def _createNewDirectories(path, discs):
    '''
    If this is a multi disc album, create a new directory for each disc.
    '''

    disc_dirs = {}

    for d in discs:
        # Set disc number to two digits
        new_dir = "Disc " + "{0:0=2d}".format(int(d))
        new_path = os.path.join(path, new_dir)

        try:
            os.mkdir(new_path)
        except OSError:
            print ("Creation of the directory '{}' failed".format(new_path))

        disc_dirs[d] = new_dir

    return disc_dirs


def _getDiscs(files):
    '''
    Look at the names of the audio files to determine if they contain any information about discs.
    E.g. Does this album contain multiple discs of music?

    If present, disc information will be at the start of the file before a hyphen that separates it
    from the rest of the track information (such as track number and name).
    '''

    # Only want to store unique values, since every track will contain disc information if present
    discs = set()
    for f in files:
        m = re.match('(\d+)-\d+.*', f)
        if m:
            discs.add(m.group(1))

    return discs


def _getFiles(path):
    '''
    Gather details of the audio files.
    '''

    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.extend(filenames)
        break

    return f


def _parseArguments():
    parser = argparse.ArgumentParser(description='Convert an iTunes audio album to a structure and format suitable for Plex.')

    parser.add_argument(
        '-p',
        '--path',
        default='.',
        help='Path to the directory containing the audio files.')

    args = parser.parse_args()

    return args


def main():
    args = _parseArguments()

    files = _getFiles(args.path)

    discs = _getDiscs(files)

    disc_dirs = _createNewDirectories(args.path, discs)

    _moveFiles(files, disc_dirs, args.path)


if __name__ == "__main__":
    main()

