from flask import Flask , render_template, request , redirect, url_for
import os , base64 , time, sys
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import shutil
import subprocess
import shlex


app = Flask(__name__)

UPLOAD_FOLDER = "./static/pdfs/"
ALLOWED_EXTENSIONS = set(['pdf' , 'txt'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


SOURCE_PATH = "./static/output/output.txt"
DEST_PATH = "./PreSumm/raw_data/1.txt"
OUTPUT_PATH = "./PreSumm/results/cnndm.-1.candidate"

def summarize():

    cmd = "python train.py -task abs -mode test_text -test_from ../models/model_step_148200.pt -log_file ../logs/val_abs_bert_medrec -text_src ../raw_data/1.txt -visible_gpus -1"

    shutil.copy(SOURCE_PATH, DEST_PATH)
    cmd = shlex.split(cmd)

    os.chdir("./Presumm/src/")
    
    process = subprocess.run(cmd , stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.STDOUT)

    if process.returncode == 0:
        os.chdir("../../")
        shutil.copy(OUTPUT_PATH , SOURCE_PATH)
        return 1
    else:
        return process.stdout


def convert_ocr(path , dpi):

    pages = convert_from_path(path , dpi , poppler_path="C:/Python37/Lib/site-packages/poppler-0.68.0/bin" )

    pg_count = 1

    try:
        shutil.rmtree("./static/output")
        shutil.rmtree("./static/pages")
    except:
        pass

    os.makedirs("./static/output")
    os.makedirs("./static/pages")


    for page in pages:
        
        page.save('./static/pages/{}.jpg'.format(pg_count) , 'JPEG') #Saves image in ./output/ folder with curent directory
        pg_count += 1

    out = open('./static/output/output.txt' , "wb") # For final converted text

    for page in range(1 , pg_count):

        # Recognize the text as string in image using pytesseract
        text = str(pytesseract.image_to_string(Image.open("./static/pages/{}.jpg".format(page))))

        # In many PDFs at line ending a 'hyphen' is added to remove this:
        text = text.replace('-\n', '')

        # Finally write the processed text to file
        out.write(text.encode("utf-8"))

        out.close()

@app.route("/")
def index():
    #return render_template("index.html")
    return render_template('index.html')

@app.route("/" , methods=["GET" , "POST"])
def scan():
    if request.method == "POST":

        f = request.files["file"]
        ext = f.filename.rsplit('.', 1)[1].lower()
        
        if ext == 'pdf':

            # id =  base64.b64encode("%s %s" %(time.time(), f.filename)).replace('=', '')
            # filename = id + ".pdf"
            #path = os.path.dirname(os.path.abspath(__file__))
            f.save(UPLOAD_FOLDER + f.filename)
            path = UPLOAD_FOLDER + f.filename

            convert_ocr(path , 500)

            return redirect(url_for("out"))

        elif ext == 'txt':
            f.filename='output.txt'
            f.save('./static/output/' + f.filename)

            return redirect(url_for("out"))
        #out = open('./app/static/output/output.txt' , "wb")            
        else:
            return "invalid Extension"
        #return render_template("scanned_output.html" , scanned = out.read() + highlights)
    return "None"
        #return out.read() if out.read() else "None"

@app.route("/scan")
def out():
    with open('./static/output/output.txt', "rb") as f:
        data = f.read().decode("utf-8")
        return render_template('scanned_output.html', scanned=data)

@app.route("/output" , methods=["GET" , "POST"])
def final():
    if request.method == "POST":
        r = summarize()
        if r == 1:
            with open('../app/static/output/output.txt', "rb") as f:
                data = f.read().decode("utf-8")
                return render_template('summary.html', summary=data)
        else:
            return r

if __name__ == "__main__":
    app.run(debug=True)