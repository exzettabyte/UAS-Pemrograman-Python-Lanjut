from flask import render_template, url_for
import os
from os.path import isfile,join
from PIL import Image
from zipfile import ZipFile
import pathlib


class WatermarK:
    def __init__(self):
        self.whitelist = ('.jpg','.jpeg','.png','zip')
        self.tmp_directory = f"{os.getcwd()}/tmp/uploads"
        self.single_directory = f"{os.getcwd()}/static/uploads/single"
        self.multiple_directory = f"{os.getcwd()}/static/uploads/multiple"

    def delete(self):
        for f in os.listdir(self.tmp_directory):
            os.remove(f'{self.tmp_directory}/{f}')

    def get_images(self):
        onlyimages = [f for f in os.listdir(self.tmp_directory) if isfile(join(self.tmp_directory,f))]
        return [f for f in onlyimages if f.endswith(self.whitelist[0:3])]

    def makezip(self,zipname):
        path = pathlib.Path(self.multiple_directory)
        with ZipFile(f"{self.multiple_directory}/../result_{zipname}",mode="w") as data:
            for f in path.iterdir():
                data.write(f,arcname=f.name)

    def watermark_multiple(self,files,file2):
        with ZipFile(f'{self.tmp_directory}/{files}', 'r') as f:
            f.extractall(f'{self.tmp_directory}')
        listimages = self.get_images()
        for img in listimages:
            if img == file2:
                pass
            else:
                self.watermark_single(img,file2,"multiple")
        self.makezip(files)

    def watermark_single(self,file_name,file_name2,mode):
        image = Image.open(f'{self.tmp_directory}/{file_name}')
        image_width = image.width
        image_height = image.height
        watermark = Image.open(f'{self.tmp_directory}/{file_name2}')
        watermark_width = watermark.width
        watermark_height = watermark.height
        image.paste(watermark,(int((image_width - watermark_width)/2),int((image_height - watermark_height)/2)), watermark)
        if mode == "multiple":
            image.save(f'{self.multiple_directory}/result_{file_name}')
        elif mode == "single":
            image.save(f'{self.single_directory}/result_{file_name}')

    def validate(self,filename,mode):
        extension = os.path.splitext(filename)[1]
        if mode == "single":
            return extension in self.whitelist
        elif mode == "multiple":
            if extension != ".zip":
                notvalid = "2"
                return notvalid

    def run(self,request):
        if request.files['file'] and request.files['file2'] != None:
            getfile = request.files['file']
            getfile2 = request.files['file2']
            file_name = getfile.filename
            file_name2 = getfile2.filename
            tmp_path = join(self.tmp_directory, file_name)        
            tmp_path2 = join(self.tmp_directory, file_name2)
            getfile.save(tmp_path)
            getfile2.save(tmp_path2)
            if request.form['mode'] == "single":
                if not self.validate(file_name,"single"):
                    notvalid = "1"
                    return notvalid
                else:
                    self.watermark_single(file_name,file_name2,"single")
                    return f"uploads/single/result_{file_name}"
            elif request.form['mode'] == "multiple":
                if self.validate(file_name,"multiple") == "2":
                    notvalid = self.validate(file_name,"multiple")
                    return notvalid
                else:    
                    self.watermark_multiple(file_name,file_name2)
                    return f"uploads/result_{file_name}"
        else:
            notvalid = "3"
            return notvalid

def page():
    return render_template('file_upload.html', file_url=None)

def execute(request):
    automation = WatermarK()
    response = automation.run(request)
    automation.delete()
    if response == "1":
        return render_template('file_upload.html',notvalid=f'{response}',file_url=None)
    elif response == "2":
        return render_template('file_upload.html',notvalid=f'{response}',file_url=None)
    elif response == "3":
        return render_template('file_upload.html',notvalid=f'{response}',file_url=None)
    else:
        return render_template('file_upload.html',file_url=url_for('static', filename=f'{response}'))