# conda activate preprocess_drone_video
# python 1_extract_frames_videos_fimix8tele.py --input-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/videos/100DRONE_2024-09-22_height=9m --frame-folder /media/biesseck/SSD_500GB/Datasets/drone_FIMIX8Tele/frames --valid-ext .MP4 --frame-ext png,jpg --frame-quality 90,95

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
                    print('\nExit')
                    os._exit(0)
            time.sleep(0.5)

    thread = threading.Thread(target=check_window_is_open)
    thread.start()


def play_video_sequential(video_path=''):
    print(f'Opening video: \'{video_path}\'')
    total_frames, width, height, fps = count_num_frames_video(video_path, verbose=True)
    delay_frame = int(1000.0/fps)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    should_pause = False

    window_name = os.path.basename(video_path)
    cv2.namedWindow(window_name, cv2.WINDOW_KEEPRATIO)
    start_monitoring_cv2_window(window_name)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:   # windows is open
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(delay_frame)
            print(f'    {window_name} - frame {frame_count}/{total_frames} - key: {key}    ', end='\r')

            if key == 32 or should_pause == True:     # spacebar
                should_pause = True
                if should_pause:
                    while True:
                        key = cv2.waitKey(0)
                        if key == 32:     # spacebar
                            should_pause = False
                            break
                        if key == 115:    # 's' or 'S' (save frame)
                            pass
                        if key == 27:     # ESC
                            break
                        if key == 83:     # RIGHT
                            break

            if key == 13:     # ENTER
                pass

            if key == 115:    # 's' or 'S' (save frame)
                pass

            if key == 27:     # ESC
                print('\nExit')
                os._exit(0)
                # break

        else:
            print('\nExit')
            os._exit(0)
            # break

        frame_count += 1
    print('')
    cv2.destroyAllWindows()
    os._exit(0)


def play_video_frame_idx(video_path=''):
    pass


def main():
    args = parse_args()
    
    if not os.path.exists(args.filepath):
        raise Exception('No such file or directory:', args.filepath)
        
    play_video_sequential(args.filepath)
    # play_video_frame_idx(args.filepath)

    


if __name__ == "__main__":
    main()
