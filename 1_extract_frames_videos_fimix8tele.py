# conda activate preprocess_drone_video
# python 1_extract_frames_videos_fimix8tele.py --input-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/videos/100DRONE_2024-09-22_height=9m --frame-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/frames --valid-ext .MP4 --frame-ext png,jpg --frame-quality 90,95

import os, sys
import cv2
import argparse
from datetime import datetime
import re


def parse_args():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser(description="Extract frames from videos")
    parser.add_argument('--input-folder', type=str, required=True, help="Folder containing video files to preprocess")
    parser.add_argument('--frame-folder', type=str, required=True, help="Folder to save extracted frames")
    
    parser.add_argument('--valid-ext', type=list_of_strings, default='MP4', help="MP4,AVI")
    parser.add_argument('--frame-ext', type=list_of_strings, default='png,jpg', help="png,jpg")
    parser.add_argument('--frame-quality', type=list_of_strings, default='95', help="90,95")  # ignored if --frame-ext=png'
    
    parser.add_argument('--manual', action='store_true', help="Select frames manually before extracting them")
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


def count_num_frames_video(video_path, verbose=False):
    cap = cv2.VideoCapture(video_path)
    try:
        if verbose: print(f'    Counting num frames video: ', end='')
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if verbose: print(f'{frame_count}')
    except:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if verbose:
                print(f'    Counting num frames video: {frame_count}', end='\r')
        if verbose: print('')
    return frame_count


def save_frame(frame_path, frame, frame_quality=95):
    if frame_path.endswith('jpg'):
        cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), frame_quality])
    else:
        cv2.imwrite(frame_path, frame)


def clear_terminal_line():
    sys.stdout.write('\x1b[2K')


def extract_all_frames_from_video(video_path='', frames_path='', frame_exts=['png','jpg'], frame_quality=95):
    frame_exts = [ext.lower().strip('.') for ext in frame_exts]
    
    if not type(frame_quality) is list:
        frame_quality = [frame_quality]
    frame_quality = [int(frame_qual) for frame_qual in frame_quality]

    num_frames_video = count_num_frames_video(video_path, verbose=True)
    cap = cv2.VideoCapture(video_path)
    idx_frame = 0

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))

    print(f"    Processing {video_name} ({width}x{height}, {fps} FPS)...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        for frame_ext in frame_exts:
            frame_filename = f"{video_name}_frame_{idx_frame:06d}.{frame_ext}"
            frame_path = os.path.join(frames_path, frame_filename)

            if frame_path.endswith('jpg'):
                for frame_qual in frame_quality:
                    frame_dir_jpg = os.path.dirname(frame_path)
                    frame_name_jpg, frame_ext_jpg = os.path.splitext(frame_filename)
                    frame_name_jpg += f'_JPEG_QUALITY={frame_qual}'
                    frame_path = os.path.join(frame_dir_jpg, f'{frame_name_jpg}{frame_ext_jpg}')
                    clear_terminal_line()
                    print(f"\r    Saving frame {idx_frame}/{num_frames_video}: {frame_path}", end='\r')
                    save_frame(frame_path, frame, frame_qual)
            else:
                clear_terminal_line()
                print(f"\r    Saving frame {idx_frame}/{num_frames_video}: {frame_path}", end='\r')
                save_frame(frame_path, frame)

        idx_frame += 1

    cap.release()
    print(f"Extracted {idx_frame} frames from {video_name}.")


def manually_extract_frames_from_video(video_path='', frames_path='', frame_exts=['png','jpg'], frame_quality=95):
    pass



def main():
    args = parse_args()
    
    # Check directories
    if not os.path.exists(args.input_folder):
        raise Exception('No such file or directory:', args.input_folder)
    if args.frame_folder.split('/')[-1] != args.input_folder.split('/')[-1]:
        args.frame_folder = os.path.join(args.frame_folder, args.input_folder.split('/')[-1])
    os.makedirs(args.frame_folder, exist_ok=True)
    
    
    # Find video files
    paths_videos = find_files_with_extensions(args.input_folder, args.valid_ext)
    if len(paths_videos) > 0:
        for idx_video, path_video in enumerate(paths_videos):
            print(f'VIDEO {idx_video}/{len(paths_videos)}: {path_video}')
            
            video_name, video_ext = os.path.splitext(path_video.split('/')[-1])
            frame_video_folder = os.path.join(args.frame_folder, video_name)
            os.makedirs(frame_video_folder, exist_ok=True)

            if args.manual:
                # show frames in screen for manual selection before saving them
                manually_extract_frames_from_video(path_video, frame_video_folder, args.frame_ext, args.frame_quality)
            else:
                extract_all_frames_from_video(path_video, frame_video_folder, args.frame_ext, args.frame_quality)
    else:
        print(f'{len(paths_videos)} video files {args.valid_ext} found in \'{args.input_folder}\'')

    


if __name__ == "__main__":
    main()
