from flask import Flask, request, send_file, jsonify, render_template
import rawpy
from PIL import Image
import io
import zipfile
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Configuration       

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_multiple_raws():
    if 'files' not in request.files:
        return jsonify({"error": "No se encontraron archivos"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "Lista de archivos vacía"}), 400

    zip_io = io.BytesIO()

    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for raw_file in files:
            try:
                with rawpy.imread(raw_file) as raw:
                    rgb = raw.postprocess()
                img = Image.fromarray(rgb)

                img_bytes = io.BytesIO()
                img.save(img_bytes, 'JPEG', quality=95)
                img_bytes.seek(0)

                filename = os.path.splitext(raw_file.filename)[0] + '.jpg'
                zip_file.writestr(filename, img_bytes.read())
            except Exception as e:
                return jsonify({"error": f"Error con {raw_file.filename}: {str(e)}"}), 500

    zip_io.seek(0)
    return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='converted_images.zip')

if __name__ == '__main__':
    app.run(debug=True)
