# conda activate preprocess_drone_video
# python play_video.py /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/videos/100DRONE_2024-09-22_height=9m/FIMI0001_2024-09-22_15-30-25_height=9m.MP4

import os, sys
import cv2
import argparse
import time
from datetime import datetime
import threading


def parse_args():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser(description="Just play a video in screen")
    parser.add_argument('filepath', type=str, help="")
    # parser.add_argument('--frame-folder', type=str, required=True, help="Folder to save extracted frames")
    
    # parser.add_argument('--valid-ext', type=list_of_strings, default='MP4', help="MP4,AVI")
    # parser.add_argument('--frame-ext', type=list_of_strings, default='png,jpg', help="png,jpg")
    # parser.add_argument('--frame-quality', type=list_of_strings, default='95', help="90,95")  # ignored if --frame-ext=png'
    
    # parser.add_argument('--manual', action='store_true', help="Select frames manually before extracting them")
    # parser.add_argument('-f', '--force', action='store_true', help="Force renaming files, even if they are already formatted")
    
    args = parser.parse_args()
    return args


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
        cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), frame_quality])
    else:
        cv2.imwrite(frame_path, frame)


def clear_terminal_line():
    sys.stdout.write('\x1b[2K')


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


def play_video_frame_idx(video_path=''):
    print(f'Opening video: \'{video_path}\'')
    total_frames, width, height, fps = count_num_frames_video(video_path, verbose=True)
    delay_frame = int(1000.0/fps)
    cap = cv2.VideoCapture(video_path)

    print(f'    ESC/q: quit    SPACEBAR: pause/play    ←/a: previous frame    →/d: next frame')
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

    while cap.isOpened():
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:   # windows is open
            print(f'    {window_name} - frame {frame_idx}/{total_frames} - key: {key}    ', end='\r')
            if playing:
                ret, frame = cap.read()
                if not ret:
                    print("End of video reached or error reading video")
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

    if not os.path.exists(args.filepath):
        raise Exception(f'No such file or directory: {args.filepath}')

    play_video_frame_idx(args.filepath)

    


if __name__ == "__main__":
    main()
