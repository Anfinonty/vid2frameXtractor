# WINDOWS ONLY
import tkinter as tk
from tkinter import filedialog
from tkinter import Text
from tkinter import Scrollbar

import webbrowser
import datetime
import time
import threading

import os
import re
import csv

SCENE_DETECT_COMMAND1 = "scenedetect -i \""
SCENE_DETECT_COMMAND2 = "\" detect-adaptive list-scenes save-images detect-content --threshold 27"

# TKinter Globals
GLOBAL_TXT_BOX = None
OPEN_TERMINAL = -1
TERMINAL_CMD = ["", ""]
CURRENT_STEP = 0
CURRENT_VIDEO_FILE = 0

# TKinter Go To Hyperlink
def GoToLink(event):
    link = str(event.widget.tag_names(tk.CURRENT)[1])
    webbrowser.open(link)

#TKinter File Explorer
def GoToFolder(event):
    link = str(event.widget.tag_names(tk.CURRENT)[1])
    webbrowser.open(link)

# Maths, Calculate Frames
def CalcFrames(sec):
    # .decimal *24 ~= to whole num
    dec = sec % 1
    frames = dec * 24
    return round(frames)

# Make Arrays for Frame Numbers and Frame Images
def MakeImagesList(folder_selected):
    # Read files from directory
    files_in_selected_folder = os.listdir(folder_selected)
    frame_numbers_list = []
    images_only_file = []

    try:
        for file in files_in_selected_folder:
            if file.split(".")[1] == "jpg" or file.split(".")[1] == "JPG":
                txt = folder_selected + "/" + file  # directory + filename
                # (<videoname>-Scene-) <Scene Number>-<Scene Sub-Number>  (.jpg)
                fn_regex = "(\d*\-\d*).jpg"
                fn = re.split(fn_regex, file)[1]
                frame_numbers_list.append(fn)
                images_only_file.append(txt)
    except:
        print("Invalid Folder or another Error Occured")

    return frame_numbers_list, images_only_file

# Generate .html
def GenerateHTML(frame_numbers_list, images_list, scene_length_list):
    # sort lists
    frame_numbers_list.sort()
    images_list.sort()

    # html
    # STYLE
    html_style = """
            <style>\n
                body {\n
                    background: #FFFFFFFF;
                }\n\n
                
                table {\n
                    border-spacing: 0px;
                }\n\n

                td, th {\n
                    border: 2px solid black;
                }\n\n

                td {\n
                    font-size:150%;
                }\n\n

                .break_column {\n
                    border: 0px;                
                }\n\n

                .frame_table_img {\n
                    width: 20%;
                }\n\n

                img {\n
                    width: 100%;
                }\n\n
                .center {\n
                    margin-left: auto;
                    margin-right: auto;
                }\n\n

            </style>\n
            """
    # START
    html_txt0 = \
        "<html>\n" \
        "   <head>\n" + \
        html_style + \
        "   <title> Animation Frames </title>\n" \
        "   </head>\n" \
        "   <body>\n" \
        "       <div id='frame_images'>\n"
    # Write custom Table rows
    html_row_list1 = []
    html_row_list2 = []
    i = 0
    page_counter = 0
    for file in images_list:
        html_row_txt = ""
        frame_id = int(frame_numbers_list[i].split("-")[0]) - 1
        html_row_txt += "                  <td>" + str(
            frame_numbers_list[i]) + "</td>\n"  # makes sure its correct alloc
        html_row_txt += "                  <td class='frame_table_img'><img src='file:///" + file + "'" + "></td>\n"
        html_row_txt += "                  <td>            </td>\n"
        html_row_txt += "                  <td>" + str(scene_length_list[frame_id]) + "</td>\n"

        CF_LHS = int(float(scene_length_list[frame_id]))  # left hand side (Seconds)
        CF_RHS = CalcFrames(float(scene_length_list[frame_id]))  # right hand side (Frames)
        html_row_txt += "                  <td>" + str(CF_LHS) + " + " + str(CF_RHS) + "</td>\n"  # sec|frames

        if page_counter < 5:
            html_row_list1.append(html_row_txt)
        elif page_counter < 9:
            html_row_list2.append(html_row_txt)
        else:
            html_row_list2.append(html_row_txt)
            page_counter = -1
        i += 1
        page_counter += 1
    # equalizer
    L = len(html_row_list1)
    M = len(html_row_list2)
    while M < L:
        html_row_list2.append("<td>###-##</td><td class='frame_table_img'></td><td></td><td></td><td></td>\n")
        M += 1
    # make table
    # No.   Frame           Notes           Length (s) || No.   Frame           Notes           Length (s)
    html_txt1 = ""
    new_page = True
    for i in range(0, L, 1):
        if new_page:
            html_txt1 += "           <table class='center'>\n<tbody>\n"  # reopen table
            html_txt1 += "              <tr><th>No.</th><th>Frames</th>" \
                         "<th>" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Notes" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "</th>" \
                         "<th>Length (s)</th><th>sec|frames</th>" \
                         "<th class='break_column'>" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "</th>" \
                         "<th>No.</th><th>Frames</th>" \
                         "<th>" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Notes" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                         "</th>" \
                         "<th>Length (s)</th><th>sec|frames</th></tr>\n"
        new_page = False
        html_txt1 += "              <tr>\n"
        html_txt1 += html_row_list1[i]
        html_txt1 += "<td class='break_column'></td>"
        html_txt1 += html_row_list2[i]
        html_txt1 += "              </tr>\n"
        if ((i + 1) % 5) == 0:
            html_txt1 += "           </tbody>\n</table>\n"  # close table
            html_txt1 += "<P style=\"page-break-before:always\">\n"
            new_page = True

    # END
    html_txt2 = \
        "       </div>\n" + \
        "   </body>\n" + \
        "</html>\n"

    return html_txt0 + html_txt1 + html_txt2

# Write HTML File
def WriteHTML(folder_location, html_txt):
    f = open(folder_location + "/html_images.html", "w")
    f.write(html_txt)
    f.close()

#Get Scene Detect Command From video file and Frames folder location
def GetScenedetectCommand(video_file, frames_folder_location):
    SCENE_DETECT_COMMAND3 = "\" -o \"" + frames_folder_location
    SCENE_DETECT_COMMAND = SCENE_DETECT_COMMAND1 + video_file + SCENE_DETECT_COMMAND3 + SCENE_DETECT_COMMAND2
    return "start \"Extracting Video Frames...\" /wait cmd /c " + SCENE_DETECT_COMMAND

#Get Frames Folder Location From Video File
def GetFramesFolderLocationFromVideoFile(video_file):
    vf = re.split("(.*)\/(.*)\.mp4", video_file)  # divides location and filename
    video_file_location = vf[1]
    video_file_name = vf[2]

    # Make folder to contain Frame Images
    frames_folder_name = "FRAMES_" + video_file_name
    frames_folder_location = video_file_location + "/" + frames_folder_name
    return frames_folder_location

#Execute after clicking on "Choose Video", Returns Video File
def ChooseVideoButtonStart():
    # Pick a video folder
    global CURRENT_STEP
    if CURRENT_STEP != 0:
        return -3

    os.system("scenedetect && echo \"\" > ___")
    if not os.path.isfile("___"):
        return -4
    else:
        os.remove("___")

    os.system("wkhtmltopdf.exe -help && echo \"\" > ___")
    if not os.path.isfile("___"):
        return -5
    else:
        os.remove("___")

    try:
        timenow = str(time.strftime("%H:%M:%S"))
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][…] Choosing Video...\n")
        video_file = filedialog.askopenfilename(filetypes=[("MP4", ".mp4")])
        frames_folder_location = GetFramesFolderLocationFromVideoFile(video_file)
        try:
            os.mkdir(frames_folder_location)
            return video_file
        except:  # return error folder exists
            return -1
    except:
        return -2

# Read CSV && Get Scene Length List
def ReadCSV(csv_location):
    scene_length_list = []
    i = 0
    with open(csv_location, "r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if i > 1:
                scene_length_list.append(row[9])
            else:
                i += 1
    return scene_length_list

# Main
def Main():
    global CURRENT_STEP
    global CURRENT_VIDEO_FILE
    video_file = ChooseVideoButtonStart()
    timenow = str(time.strftime("%H:%M:%S"))
    if video_file == -1:
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][X] File Already Exists.\n", "warning")
    elif video_file == -2:
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][X] Operation Cancelled.\n", "warning")
    elif video_file == -3:
        GLOBAL_TXT_BOX.insert("0.0", "\n[" + timenow + "][X] App is Busy.\n", "warning")
    elif video_file == -4:
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][X] PySceneDetect Is Not Installed.\n", "warning")
    elif video_file == -5:
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][X] wkhtmltopdf.exe Is Not in the Same Folder as this App.\n", "warning")
    else:
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][√] Video Chosen.\n", "success")
        GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][…] Extracting Frames...\n")
        GLOBAL_TXT_BOX.insert("0.0", "\n[" + timenow + "][!] Do Not Exit Manually from the Command Prompt.\n", "warning")
        CURRENT_VIDEO_FILE = video_file
        CURRENT_STEP = 1

# AnimateTasks
# Separate thread to handle cmds
def RunTerminal():
    global OPEN_TERMINAL
    while True:
        if OPEN_TERMINAL > -1:
            os.system(TERMINAL_CMD[OPEN_TERMINAL])
            os.system("echo . > _")
            OPEN_TERMINAL = -1
        time.sleep(1)

#Animates App Terminal
def AnimateTask():
    global OPEN_TERMINAL
    global TERMINAL_CMD
    global CURRENT_STEP
    global CURRENT_VIDEO_FILE
    sec_cnt = 0
    scene_length_list = None
    csv_location = ""
    frames_folder_location = ""
    while True:
        timenow = str(time.strftime("%H:%M:%S"))
        # ---Run Extraction of Frames
        if CURRENT_STEP == 1:
            #open terminal to extract frames
            frames_folder_location = GetFramesFolderLocationFromVideoFile(CURRENT_VIDEO_FILE)
            TERMINAL_CMD[0] = GetScenedetectCommand(CURRENT_VIDEO_FILE, frames_folder_location)
            OPEN_TERMINAL = 0

            #csv_location
            csv_name = re.split("\/FRAMES_(.*)", frames_folder_location)[1] + "-Scenes.csv"
            csv_location = frames_folder_location + "/" + csv_name

            CURRENT_STEP = 2
        # ---Wait For CSV
        if CURRENT_STEP == 2:
            if os.path.isfile("_"):
                os.remove("_")
                try:
                    scene_length_list = ReadCSV(csv_location)  # Read CSV
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][√] Frames Extracted." + " (" + str(sec_cnt) + "s)\n", "success")
                    CURRENT_STEP = 3
                except:
                    CURRENT_STEP = 0
                    CURRENT_VIDEO_FILE = ""
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][X] Operation Interrupted.\n", "warning")
                sec_cnt = 0
            else:
                sec_cnt += 1
                GLOBAL_TXT_BOX.insert("0.0", ".")
                if sec_cnt % 60 == 0:
                    GLOBAL_TXT_BOX.insert("0.0", "\n")
        # --- Write HTML
        elif CURRENT_STEP == 3:
            frame_numbers_list, images_list = MakeImagesList(frames_folder_location)  # Get Frame-no. & Frame-images txt
            html_txt = GenerateHTML(frame_numbers_list, images_list, scene_length_list) #HTML Txt from above data

            GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][…] Writing HTML...\n")
            WriteHTML(frames_folder_location, html_txt)  # Write HTML File
            GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][√] HTML Written.\n", "success")
            CURRENT_STEP = 4
        # --- Write PDF
        elif CURRENT_STEP == 4:
            GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][…] Writing PDF...\n")
            GLOBAL_TXT_BOX.insert("0.0", "\n[" + timenow + "][!] Do Not Exit Manually from the Command Prompt.\n", "warning")
            command = "start \"Writing PDF...\" /wait cmd /c \"" \
                      ".\wkhtmltopdf.exe -n " \
                      "--enable-local-file-access " \
                      "--page-size \"A2\" " \
                      "--orientation \"landscape\" " \
                      "--disable-smart-shrinking " \
                      "--no-pdf-compression " \
                      "--footer-right \"Page [page] to [topage]\" " \
                      "--encoding \"UTF-8\" " + \
                      "\"file:///" + frames_folder_location + "/html_images.html\" " + \
                      "\"" + frames_folder_location + "/html_images.pdf\" && echo . > __\""
            TERMINAL_CMD[1] = command
            OPEN_TERMINAL = 1
            CURRENT_STEP = 5
        # --- Wait For PDF
        elif CURRENT_STEP == 5:
            if os.path.isfile("_"):
                if os.path.isfile("__"):
                    os.remove("__")
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][√] PDF Written." + " (" + str(sec_cnt) + "s)\n", "success")
                    f = "file:///" + frames_folder_location
                    g = f + "/html_images.pdf"
                    GLOBAL_TXT_BOX.insert("0.0", (f + "\n"), ("link", str(f)))
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "] Go To Folder: ")
                    GLOBAL_TXT_BOX.insert("0.0", (g + "\n"), ("link", str(g)))
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "] Go To PDF: ")
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][√] Finished.\n", "success")
                else:
                    GLOBAL_TXT_BOX.insert("0.0", "[" + timenow + "][X] Operation Interrupted.\n", "warning")
                os.remove("_")
                CURRENT_STEP = 0
                CURRENT_VIDEO_FILE = ""
                sec_cnt = 0
            else:
                sec_cnt += 1
                GLOBAL_TXT_BOX.insert("0.0", ".")
                if sec_cnt % 60 == 0:
                    GLOBAL_TXT_BOX.insert("0.0", "\n")
        time.sleep(1)

#RUN
root = tk.Tk()
root.title("Video Frames Extractor v1.3 (WINDOWS)")

# resolution
GR_WIDTH = 640
GR_HEIGHT = 480
root.geometry(str(GR_WIDTH) + "x" + str(GR_HEIGHT))

# Text Box Logging
GLOBAL_TXT_BOX = Text(root, width=int(GR_WIDTH / 16 + 20), height=int(GR_HEIGHT / 16 - 4))
GLOBAL_TXT_BOX.place(x=12 + 96, y=8)

GLOBAL_TXT_BOX_scrollbar = Scrollbar(root)
GLOBAL_TXT_BOX_scrollbar.place(x=int(GR_WIDTH - 40), y=8)

# Attach textbox to scrollbar
GLOBAL_TXT_BOX.config(yscrollcommand=GLOBAL_TXT_BOX_scrollbar.set)
GLOBAL_TXT_BOX_scrollbar.config(command=GLOBAL_TXT_BOX.yview)

# Formats
GLOBAL_TXT_BOX.tag_config("success", foreground="green")
GLOBAL_TXT_BOX.tag_config("warning", foreground="red")
GLOBAL_TXT_BOX.tag_config("link", foreground="blue")
GLOBAL_TXT_BOX.tag_bind("link", "<Button-1>", GoToLink)

# Button to search for Video File
button_find_video = tk.Button(root, text="Choose Video", command=Main)  # lambda: Main(GLOBAL_TXT_BOX))
button_find_video.place(x=8, y=8)

# Welcome Message
timenow = str(time.strftime("%H:%M:%S"))
lnk1 = "https://scenedetect.com/en/latest/download/"
lnk2 = "https://wkhtmltopdf.org/downloads.html"
GLOBAL_TXT_BOX.insert("0.0", "\n\nToday is " + str(datetime.date.today()) + ".\nThe Time Now is " + timenow +".\n")
GLOBAL_TXT_BOX.insert("0.0", "\nVideoFramesExtractor v1.3 (Windows) By Anfinonty for Ginyoagoldie Dec-27-2022")
GLOBAL_TXT_BOX.insert("0.0", lnk1+"\n",("link", str(lnk1)))
GLOBAL_TXT_BOX.insert("0.0", "PySceneDetect: ")
GLOBAL_TXT_BOX.insert("0.0", lnk2+"\n", ("link", str(lnk2)))
GLOBAL_TXT_BOX.insert("0.0", "\nwkhtmltopdf: ")

# START
if os.path.isfile("_"):
    os.remove("_")
if os.path.isfile("__"):
    os.remove("__")
if os.path.isfile("___"):
    os.remove("___")

thread1 = threading.Thread(target=AnimateTask)
thread1.daemon = True #make AnimateTask terminate when the user exits the window
thread1.start()
thread2 = threading.Thread(target=RunTerminal)
thread2.daemon = True
thread2.start()
root.mainloop()
