import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk,Image
from pathlib import Path 




# Costumized exception part

class NotValidNumberError (Exception):
    pass

class NotValidPath(Exception):
    pass

# raise err if num is not digit  and 0<num <8
def is_valid_num(num):
    try:
        if num =='':            # accept empty input to default number of directories (1)
            return 
        i = int(num) 
        if (i < 1) or (i >7 ):
            raise NotValidNumberError
    except:
        raise NotValidNumberError()

# raise err if path is not exist dir
def is_valid_path(path):
    if not Path(path).exists():
        raise NotValidPath()



class Browser ():
    '''
        Class for create the GUI for photos organization.The user enter the number and names of
        sub directories to copy photos into, and while browsing the directory, photo will be
        displayed as thumbnails, by clicking on the desired button the photowill be copied to the fit directory
    '''

    def __init__(self):

        self.root = tk.Tk() 
        self.root.title('Photo Browser')
        self.config_data = {'bg':'#B8E0FE', 'width':500, 'height':450, 'font': ('Arial 12')}         # default configuration for widgets
        self.root.geometry('500x450+100+100')
        # the screen is composed from 3 parts, rule diffrent part of the widgets
        self.up_frame =tk.Frame(master =self.root,width=self.config_data['width'], height = 300, bg = '#B8E0FE')
        self.mid_frame =tk.Frame(master =self.root,width=self.config_data['width'], height = 100, bg = '#B8E0DE')
        self.bottom_frame =tk.Frame(master =self.root,width=self.config_data['width'], height = 50, bg = '#A1E0DE')
        # temp dir for thumbnails
        self.thumbnail_dir = Path((Path().cwd() / 'Thumbnails'))
        # table to track number of copied photos every new dir
        self.TOTAL = {}
        # variablle to track the widgets in  the future
        self.msg = ''
        self.entries = []
        self.labels = []
        self.btn_names = []
        self.names=['Trash']
        self.next_bt =[]
        self.img_list=[]
        self.ROOT_DIR = ''
        self.num_of_dir = 1
        self.i = 0
        # for testing mode
        self.prod = True

    def opening_screen(self):
        '''getting and checking user input'''
        try:
            self.ROOT_DIR = (self.entries[0].get())
            is_valid_path(self.ROOT_DIR)
            is_valid_num(self.entries[1].get())
            self.num_of_dir = int(self.entries[1].get())
            ### debug
            if self.num_of_dir == '':
                self.test_data()
            ### end debug
            self.img_list = [f for f in Path(self.ROOT_DIR).iterdir() if (not f.is_dir())]
            # clear previous screen
            self.destroy_children(self.up_frame)
            self.destroy_children(self.mid_frame, self.entries, self.labels)
            #  create enteries to colllect directories names
            for j in range(self.num_of_dir):
                entry = tk.Entry(master = self.up_frame)
                self.entries.append(entry)
                entry.grid(row = j, column=1,padx = 30, pady = 5)              
                label = tk.Label(master = self.up_frame, text = 'Enter dir name:' , bg= '#B8E0FE', font='Ariel 12')
                self.labels.append(label)
                label.grid(row = j, column= 0, padx = 30, pady = 5)
            # set the next button to new command
            self.next_bt[0]['command'] = self.insert_name
        
        except NotValidPath:
            
            self.msg['text'] = 'Ilegal input for path'
            # replace by self.errmsg(msg)
        except NotValidNumberError:
            
            self.msg['text'] ='Ilegal input for number'
            
    def insert_name(self):
        ''' collect the names of directories'''
        
        # collect the names of dirs
        if self.prod:
            for e in self.entries:
                self.names.append(e.get())
        # clear the screen display
        self.destroy_children(self.up_frame, self.entries, self.labels)
        all_names = '\n  - '.join(self.names)
        # reset the msg widet 
        self.msg = tk.Label(master = self.up_frame, text ='You chose the next directories:\n  - '+all_names, font = ('Ariel 12'),
                bg = self.config_data['bg'], justify = tk.LEFT)
        self.msg.grid(row = 0, column = 0,padx = 20, pady =40, sticky = 'nsew')
        # create the directories
        for name in self.names:
            self.create_dir(self.ROOT_DIR, name)
            self.TOTAL[name] = 0
        self.next_bt[0]['command']= self.show_photo
        
            
    def show_photo(self):
        i = self.i
        # create canvas to display thumbails
        if i == 0:
            self.canvas1 = tk.Canvas(master = self.up_frame,width=self.config_data['width'], height = 300, bg='#B8E0FE',highlightthickness=0)
        # set next btn to be used as finish btn
        self.next_bt[0]['command'] = self.finish_screen
        self.next_bt[0]['text'] = 'Finish'
        # iterate over the files and try to treat them as photos
        if i < len(self.img_list):
            try:
                out = self.create_thumbnail(self.img_list[i])
            
                # display thumbnail
                image1 = ImageTk.PhotoImage(Image.open(str(out)))
                # clear up_frame
                self.msg.destroy()
                # display photo
                self.canvas1.grid(row = 0, column = 0)
                self.canvas1.create_image(self.config_data['width']/2, 150, image=image1)
                self.canvas1.image = image1    
                #select directory
                btns_max_len = len(max(self.names, key=len))
                l = tk.Label(master= self.mid_frame,text = 'click to\ncopy photo', justify = tk.LEFT,
                    bg = self.config_data['bg'],font = self.config_data['font'])
                l.grid(row = 0, column=0, rowspan = 2, padx = (10,0))
                for j, n in enumerate(self.names):
                    dest = Path(self.ROOT_DIR) / n
                    btn = tk.Button(master= self.mid_frame, width = btns_max_len, text = n, command = lambda x=dest:self.send(Path(self.img_list[i]), Path(x)))
                    self.btn_names.append(btn)
                    btn.grid(row = j//4, column= (j%4)+1,padx = (3, 0), pady  = 10)
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
            The last screen of the app, show the number of photos in evry new directory
        '''
        # clear the up_frame
        self.destroy_children(self.canvas1)
        self.destroy_children(self.up_frame)
        self.destroy_children(self.mid_frame)
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
        self.draw_table(int(self.num_of_dir)+1,2,c3)
        # set the finish button to be used as exit
        self.next_bt[0]['command'] = self.exit_screen
        self.next_bt[0]['text'] = 'Exit'
        
    def exit_screen(self):
        '''terminate the app'''
        shutil.rmtree(self.thumbnail_dir)
        self.root.destroy()
        

    def initiate_screen(self):
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

        # add the next button
        self.next_bt.append(tk.Button(master = self.bottom_frame,text='Next', command=self.opening_screen))
        self.next_bt[0].grid(row = 0, column=0,pady = 10,padx = 20, sticky = 'e')
    
    def run(self):
        '''
            method to initialize the app andconfig the initial display
        '''
        #self.initiate_screen()
        # add the openning message for the user
        self.msg = tk.Label(master = self.up_frame,bg = '#B8E0FE', font="Times 16 bold", 
        text = 'Welcome to the image browser.\nInsert the nuber of the directory\nto sort the images',
            justify=tk.LEFT)
        self.msg.grid(row =0 , column = 0, padx  = 20, pady = 30, sticky = 'w')
        # add entries and label to inser user input
        self.entries.append(tk.Entry(master = self.mid_frame, bg= 'white'))
        self.entries.append(tk.Entry(master = self.mid_frame, bg = 'white'))
        self.labels.append(tk.Label(self.mid_frame, text = 'Enter images directory path:',
             bg= '#B8E0FE', font='Ariel 12'))
        self.labels.append(tk.Label(self.mid_frame, text = 'Enter number of sub-directories:',
             bg= '#B8E0FE', font='Ariel 12'))
        
        for i in range(len(self.entries)):
            self.labels[i].grid(row = i, column = 0,padx = 0, sticky = 'w')
            self.entries[i].grid(row = i, column = 1, padx = 0,sticky = 'w')
        
        # add temp directory for thumbnails
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        # run the app
        #self.root.mainloop()
    
    def run_window(self, name, prod=True):
        '''for testing propose, allow to run specific window directly'''
        self.prod = prod
        if not self.prod:
            self.test_data()
        self.initiate_screen()
        
        getattr(Browser, name)(self)
        self.root.mainloop()
        
        
    def destroy_children(self, wgt, *args):
        children = wgt.winfo_children()
        for c in children:
            c.destroy()
        for arg in args:
            arg.clear()

    def send(self, src, dest):
        '''send photo from root dir to the target dir chose by user'''
        shutil.copy(Path(src),Path(dest))    
        # update total
        self.TOTAL[dest.name] += 1
        # return to next image
        self.show_photo()
    
    def create_dir(self, parent_dir, name):
        new_dir = Path(parent_dir) / name
        Path(new_dir).mkdir(parents=True, exist_ok=True)

    def create_thumbnail(self, img_path):
        img_name = str(img_path.stem)
        thumbnail_name = img_name+'_thumbnail.jpg'
        path_to_save = Path(self.thumbnail_dir)/ thumbnail_name
        im = Image.open(img_path)
        im = im.convert('RGB')
        im.thumbnail((200,300), Image.ANTIALIAS)
        im.save(str(path_to_save), "JPEG")
        return path_to_save
    
    def draw_table(self, r, c, master):
        ''' create the tabel to summerize the app data'''
        self.entries.clear()     
        print(r,c)
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
        for i in range(2):
            self.entries[i].config(fg='blue', font =('Arial',12, 'bold'))            

    def test_data(self):
        self.ROOT_DIR = r'C:\Users\elkana\Pictures\lego'
        self.names += ['airplanes', 'cars', 'robots', 'other','a', 'dk']
        self.num_of_dir = len(self.names)
        self.img_list = [f for f in Path(self.ROOT_DIR).iterdir() if (not f.is_dir())]


if __name__ == "__main__":
    b = Browser()
    b.run_window('run', prod=False)