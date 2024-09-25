# conda activate preprocess_drone_video
# python 0_preprocess_videos_fimix8tele.py --input-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/videos/100DRONE_2024-09-22_height=9m --delete-ext LRV,THM --valid-ext MP4

import os, sys
import argparse
from datetime import datetime
import re


def parse_args():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser(description="Preprocess videos by extracting frames, resizing, and optionally deleting the original videos.")
    parser.add_argument('--input-folder', type=str, required=True, help="Folder containing video files to preprocess")

    parser.add_argument('--delete-ext', type=list_of_strings, default='LRV,THM', help="LRV,THM")
    parser.add_argument('--valid-ext', type=list_of_strings, default='MP4', help="MP4,AVI")

    parser.add_argument('--suffix', type=str, default='', help="Suffix to be added in file name. Ex: _height=9m")
    parser.add_argument('-f', '--force', action='store_true', help="Force renaming files, even if they are already formatted")
    
    args = parser.parse_args()
    return args


def find_files_with_extensions(folder_path, valid_extensions):
    valid_extensions = [ext.lower() for ext in valid_extensions]
    matching_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in valid_extensions):
                matching_files.append(os.path.join(root, file))
    
    return sorted(matching_files)


def timeConvert(timestamp):
    newtime = datetime.fromtimestamp(timestamp)
    date_str = str(newtime.date())
    time_str = str(newtime.time()).split('.')[0].replace(':','-')
    return date_str, time_str


def filename_is_already_formatted(pathfile, suffix=''):
    filename = os.path.basename(pathfile)
    pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.'+suffix
    # print('pattern:', pattern)
    return bool(re.search(pattern, filename))



def main():
    args = parse_args()
    args.suffix = args.suffix.strip('_')
    # print('args.valid_ext:', args.valid_ext, 'type:', type(args.valid_ext), 'tuple:', tuple(args.valid_ext))
    # print('args.delete_ext:', args.delete_ext, 'type:', type(args.delete_ext), 'tuple:', tuple(args.delete_ext))
    # sys.exit(0)

    # Check directories
    if not os.path.exists(args.input_folder):
        raise Exception('No such directory:', args.input_folder)
    
    # Delete unnecessary files
    pathfiles_to_delete = find_files_with_extensions(args.input_folder, args.delete_ext)
    if len(pathfiles_to_delete) > 0:
        for idx_file, path_file in enumerate(pathfiles_to_delete):
            if path_file.endswith(tuple(args.delete_ext)) and not path_file.endswith(tuple(args.valid_ext)):
                print(f'DELETING FILE {idx_file}/{len(pathfiles_to_delete)}: {path_file}', end='\r')
                os.remove(path_file)
        print('')
    else:
        print(f'{len(pathfiles_to_delete)} files deleted, {len(pathfiles_to_delete)} files {args.delete_ext} found in \'{args.input_folder}\'')

    # Rename video files
    pathfiles_valid = find_files_with_extensions(args.input_folder, args.valid_ext)
    pathfiles_valid_to_rename = [filename for filename in pathfiles_valid
                                 if (not filename_is_already_formatted(filename, args.suffix) or args.force)]
    if len(pathfiles_valid_to_rename) > 0:
        for idx_pathfile_valid_rename, pathfile_valid_rename in enumerate(pathfiles_valid_to_rename):
            stat_orig_video = os.stat(pathfile_valid_rename)
            mdate_str, mtime_str = timeConvert(stat_orig_video.st_mtime)
            print(f'RENAMING FILE {idx_pathfile_valid_rename}/{len(pathfiles_valid_to_rename)}: {pathfile_valid_rename}')

            # build new file name
            pathfile_valid_rename_path, pathfile_valid_rename_filename = os.path.dirname(pathfile_valid_rename), os.path.basename(pathfile_valid_rename)
            pathfile_valid_rename_name, pathfile_valid_rename_extension = os.path.splitext(pathfile_valid_rename_filename)
            pathfile_valid_rename_newname = pathfile_valid_rename_name.split('_')[0] \
                                                      + '_' + mdate_str \
                                                      + '_' + mtime_str \
                                                      + ('_' + args.suffix if args.suffix != '' else '') \
                                                      + pathfile_valid_rename_extension
            pathfile_valid_rename_newpath = os.path.join(pathfile_valid_rename_path, pathfile_valid_rename_newname)
            print(f'              └─> {pathfile_valid_rename_newname}')
            os.rename(pathfile_valid_rename, pathfile_valid_rename_newpath)
        print('')
    else:
        print(f'{len(pathfiles_valid_to_rename)} files renamed, {len(pathfiles_valid)} files', args.valid_ext, f'with names already formatted in \'{args.input_folder}\'')



if __name__ == "__main__":
    main()
