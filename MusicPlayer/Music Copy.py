import os
from io import BytesIO
import PIL.Image as CoverArt
import tinytag
from sys import platform
import threading
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from mutagen.id3 import ID3

from tkinter import ttk
from ttkthemes import themed_tk as tk

from mutagen.mp3 import MP3
from mutagen import File
from pygame import mixer

root = tk.ThemedTk()
root.get_themes()  # Returns a list of all themes that can be set
print(sys.platform)

new_canvas = Canvas(root, width=200, height=200)

if platform == "Mac OS X ":
    root.set_theme("aqua")
elif platform == "darwin":
    root.set_theme("clam")
elif platform == "Win10":
    root.set_theme("xpnative")        # Sets an available theme


# Fonts - Arial (corresponds to Helvetica), Courier New (Courier), Comic Sans MS, Fixedsys,
# MS Sans Serif, MS Serif, Symbol, System, Times New Roman (Times), and Verdana
#
# Styles - normal, bold, roman, italic, underline, and overstrike.

statusbar = ttk.Label(root, text="Welcome to Melody", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side=BOTTOM, fill=X)

# Create the menu_bar
menuBar = Menu(root)
root.config(menu=menuBar)

# Create the submenu

subMenu = Menu(menuBar, tearoff=0)

playlist = []


# playlist - contains the full path + filename
# playlistbox - contains just the filename
# Fullpath + filename is required to play the music inside play_music load function

def browse_file():
    global filename_path
    filename_path = filedialog.askopenfilename()
    add_to_playlist(filename_path)
    mixer.music.queue(filename_path)


def add_to_playlist(filename):
    global index
    filename = os.path.basename(filename)
    index = 0
    if filename.endswith(".mp3"):
        playlistbox.insert(index, filename)
        playlist.insert(index, filename_path)
        index += 1
    else:
        tkinter.messagebox.showerror('File not found', 'Melody could not load the file. Please check again.')


def add_directory_to_playlist():
    try:
        global index
        directory = filedialog.askdirectory()
        os.chdir(directory)
        index = 0
        for files in os.listdir(directory):
            if files.endswith(".mp3"):
                playlistbox.insert(index, files)
                playlist.insert(index, files)
                index += 1

    except:
        tkinter.messagebox.showerror('File not found', 'Melody could not load the directory. Please check again.')


menuBar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)


def about_us():
    tkinter.messagebox.showinfo('About Melody', 'This is a music player build using Python Tkinter by @attreyabhatt')


subMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About Us", command=about_us)

mixer.init()  # initializing the mixer

root.title("Melody")
root.iconbitmap(r'Images\melody.ico')

# Root Window - StatusBar, LeftFrame, RightFrame
# LeftFrame - The listbox (playlist)
# RightFrame - TopFrame,MiddleFrame and the BottomFrame

leftFrame = Frame(root)
leftFrame.pack(side=LEFT, padx=30, pady=30)

playlistbox = Listbox(leftFrame)
playlistbox.pack()

addBtn = ttk.Button(leftFrame, text="+ Add", command=browse_file)
addBtn.pack(side=LEFT)

director_Button = ttk.Button(leftFrame, text="+ Playlist", command=add_directory_to_playlist)
director_Button.pack(side=LEFT)


def del_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)


delBtn = ttk.Button(leftFrame, text="- Del", command=del_song)
delBtn.pack(side=LEFT)

rightFrame = Frame(root)
rightFrame.pack(pady=30)

topFrame = Frame(rightFrame)
topFrame.pack()

titleArtist = ttk.Label(topFrame, text="Title - Artist")
titleArtist.pack(pady=5)

trackAlbum = ttk.Label(topFrame, text="Track - Album")
trackAlbum.pack(pady=5)

length_label = ttk.Label(topFrame, text='Total Length : --:--')
length_label.pack(pady=5)

current_time_label = ttk.Label(topFrame, text='Current Time : --:--', relief=GROOVE)
current_time_label.pack()


def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        artist = audio['TPE1']
        title = audio['TIT2']
        track = audio["TRCK"]
        album = audio["TALB"]
        pict = audio['APIC']
        # titleArtist['text'] = artist + " - " + title
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    length_label['text'] = "Total Length" + ' - ' + timeformat

    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            current_time_label['text'] = "Current Time" + ' - ' + timeformat
            time.sleep(1)
            current_time += 1


def play_music():
    global paused

    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            selected_song = int(selected_song[0])
            play_it = playlist[selected_song]
            mixer.music.load(play_it)
            mixer.music.play()
            audio = MP3(play_it)
            artist = (audio['TPE1'][0])
            title = (audio['TIT2'][0])
            track = (audio["TRCK"][0])
            album = (audio["TALB"][0])
            # pict = (audio['APIC'][0].data)
            # imPIL = CoverArt.open(BytesIO(pict))
            # im = PhotoImage(imPIL)
            # coverArt = ttk.Label(topFrame, image=im)
            # coverArt.pack()
            cover = File(play_it)
            artwork = cover.tags["APIC:"].data
            with open('image.jpg', 'wb') as img:
                img.write(artwork)
            art = ttk.Label(topFrame)
            image = PhotoImage(file="image.jpg")
            art['image'] = image
            art.pack(pady=20)

            titleArtist['text'] = artist + " - " + title
            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
            trackAlbum['text'] = track + " - " + album

            show_details(play_it)
        except:
            tkinter.messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')

# Added by Steffen Hayes
# Creating a command to play next or go back a song in a directory for the playlist


def next_song():
    try:
        global index
        selected_song = playlistbox.curselection()
        selected_song = int(selected_song[0])
        play_it = playlist[selected_song]
        mixer.music.load(play_it)
        play_music()
        statusbar['text'] = "Playing Next Song"
    except:
        tkinter.messagebox.showerror('File not found', 'Melody could not load the next file. Please check again.')


def prev_song():
    try:
        global index
        index -= 1
        mixer.music.load(playlist)
        mixer.music.play()
        statusbar['text'] = "Playing Previous Song"
    except:
        tkinter.messagebox.showerror('File not found', 'Melody could not load the previous file. Please check again.')


def repeat_music():
    play_music()
    statusbar['text'] = "Restarting Music"


def stop_music():
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"


paused = FALSE


def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"


def rewind_music():
    play_music()
    statusbar['text'] = "Rewinding Music"


def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1


muted = FALSE


def mute_music():
    global muted
    if muted:  # unmute the music
        mixer.music.set_volume(0.5)
        volumeBtn.configure(image=volumePhoto)
        scale.set(50)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)
        muted = TRUE


middleframe = Frame(rightFrame)
middleframe.pack(pady=30, padx=30)

playPhoto = PhotoImage(file='Images/play.png')
playBtn = ttk.Button(middleframe, image=playPhoto, command=play_music)
playBtn.grid(row=0, column=0, padx=10)

nextPhoto = PhotoImage(file="Images/next.png")
nextBtn = ttk.Button(middleframe, image=nextPhoto, command=next_song)
nextBtn.grid(row=1, column=0, padx=10)

prevPhoto = PhotoImage(file="Images/back.png")
nextBtn = ttk.Button(middleframe, image=prevPhoto, command=prev_song)
nextBtn.grid(row=1, column=1, padx=10)

repeatPhoto = PhotoImage(file="Images/repeat.png")
nextBtn = ttk.Button(middleframe, image=repeatPhoto, command=repeat_music)
nextBtn.grid(row=1, column=2, padx=10)

stopPhoto = PhotoImage(file='Images/stop.png')
stopBtn = ttk.Button(middleframe, image=stopPhoto, command=stop_music)
stopBtn.grid(row=0, column=1, padx=10)

pausePhoto = PhotoImage(file='Images/pause.png')
pauseBtn = ttk.Button(middleframe, image=pausePhoto, command=pause_music)
pauseBtn.grid(row=0, column=2, padx=10)

# Bottom Frame for volume, rewind, mute etc.

bottomframe = Frame(rightFrame)
bottomframe.pack()

rewindPhoto = PhotoImage(file='Images/rewind.png')
rewindBtn = ttk.Button(bottomframe, image=rewindPhoto, command=rewind_music)
rewindBtn.grid(row=0, column=0)

mutePhoto = PhotoImage(file='Images/mute.png')
volumePhoto = PhotoImage(file='Images/volume.png')
volumeBtn = ttk.Button(bottomframe, image=volumePhoto, command=mute_music)
volumeBtn.grid(row=0, column=1)

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
scale.grid(row=0, column=2, pady=15, padx=30)

new_canvas.pack()
def on_closing():
    stop_music()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
