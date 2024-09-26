# conda activate preprocess_drone_video
# python 1_extract_frames_video_fimix8tele.py --input /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/videos/100DRONE_2024-09-22_height=9m/FIMI0001_2024-09-22_15-30-25_height=9m.MP4 --frame-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/frames --valid-ext .MP4 --frame-ext png,jpg --frame-quality 90,95
# python 1_extract_frames_video_fimix8tele.py --input /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/videos/100DRONE_2024-09-22_height=9m --frame-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/frames --valid-ext .MP4 --frame-ext png,jpg --frame-quality 90,95 --all

import os, sys
import cv2
import argparse
import time
from datetime import datetime
import re
import threading


def parse_args():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser(description="Extract frames from videos")
    parser.add_argument('--input', type=str, required=True, help="Folder containing video files to preprocess")
    parser.add_argument('--frame-folder', type=str, required=True, help="Folder to save extracted frames")
    
    parser.add_argument('--valid-ext', type=list_of_strings, default='MP4', help="MP4,AVI")
    parser.add_argument('--frame-ext', type=list_of_strings, default='png,jpg', help="png,jpg")
    parser.add_argument('--frame-quality', type=list_of_strings, default='95', help="90,95")  # ignored if --frame-ext=png'
    
    parser.add_argument('--all', action='store_true', help="Extract all frames from video")
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
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    try:
        if verbose: print(f'    Counting num frames video: ', end='')
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if verbose: print(f'{frame_count} - {width}x{height} - fps: {fps}')
    except:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if verbose:
                print(f'    Counting num frames video: {frame_count}', end='\r')
        if verbose: print(f' - {width}x{height} - fps: {fps}')
    return frame_count, width, height, fps


def save_frame(frame_path, frame, frame_quality=95):
    if frame_path.endswith('jpg'):
        cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), int(frame_quality)])
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



def start_monitoring_cv2_window(window_name=''):
        def check_window_is_open():
            while True:
                if cv2.getWindowProperty(window_name, 0) >= 0:
                    if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):   # windows is open
                        print("\nWindow closed")
                        os._exit(0)
                time.sleep(0.5)

        thread = threading.Thread(target=check_window_is_open)
        thread.start()

def manually_extract_frames_from_video(video_path='', frames_path='', frame_exts=['png','jpg'], frame_quality=95):
    print(f'Opening video: \'{video_path}\'')
    total_frames, width, height, fps = count_num_frames_video(video_path, verbose=True)
    delay_frame = int(1000.0/fps)
    cap = cv2.VideoCapture(video_path)

    print(f'    ESC/q: quit    SPACEBAR: pause/play    ←/a: previous frame    →/d: next frame    s: save frame')
    window_name = os.path.basename(video_path)
    cv2.namedWindow(window_name, cv2.WINDOW_KEEPRATIO)
    cv2.resizeWindow(window_name, 1024, 680)
    start_monitoring_cv2_window(window_name)

    if not cap.isOpened():
        Exception(f"Error: Unable to open video file: {video_path}")
        return

    playing = True
    frame_idx = 0
    key = -1

    # main loop
    while cap.isOpened():
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:   # windows is open
            print(f'    {window_name} - frame {frame_idx}/{total_frames} - key: {key}    ', end='\r')
            if playing:
                ret, frame = cap.read()
                if not ret:
                    print("\nEnd of video reached or error reading video")
                    break
                
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(delay_frame)
            else:
                key = cv2.waitKey(0)

            if key == 27 or key == ord('q'):  # ESC or 'q' key to exit
                print("\nExiting video player")
                os._exit(0)
            
            if key == ord(' '):  # Space key to pause/play
                playing = not playing
            
            if key == 81 or key == ord('a'):  # Left arrow key to move backward one frame
                playing = False
                frame_idx = max(0, frame_idx-1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(window_name, frame)

            if key == 83 or key == ord('d'):  # Right arrow key to move forward one frame
                playing = False
                frame_idx = min(total_frames-1, frame_idx+1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(window_name, frame)
            
            if key == ord('s'):  # Save frame
                video_name, video_ext = os.path.splitext(os.path.basename(video_path))
                for frame_ext in frame_exts:
                    frame_filename = f"{video_name}_frame_{frame_idx:06d}.{frame_ext}"
                    frame_path = os.path.join(frames_path, frame_filename)

                    if frame_path.endswith('jpg'):
                        for frame_qual in frame_quality:
                            frame_dir_jpg = os.path.dirname(frame_path)
                            frame_name_jpg, frame_ext_jpg = os.path.splitext(frame_filename)
                            frame_name_jpg += f'_JPEG_QUALITY={frame_qual}'
                            frame_path = os.path.join(frame_dir_jpg, f'{frame_name_jpg}{frame_ext_jpg}')
                            clear_terminal_line()
                            print(f"    Saving frame {frame_idx}/{total_frames}: {frame_path}")
                            save_frame(frame_path, frame, frame_qual)
                    else:
                        clear_terminal_line()
                        print(f"    Saving frame {frame_idx}/{total_frames}: {frame_path}")
                        save_frame(frame_path, frame)

            if playing:
                frame_idx += 1

        else:
            print("\nWindow closed")
            os._exit(0)

    os._exit(0)
    cap.release()
    cv2.destroyAllWindows()



def main():
    args = parse_args()
    
    # Check directories
    if not os.path.exists(args.input):
        raise Exception(f'No such file or directory: {args.input}')


    if os.path.isfile(args.input):
        video_name, video_ext = os.path.splitext(args.input.split('/')[-1])
        frame_video_folder = os.path.join(args.frame_folder, args.input.split('/')[-2], video_name)
        os.makedirs(frame_video_folder, exist_ok=True)

        if args.all:
            extract_all_frames_from_video(args.input, frame_video_folder, args.frame_ext, args.frame_quality)
        else:
            # show frames in screen for manual selection before saving them
            manually_extract_frames_from_video(args.input, frame_video_folder, args.frame_ext, args.frame_quality)


    elif os.path.isdir(args.input):
        if args.frame_folder.split('/')[-1] != args.input.split('/')[-1]:
            args.frame_folder = os.path.join(args.frame_folder, args.input.split('/')[-1])
        os.makedirs(args.frame_folder, exist_ok=True)

        # Find video files
        paths_videos = find_files_with_extensions(args.input, args.valid_ext)
        if len(paths_videos) > 0:
            for idx_video, path_video in enumerate(paths_videos):
                print(f'VIDEO {idx_video}/{len(paths_videos)}: {path_video}')
                
                video_name, video_ext = os.path.splitext(path_video.split('/')[-1])
                frame_video_folder = os.path.join(args.frame_folder, video_name)
                os.makedirs(frame_video_folder, exist_ok=True)

                if args.all:
                    extract_all_frames_from_video(path_video, frame_video_folder, args.frame_ext, args.frame_quality)
                else:
                    # show frames in screen for manual selection before saving them
                    manually_extract_frames_from_video(path_video, frame_video_folder, args.frame_ext, args.frame_quality)
        else:
            print(f'{len(paths_videos)} video files {args.valid_ext} found in \'{args.input}\'')



if __name__ == "__main__":
    main()
