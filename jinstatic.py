import os
import sys
import shutil
import pyinotify
import ConfigParser

##############################################################################

##define basic paths
base_input_folder 	= os.getcwd() + "/input"
base_output_folder 	= os.getcwd() + "/output"
descend_recursive	= True

if len(sys.argv) > 1:
	config 				= ConfigParser.RawConfigParser()
	config.read(sys.argv[1])
	

##overload the settings from the provided config file
if config.has_option("Paths","base_input_folder"):
	base_input_folder = config.get('Paths', 'base_input_folder')
	
if config.has_option("Paths","base_output_folder"):
	base_output_folder = config.get('Paths', 'base_output_folder')	
	
if not base_input_folder or not base_output_folder:
	print "paths are empty"
	exit()


##if the input does not exist, we are done :/
if not os.path.exists(base_input_folder):
	print "input folder does not exist"
	exit();

##delete the output folder and recreate it
if os.path.exists(base_output_folder): 
	shutil.rmtree(base_output_folder)

os.makedirs(base_output_folder)

##load up the jinja loader
from jinja2 import Environment, FileSystemLoader
jinja2_loader = Environment(loader=FileSystemLoader(base_input_folder) )

###########################################################################

def render_template(template_path,template_dict):

	print template_dict

	try:
		template_obj 		= 	jinja2_loader.get_template(template_path)
		render_result		= 	template_obj.render(template_dict)
	except Exception,expeti:
		print "[Compile Failed] error on --> " + template_path
		print expeti
		render_result		= str(expeti)

	return render_result


def recompile(input_dir,output_dir,relative=""):
	
	folder_contents = os.listdir(input_dir)
	context_dict 	= {"yuno_jerry":"jerry is awesome!"}
	
	for content_item in folder_contents:
	
		##if it's a folder.. lets go recursive on the next folder
		if os.path.isdir(input_dir + "/" + content_item):
			new_input 		= input_dir + "/" + content_item
			new_output 		= output_dir + "/" + content_item
			new_relative 	= relative + content_item + "/" 
			
			##make the folder if it does not exist
			if not os.path.exists(new_output): 
				os.mkdir(new_output)
			
			recompile(new_input,new_output,new_relative)
			continue;
		##
		render_result = render_template(relative + content_item,context_dict)
		
		file_opened	= open(output_dir + "/" + content_item ,"w+")
		file_opened.write(render_result)
		file_opened.close()
		
	



###########################################################################

class OnWriteHandler(pyinotify.ProcessEvent):
    def my_init(self):	pass

    def _run_cmd(self):
		print '==> Modification detected'
		recompile(base_input_folder,base_output_folder)

    def process_IN_MODIFY(self, event):
    	file_ext = event.pathname.split(".")[-1]
    	print file_ext
    	
    	if file_ext not in ["htm","html"]:
    		print event.pathname
    		return 0 
    				
        self._run_cmd()

##bind the watcher
wm 			= pyinotify.WatchManager()
handler 	= OnWriteHandler()
notifier 	= pyinotify.Notifier(wm, default_proc_fun=handler)

wm.add_watch(base_input_folder,pyinotify.IN_MODIFY, rec=True, auto_add=True)
notifier.loop()
