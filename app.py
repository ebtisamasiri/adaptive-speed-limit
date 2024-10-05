# # # from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# # # import os
# # # from main import process_video  # Import the function from main.py

# # # app = Flask(__name__)

# # # # Configure upload and processed video folders
# # # UPLOAD_FOLDER = 'uploads'
# # # PROCESSED_FOLDER = 'static/processed_videos'

# # # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # # app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# # # # Ensure the directories exist
# # # if not os.path.exists(UPLOAD_FOLDER):
# # #     os.makedirs(UPLOAD_FOLDER)
# # # if not os.path.exists(PROCESSED_FOLDER):
# # #     os.makedirs(PROCESSED_FOLDER)

# # # # Route for the main page
# # # @app.route('/')
# # # def index():
# # #     return render_template('index.html')


# # # # Handle video upload and processing
# # # @app.route('/upload', methods=['POST'])
# # # def upload_file():
# # #     if 'file' not in request.files:
# # #         return redirect(request.url)
    
# # #     file = request.files['file']
    
# # #     if file.filename == '':
# # #         return redirect(request.url)
    
# # #     if file:
# # #         # Save the uploaded file
# # #         video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
# # #         file.save(video_path)
        
# # #         # Process the video using the function in main.py
# # #         processed_video_path = process_video(video_path, app.config['PROCESSED_FOLDER'])
        
# # #         # Redirect to the processed video for download
# # #         return redirect(url_for('processed_video', filename=os.path.basename(processed_video_path)))


# # # # Route to serve processed videos
# # # @app.route('/processed/<filename>')
# # # def processed_video(filename):
# # #     return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


# # # if __name__ == '__main__':
# # #     app.run(debug=True)
# # from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# # import os
# # from main import process_video  # Import the video processing function

# # app = Flask(__name__)

# # # Configure upload and processed video folders
# # UPLOAD_FOLDER = 'uploads'
# # PROCESSED_FOLDER = 'static/processed_videos'

# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# # # Ensure the directories exist
# # if not os.path.exists(UPLOAD_FOLDER):
# #     os.makedirs(UPLOAD_FOLDER)
# # if not os.path.exists(PROCESSED_FOLDER):
# #     os.makedirs(PROCESSED_FOLDER)

# # # Route for the main page
# # @app.route('/')
# # def index():
# #     return render_template('index.html', processed_video=None)


# # # Handle video upload and processing
# # @app.route('/upload', methods=['POST'])
# # def upload_file():
# #     if 'file' not in request.files:
# #         return redirect(request.url)

# #     file = request.files['file']

# #     if file.filename == '':
# #         return redirect(request.url)

# #     if file:
# #         # Save the uploaded file
# #         video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
# #         file.save(video_path)

# #         # Process the video using the function in main.py
# #         processed_video_path = process_video(video_path, app.config['PROCESSED_FOLDER'])
        

# #         # Render the page with the processed video for playback
# #         return render_template('index.html', processed_video=os.path.basename(processed_video_path))


# # # Route to serve processed videos
# # @app.route('/processed/<filename>')
# # def processed_video(filename):
# #     return send_from_directory(app.config['PROCESSED_FOLDER'], filename, mimetype='video/mp4')



# # if __name__ == '__main__':
# #     app.run(debug=True)
# from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# import os
# from main import process_video

# app = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# PROCESSED_FOLDER = 'static/processed_videos'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
# if not os.path.exists(PROCESSED_FOLDER):
#     os.makedirs(PROCESSED_FOLDER)

# @app.route('/')
# def index():
#     return render_template('index.html', processed_video=None)

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return redirect(request.url)
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return redirect(request.url)

#     if file:
#         video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(video_path)
        
#         processed_video_path = process_video(video_path, app.config['PROCESSED_FOLDER'])
        
#         return render_template('index.html', processed_video=os.path.basename(processed_video_path))

# @app.route('/processed/<filename>')
# def processed_video(filename):
#     return send_from_directory(app.config['PROCESSED_FOLDER'], filename, mimetype='video/mp4')

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from main import process_video

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/processed_videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    
    if file.filename == '':
        return 'No file selected', 400

    if file:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)
        
        processed_video_path = process_video(video_path, app.config['PROCESSED_FOLDER'])

        # Return the processed video HTML tag directly for insertion via JavaScript
        return f'''
            <h2>Processed Video:</h2>
            <video width="720" height="480" controls>
                <source src="{url_for('processed_video', filename=os.path.basename(processed_video_path))}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        '''

@app.route('/processed/<filename>')
def processed_video(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
