import shutil
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import ImageTk,Image
from pathlib import Path 
import collage_maker as maker

# db import
from saver import Saver

# program constants
DB_SCHEME = 'mongodb://localhost:27017'


# Costumized exception part

class NotValidNumberError (Exception):
    pass

class NotValidPath(Exception):
    pass

# raise err if num is not digit  and 0<num <8
def is_valid_num(num):
    try:
        i = int(num) 
        if (i < 1) or (i >7 ):
            raise NotValidNumberError
    except:
        raise NotValidNumberError()





class Browser ():
    '''
        Class for create the GUI for photos organization.The user enter the number and names of
        sub directories to copy photos into, and while browsing the directory, photo will be
        displayed as thumbnails, by clicking on the desired button the photowill be copied to the fit directory
    '''

    def __init__(self, saver = Saver(DB_SCHEME)):

        self.root = tk.Tk() 
        self.root.title('Photo Browser')
        self.config_data = {'bg':'#B8E0FE', 'width':500, 'height':450, 'font': ('Arial 12')}         # default configuration for widgets
        self.root.geometry('500x450+100+100')
        self.search_mode = False
        # temp dir for thumbnails
        self.thumbnail_dir = Path((Path().cwd() / 'Thumbnails'))
        # table to track number of copied photos every new folder
        self.TOTAL = {}
        # variablle to track the widgets in  the future
        self.msg = ''
        self.entries = []
        self.labels = []
        self.btn_names = []
        self.names=['Trash']
        self.next_bt =[]
        self.img_list=[]
        self.dir_to_organaize = ''
        self.num_of_dir = 1
        self.i = 0
        self.saver = saver
        self.im_size = (200,200)            # default
        # list to contain all selected photo
        self.chosen_pathes = set()
        # for testing mode
        self.testing = False

    def create_frames(self):
        '''
            Create the app's layouts. This method should be called before any other method which run any screen
        '''
        # the screen is composed from 3 parts, rule diffrent part of the widgets
        self.up_frame =tk.Frame(master =self.root,width=self.config_data['width'], height = 300, bg = self.config_data['bg'])
        self.mid_frame =tk.Frame(master =self.root,width=self.config_data['width'], height = 100, bg = self.config_data['bg'])
        self.bottom_frame =tk.Frame(master =self.root,width=self.config_data['width'], height = 50, bg = self.config_data['bg'])
        # grid all layouts widgets
        self.up_frame.grid(row = 0, column = 0, columnspan = 2,padx = 0)
        self.mid_frame.grid(row = 1, column = 0, columnspan = 2,padx = 0)
        self.bottom_frame.grid(row = 2, column = 0, columnspan = 2, padx = 0)
        self.mid_frame.rowconfigure([0,1], minsize=35)
        self.bottom_frame.columnconfigure([0], minsize = self.config_data['width'])
        # set the size of the masters fix
        self.mid_frame.grid_propagate(False)
        self.up_frame.grid_propagate(False)
        self.bottom_frame.grid_propagate(False)               

    def run(self):
        '''
            Initialize the app and config the initial display. In this Scren the user can choose to 
            search photos by tag or organaize specific folder.
        '''
        # add the openning message 
        self.msg = tk.Label(master = self.up_frame,bg = '#B8E0FE', font="Times 16 bold", 
        text = 'Welcome to the Photo Browser.\nYou can organize photos directory \nor search for photos by tag',
            justify=tk.LEFT)
        self.msg.grid(row =0 , column = 0, padx  = 20, pady = 30, sticky = 'w', columnspan = 2)
        # add buutons to choose if search or oranaize
        self.btn_names.append(tk.Button(master=self.mid_frame, text = 'Select folder\nto organize', command = self.organiaze_opening))
        self.btn_names.append(tk.Button(master=self.mid_frame, text = 'Search by tags', command = self.search_opening))
        for i in range(len(self.btn_names)):
            self.btn_names[i].grid(row = 0, column = i, padx = (40*(i+1), 0), pady = 10)
            self.btn_names[i].config(fg = 'white', bg = '#0D4DCD', justify=tk.CENTER,width = 20, height = 3)
            
        # add temp directory for thumbnails
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    #########################################################
    #                                                       #
    # Search by tag section                                 #   
    #                                                       #
    #########################################################
    
    def search_opening(self, redirect = False):
        '''
            App's search-by-tag option oppening screen. Clean the app's screan and add entry to insert the tag.
        '''
        # set app mode
        self.search_mode = True
        self.destroy_children(self.mid_frame, self.btn_names)
        # list for containing pathe of chosen photos
        self.msg['text'] =  'Welcome to the images search.\nInsert tag to filter photos\n'
        # add enteries to insertt tags (1 is default. cna be modified to more than one tag)
        for i in range(1):
            e = tk.Entry(master=self.up_frame)
            l = tk.Label(master=self.up_frame, bg = self.config_data['bg'])
            if i == 0:
                l['text'] = 'Tag to filter photos'
            else:
                l['text'] = 'Tag to filter photos (optional)'
            e.grid(row = i+1, column = 1, padx = 10, pady =10, sticky = 'w')
            l.grid(row = i+1, column = 0, padx = (20,0) , pady =10, sticky = 'w')
            self.entries.append(e)
            self.labels.append(l)
        self.next_bt.append(tk.Button(master=self.bottom_frame, text='next', command=self.get_tag_name))
        self.next_bt[0].grid(row = 0, column=0,pady = 10,padx = 20, sticky = 'e')

    def get_tag_name(self):
        '''
            Get the user tag, and try to get the matches photos from db
        '''
        # prevents duplicate in case of more the 1 tag
        tags = {e.get() for e in self.entries}
        if tags == {''}:
            self.search_opening(redirect= True)
        else:
            self.img_list = self.saver.get_tag_path(tags.pop())
            if self.img_list:
                self.destroy_children(self.up_frame)
                self.canvas1 = tk.Canvas(master = self.up_frame,width=self.config_data['width'], height = 300, bg='#B8E0FE',highlightthickness=0)
                self.r_symbol = ImageTk.PhotoImage(Image.open('right.png'))
                self.l_symbol =ImageTk.PhotoImage(Image.open('left.png')) 
                self.show_photo()
            else:
                self.msg['text'] = 'There  are no photos matches\n the search tag'

    #########################################################
    #                                                       #
    # Organaize folder section                              #   
    #                                                       #
    #########################################################
    
    def organiaze_opening(self, redirect = False) :
        '''
            Organaize folder option -  openning screen
        '''
        # set app mode
        self.search_mode = False
        self.destroy_children(self.mid_frame, self.btn_names)
        self.msg = 'Welcome to the image browser.\nInsert the nuber of the directory\nto sort the images'
        self.btn_names.append(tk.Button(master = self.mid_frame, text = 'Click for chooce direcroty', command = self.open_file_dialog))
        self.btn_names[0].grid(row = 0, column = 0, padx  = 100, pady=3, sticky = 'w')
        if self.dir_to_organaize != '':
            self.labels.insert(0,(tk.Label(master= self.mid_frame, text = 'You have choce:\n'+self.dir_to_organaize,
                 bg = self.config_data['bg'], font = self.config_data['font'])))
            self.labels[0].grid(row = 1, column = 0, padx = 100, pady = 6, sticky='w')  
        if redirect:
            label = tk.Label(master=self.mid_frame, text='Please choose directory', font ='Arial 12', fg = 'Red' , bg = self.config_data['bg'])
            label.grid(row = 1, column = 0,  padx  = 100, pady=3,sticky = 'w')
        # add the next button
        self.next_bt.append(tk.Button(master = self.bottom_frame,text='Next', command=self.get_dir_number))
        self.next_bt[0].grid(row = 0, column=0,pady = 10,padx = 20, sticky = 'e')
    
    def get_dir_number(self):
        '''
            Create antery to get the number of desination folder to copy there the photos from original folder            
        '''
        if self.dir_to_organaize == '':
            self.organiaze_opening(redirect=True)

        else:
            self.destroy_children(self.mid_frame, self.labels, self.btn_names)     
            l = tk.Label(master=self.up_frame, text = 'Enter the number of sub-folders\nyou'
                    ' want to be created:\n(trash foder will be added automaticly', bg = self.config_data['bg'],
                     font = self.config_data['font'], justify = tk.LEFT)
            l.grid(row = 2, column = 0)
            self.entries.append(tk.Entry(master = self.mid_frame, bg = 'white'))
            self.labels.append(tk.Label(self.mid_frame, text ='Please enter number between 1-7',
                bg= '#B8E0FE', font='Ariel 12', justify=tk.LEFT))   
            for i in range(len(self.entries)):
                self.labels[i].grid(row = i, column = 0,padx = 10, sticky = 'w')
                self.entries[i].grid(row = i, column = 1, padx = 10,sticky = 'w')
            self.next_bt[0]['command'] = self.get_folders_name
    
    def get_folders_name(self):
        '''
            Craete enteries to get the new folders name
        '''
        try:
            # if testing mode num_of_dir is determinded beforehand, so we dont need to take this arg from user
            if not self.testing:            
                is_valid_num(self.entries[0].get())
                self.num_of_dir = int(self.entries[0].get())
            
            # clear previous screen
            self.destroy_children(self.up_frame)
            self.destroy_children(self.mid_frame, self.entries, self.labels)
            #  create enteries to colllect directories names
            for j in range(int(self.num_of_dir)):
                entry = tk.Entry(master = self.up_frame)
                self.entries.append(entry)
                entry.grid(row = j, column=1,padx = 30, pady = 5)              
                label = tk.Label(master = self.up_frame, text = 'Enter the folder name:' , bg= '#B8E0FE', font='Ariel 12')
                self.labels.append(label)
                label.grid(row = j, column= 0, padx = 30, pady = 5)
            
            self.next_bt[0]['command'] = self.show_names
        
        except NotValidNumberError: 
            label = tk.Label(master=self.mid_frame, text='Please enter number btween 1 to 7', font ='Arial 12', fg = 'Red' )
            label.grid(row = 1, column = 0,  padx  = (100,0), pady=3, columnspan = 2)
            
    def show_names(self):
        ''' 
            Show the names of folders, and create the folder at current directory
        '''        
        # collect the names of dirs
        if not self.testing:
            for e in self.entries:
                self.names.append(e.get())
        # clear the screen display
        self.destroy_children(self.up_frame, self.entries, self.labels)
        all_names = '\n  - '.join(self.names)
        # reset the msg widet 
        self.msg = tk.Label(master = self.up_frame, text ='You chose the next directories:\n  - '+all_names, font = self.config_data['font'],
                bg = self.config_data['bg'], justify = tk.LEFT)
        self.msg.grid(row = 0, column = 0,padx = 20, pady =40, sticky = 'nsew')
        # create the directories
        for name in self.names:
            self.create_dir(Path.cwd(), name)
            self.TOTAL[name] = 0
        # get the files in the selected folder
        self.img_list = [f for f in Path(self.dir_to_organaize).iterdir() if (not f.is_dir())]
        self.next_bt[0]['command']= self.show_photo
        
            
    def show_photo(self, rotation=0):
        '''
            Iterate over img_list and display the photos
        '''
        i = self.i
        # set next btn to be used as finish btn
        self.next_bt[0]['command'] = self.finish_screen
        self.next_bt[0]['text'] = 'Finish'
        # create canvas to display thumbnails
        if i == 0:
            self.destroy_children(self.up_frame, self.labels, self.entries)
            self.canvas1 = tk.Canvas(master = self.up_frame,width=self.config_data['width'], height = 300, bg='#B8E0FE',highlightthickness=0)    
            self.canvas1.grid(row = 0, column = 0)
        # in case of folder organization, create the btn to be selected to copy the photo
        if not self.search_mode:
            self.create_tags_btn()
            self.create_folder_btn(rotation, i)
        # in case of search
        else:
            self.canvas1.delete('outline')
            self.create_navigate_btn()
            self.draw_outline(i)
            self.create_select_btn(i, rotation)
        # display the Ith photo
        if i < len(self.img_list):
            try:
                out = self.create_thumbnail(Path(self.img_list[i]), rotation)
                # display thumbnail
                image1 = ImageTk.PhotoImage(Image.open(str(out)))
                self.canvas1.create_image(self.config_data['width']/2, 150, image=image1)
                self.canvas1.image = image1  
                self.i += 1
            # case file is not an image
            except IOError:
                self.i += 1
                self.show_photo()    
        # there is no more files to handle 
        else:           
            self.finish_screen()     

    def finish_screen(self):    
        '''
            The last screen of the app, show the number of photos in evry new directory, or allow to create collage
            from selected photos
        '''
        # clear the screen        
        self.destroy_children(self.canvas1)
        self.destroy_children(self.up_frame)
        self.destroy_children(self.mid_frame)
        self.destroy_children(self.bottom_frame, self.next_bt)
        if self.search_mode:            
            self.msg = tk.Label(master = self.up_frame,text = '', bg = self.config_data['bg'])
            self.msg.grid (row = 1, column = 0, padx = 150, pady =30)
            # temporary directory to store selected photos
            dir = self.create_dir(Path.cwd(), 'collage_photos')
            for p in self.chosen_pathes:
                shutil.copy(Path(p),Path(dir))    
            self.bar = ttk.Progressbar(master=self.up_frame, orient = tk.HORIZONTAL, length  = 300, mode='determinate')
            self.bar.grid(row = 0, column = 0, padx = 100, pady=20)
            create_btn = tk.Button(master=self.up_frame, text = 'Create Collage',
             command= lambda x = dir: self.create_collage(dir))
            create_btn.grid(row = 2, column = 0, padx =150, pady = 20)
            
        else:    
            self.up_frame.rowconfigure(2, minsize = 20)
            self.up_frame.columnconfigure(3, minsize =50)
            # create new grid for up frame to draw the summerize table
            c1 = tk.Canvas(master= self.up_frame, width= self.config_data['width'], height=20 , bg = self.config_data['bg'],highlightthickness=0)
            c1.grid(row = 0, column = 0, columnspan = 3 )
            c2 =  tk.Canvas(master= self.up_frame, width= 50, height=280 ,bg =  self.config_data['bg'] ,highlightthickness=0 )
            c3 =  tk.Canvas(master= self.up_frame, width= 400, height=280 ,bg = self.config_data['bg'],highlightthickness=0)
            c4 =  tk.Canvas(master= self.up_frame, width= 50, height=280 ,bg = self.config_data['bg'],highlightthickness=0)
            c2.grid(row = 1, column = 0)
            c3.grid(row = 1, column = 1)
            c4.grid(row = 1, column = 2)
            c3.grid_propagate(False)
            self.msg = tk.Label(master = c3, text = 'Final results:\n number of the images at every destination directory',
                font = ('Arial', 12), bg = self.config_data['bg'])
            self.msg.grid(row =0, column= 0, columnspan = 2, pady = (20,20))
            if not self.testing:
                # Note! this increment is becouse in test mode num_of_dir include trash dir, but not in prod mode
                self.num_of_dir += 1    
            self.draw_table(int(self.num_of_dir)+1,2,c3)
        # set the finish button to be used as exit
        self.next_bt.append(tk.Button(master = self.bottom_frame,text='Exit', command=self.exit_screen))
        self.next_bt[0].grid(row = 0, column=0,pady = 10,padx = 20, sticky = 'e')
        
    def exit_screen(self):
        '''
            Terminate the app
        '''
        shutil.rmtree(self.thumbnail_dir)
        self.root.destroy()
        
    def run_window(self, name,testing=False):
        '''for testing propose, allow to run specific window directly, by passing window name'''
        self.testing = testing
        if self.testing:
            self.test_data()
        self.create_frames()
        
        getattr(Browser, name)(self)
        self.root.mainloop()
        
    
    #########################################################################
    #                                                                       #
    # Class methods to handle backend actions (rotate, copy, undo....)      #
    #                                                                       #
    #########################################################################
    
    def rotate(self, rotation, mode='organaize'):
        '''
            Rotate photo 90 degrees counter clockwise,  by increment rotation counter by 1. 
            The cahnge in the photo oraintation is actualy made in the create_thumbnail method,
            which get the rotation parameter and accunt it while creating the thumbnail
        '''
        rotation += 1
        self.i -= 1
        self.show_photo(rotation%4)
        

    def process_photo(self, src, dest):
        '''
            Copy photo from dir_to_organaize to the target dir chose by user, and store its accoiciated tags in db
        '''
        tags = []
        for e in self.entries:
            if e.get()!='':
                tags.append(e.get())
            e.delete(0,tk.END)
        self.saver.save(str(src), *tags)
        shutil.copy(Path(src),Path(dest))    
        # update total
        self.TOTAL[dest.name] += 1
        # return to next image
        self.show_photo()
        
    
    def create_dir(self, parent_dir, name):
        '''
            Create the folder determinerd by user
        '''
        new_dir = Path(parent_dir) / name
        Path(new_dir).mkdir(parents=True, exist_ok=True)
        return new_dir

    def create_thumbnail(self, img_path, rotation=0):
        '''
            Create the thumbnail photo to be displayd within the app screen
        '''
        img_name = str(img_path.stem)
        thumbnail_name = img_name+'_thumbnail.jpg'
        path_to_save = Path(self.thumbnail_dir)/ thumbnail_name
        im = Image.open(img_path)
        im = im.convert('RGB')
        # rotate if needed
        im  = im.rotate(90*rotation, expand=True)
        im.thumbnail((200,300), Image.ANTIALIAS)
        # size is needed in case of selection 
        self.im_size = im.size
        im.save(str(path_to_save), "JPEG")
        return path_to_save
    
    def draw_table(self, r, c, master):
        ''' 
            Create the tabel to summerize the app data
        '''
        self.entries.clear()     
        for i in range(r): 
            for j in range(c): 
                e = tk.Entry(master = master, width=20, fg='Black', 
                               font=('Arial',12))
                self.entries.append(e)
                e.grid(row=i+1, column=j) 
        # write the data to table
        total_values = list(self.TOTAL.values())
        for i in range (1, r):
            self.entries[(2*i)].insert(0, self.names[i-1])
            self.entries[(2*i)+1].insert(0, total_values[i-1])
        self.entries[0].insert(0,'Directory name')
        self.entries[1].insert(0,'Number of images')
        # table headers style
        for i in range(2):
            self.entries[i].config(fg='blue', font =('Arial',12, 'bold'))            

    def test_data(self):
        '''
            Set the app in test mode: set all the relevant variables to allow test specific methid without user input
        '''
        self.root.title('Photo Browser TESTING MODE')    
        self.dir_to_organaize = r'C:\Users\elkana\Documents\elkana\python\manage'
        self.names += ['airplanes', 'cars', 'robots', 'other','a', 'dk']
        self.num_of_dir = len(self.names)
        self.img_list = [f for f in Path(self.dir_to_organaize).iterdir() if (not f.is_dir())]
        self.next_bt.append(tk.Button(master = self.bottom_frame,text='Next', command=self.get_dir_number))
        self.next_bt[0].grid(row = 0, column=0,pady = 10,padx = 20, sticky = 'e')
        for name in self.names:
            self.create_dir(Path.cwd(), name)
            self.TOTAL[name] = 0

    def open_file_dialog(self):
        '''
            Open file dialog box and set the dir_to_organaize to the selected directory
        '''
        self.dir_to_organaize = filedialog.askdirectory(initialdir = '/')
        self.organiaze_opening(redirect=False)
    

    def select(self,path, rotation):
        '''
            Mark photo as selected: insert photo path to list 
        '''
        self.chosen_pathes.add(path)
        self.i -= 1
        self.show_photo(rotation)
    
    def undo_select(self,path,rotation ):
        '''
            Unmark photo as selected    
        '''
        try:
            self.chosen_pathes.remove(path)
        except KeyError:
            pass
        finally:
            self.i -= 1
            self.show_photo(rotation)
    
    def prev(self):
        '''
            Go back to previous photo 
        '''
        self.i -= 2
        if self.i <0:
            self.i = 0
        self.show_photo()
        
    def create_tags_btn(self):
        '''
            Craete the tags widgets to enable user tagging photos
        '''
        self.destroy_children(self.mid_frame)
        # add tags
        self.labels.append(tk.Label(master=self.bottom_frame, text = 'Add Tags (location, name, etc.):'))
        self.entries.append(tk.Entry(master=self.bottom_frame))
        self.entries.append(tk.Entry(master=self.bottom_frame))
        self.labels[0].grid(row = 0, column = 0, padx = 4, pady = 5,sticky = 'w')
        self.entries[0].grid(row = 0, column = 1, padx = 4, pady = 5,sticky = 'w')
        self.entries[1].grid(row = 0, column = 2, padx = 4, pady = 5,sticky = 'w')
        self.next_bt[0].grid(row = 0, column=3,pady = 10,padx = 4, sticky = 'e')
        #self.bottom_frame.columnconfigure([3], minsize = self.config_data['width']//4)
        self.bottom_frame.columnconfigure([0,1,2], minsize = 0)
        
    def create_folder_btn(self, rotation, i):
        '''
            Create the button for every folder named by user. By cliciking on button, the photo 
            will be proccesed: copy to destination folder, and stored it tags
        '''
        btns_max_len = len(max(self.names, key=len))
        self.mid_frame.columnconfigure([0,1,2,3,4,5], minsize = 30)
        l = tk.Label(master= self.mid_frame,text = 'click to\ncopy photo', justify = tk.LEFT,
            bg = self.config_data['bg'],font = self.config_data['font'])
        l.grid(row = 0, column=0, rowspan = 2, padx = (10,0))

        rot_btn = tk.Button(master= self.mid_frame, text = 'Rotate', command = lambda x = rotation: self.rotate(rotation=x),
                    bg = '#F38181')
        rot_btn.grid(row = 0, column = 5, rowspan = 2, padx = (10,0))
        for j, n in enumerate(self.names):
            dest = Path.cwd() / n
            btn = tk.Button(master= self.mid_frame, width = btns_max_len, text = n, command = lambda x=dest:self.process_photo(Path(self.img_list[i]), Path(x)))
            self.btn_names.append(btn)
            btn.grid(row = j//4, column= (j%4)+1,padx = (3, 0), pady  = 10)
    
    
    def create_navigate_btn(self):
        ''' 
            Create the next photo / prev photo to navigate photos, in search mode
        '''
        next_im_bt = tk.Button(image = self.r_symbol,command = self.show_photo)
        prev_bt = tk.Button(image=self.l_symbol, command = self.prev)             
        self.canvas1.create_window(self.config_data['width']*(7/8), 250, window=next_im_bt)
        self.canvas1.create_window(self.config_data['width']*(1/8), 250, window=prev_bt)

    def create_select_btn(self, i, rotation):
        '''
            Create the btn to select / undo selection photo in search mode
        '''
        select_bt = tk.Button(master=self.mid_frame, text = 'Select Photo', 
            command = lambda x = self.img_list[i], y = rotation: self.select(x,y) )
        rotate = tk.Button(master=self.mid_frame,text = 'Rotate',
            command = lambda x = rotation, y='tags': self.rotate(x, mode=y))
        undo_select = tk.Button(master=self.mid_frame, text = 'Undo selection', 
            command = lambda x=self.img_list[i], y=rotation: self.undo_select(x,y))
        rotate.grid(row = 0, column = 1, sticky = 'n')
        select_bt.grid(row = 0, column =2,sticky = 'n')
        undo_select.grid(row = 0, column =0, sticky = 'n')
        self.mid_frame.columnconfigure([0,1,2],minsize = self.config_data['width']/3 )

    
    
    def draw_outline(self, i, color = 'red'):
        '''
            Draw colored frame (default =red), for selected photos , in search mode
        '''
        if i < len(self.img_list) and (self.img_list[i] in self.chosen_pathes):
            x1, y1 =  (250-self.im_size[0]/2), (150-self.im_size[1]/2)
            x2, y2 = (x1+self.im_size[0]), (y1+self.im_size[1])
            self.canvas1.create_rectangle(x1,y1,x2,y2, fill='', outline=color, width =3, tag='outline')
    
    
    def destroy_children(self, wgt, *args):
        '''
            Clear farme form any widget. optonaly can clear widget list (enteries, lables)
        '''
        children = wgt.winfo_children()
        for c in children:
            c.destroy()
        for arg in args:
            arg.clear()


    def create_collage(self, folder):
        '''
            Create the collage from selected photos. 
        '''
        self.bar['value'] = 15
        self.up_frame.update_idletasks()
        try:
            maker.main(folder, 'collage.jpg', 1080, 800, False)
            self.bar['value'] = 100
            self.msg['text'] = f'The collage is ready! collage name: collage.jpg'
        except:
            self.msg['text'] = 'Sorry. Something went wrong, coud not make collage :('
        finally:
            shutil.rmtree(folder)

    


if __name__ == "__main__":
    b = Browser()
    b.run_window('run', testing=False)



# cahnge chosen path to set