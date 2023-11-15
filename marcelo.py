import csv
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
# from youtube_uploader_selenium import YouTubeUploader
from datetime import datetime, timedelta
import time

def upload_video(file_name, thumb, title, desc):
    
    command = f"cd /content && python3 /content/Youtube-Auto-Upload/youtube.py --file='{file_name}' --thumb='{thumb}' --title='{title}' --description='{desc}' --privacyStatus='private'"
    output_file = subprocess.call(command, shell=True)
    if (output_file != 0): exit(1)

def thumb_generator(file, title):
    print('Generating thumbnails...')
    bg_dir = './thumbs/'
            
    # if sucessfully copy the frame, check and create thumbnail
    command = "python3 ./thumb_generator.py --input './assets/default_face.png' --title '"+title+"'"
    output_file = subprocess.call(command, shell=True)
    
    command = "python3 ./thumb_generator.py --input "+file+" --title '"+title+"' -d False"
    output_file = subprocess.call(command, shell=True)
    
    if (len(os.listdir(bg_dir)) >= 1):
        bg = random.choice(os.listdir(bg_dir))
        return (bg_dir+bg)
    else:
        exit(1)

def move_files(title):
    files = title.replace(' ','_')
    command = "mkdir -p output/"+files+"/ && mv *.mp4 output/"+files+"/"
    output_file = subprocess.call(command, shell=True)

def main():
    with open('lists/list.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        try:
            header = next(reader)
            print(header)
            row_number = 0
            for row in reader:
                print('%s' % (row))

                url             = row[0]
                cut_start       = row[1]
                cut_end         = row[2]
                podcast         = row[3]
                title           = row[4]
                description     = row[5]
                tags            = row[6]

                title = title.split("|")
                title = title[0]

                output_filename = os.getcwd() + '/' + title.replace(' ','_')+'_EDITED.mp4'
                print ('File: %s' % (output_filename))
                print ('Pwd: %s' % (os.getcwd()))

                if (len(str(cut_start)) > 0 and len(str(cut_end)) > 0):
                    print('Corta pra mim Marcelo Resenha')
                    command = "python3 ./jumpcutter.py --silent_threshold 0.02 --sounded_speed 1 --silent_speed 999999 --frame_margin 2 --frame_rate 30 --frame_quality 1 --url "+str(url)+" --title '"+str(title)+"' --from_time "+str(cut_start)+" --to_time "+str(cut_end)+" --output_file "+output_filename
                    output_file = subprocess.call(command, shell=True)
                else:
                    print('Sem ponto de Corta pra mim Marcelo Resenha')
                    command = "python3 ./jumpcutter.py --silent_threshold 0.02 --sounded_speed 1 --silent_speed 999999 --frame_margin 2 --frame_rate 30 --frame_quality 1 --url "+str(url)+" --title '"+str(title)+"' --output_file "+output_filename
                    output_file = subprocess.call(command, shell=True)
                

                # Insert Opening and Ending and setting output_filename_final
                opening_video = Path('assets/opening.mp4')
                ending_video = Path('assets/ending.mp4')
                output_filename_final = os.getcwd() + '/' + title.replace(' ','_')+'_FINAL.mp4'
                
                print('Concatenando videos de abertura e fechamento')
                if (opening_video.is_file() and ending_video.is_file()):
                    command = "ffmpeg -y -i "+str(opening_video)+" -i "+output_filename+" -i "+str(ending_video)+" -filter_complex '[0:v] [0:a] [1:v] [1:a] [2:v] [2:a] concat=n=3:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' -metadata handler_name='Produzido por @EddieOz youtube.com/eddieoz' -qscale:v 1 -strict -2 -b:v 6000k "+output_filename_final
                    output_file = subprocess.call(command, shell=True)
                print('Gerando thumbs')
                if (output_file == 0):
                    thumb = thumb_generator(output_filename, title)
                    print("Selected thumb: %s" % (thumb))
                    if (thumb != None):
                       upload_video(output_filename, thumb, title, description)
                
                # Move all video files to dir/
                move_files(title)
                row_number+=1
                time.sleep(5)

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(output_filename, reader.line_num, e))

    csvfile.close()

if __name__ == "__main__":
    main()
