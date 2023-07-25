import os
from flask import Flask, request
import ffmpeg
import webbrowser

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    video_file = request.files.get('video')
    filename = request.form.get('filename')
    save_path = os.path.join(os.getcwd(), 'Video', filename)
    video_file.save(save_path)
    convert_to_mp4(save_path)
    return 'File uploaded successfully'

def convert_to_mp4(file_path):
    # Determine the output file path
    output_path = os.path.splitext(file_path)[0] + '.mp4'

    # Use ffmpeg-python to convert WebM to MP4
    ffmpeg.input(file_path).output(output_path).run()

    # Remove the original file
    os.remove(file_path)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KYC Solution</title>
        <style>
            video {
                width: 400px;
                height: 300px;
            }
        </style>
    </head>
    <body>
        <h1>KYC Solution</h1>
        <button id="startButton">Start Recording</button>
        <button id="stopButton" disabled>Stop Recording</button>
        <br>
        <video id="videoElement" controls autoplay></video>
        <br>
        <script>
            var startButton = document.getElementById('startButton');
            var stopButton = document.getElementById('stopButton');
            var videoElement = document.getElementById('videoElement');
            var mediaRecorder;
            var recordedBlobs = [];

            function startRecording() {
                navigator.mediaDevices.getUserMedia({ audio: true, video: true })
                    .then(function(stream) {
                        videoElement.srcObject = stream;
                        mediaRecorder = new MediaRecorder(stream);

                        mediaRecorder.ondataavailable = function(event) {
                            if (event.data && event.data.size > 0) {
                                recordedBlobs.push(event.data);
                            }
                        };

                        mediaRecorder.start();
                        startButton.disabled = true;
                        stopButton.disabled = false;
                    })
                    .catch(function(error) {
                        console.log('Error accessing media devices: ', error);
                    });
            }

            function stopRecording() {
                mediaRecorder.stop();
                startButton.disabled = false;
                stopButton.disabled = true;

                var blob = new Blob(recordedBlobs, { type: 'video/webm' });
                var videoUrl = URL.createObjectURL(blob);

                videoElement.src = videoUrl;

                var formData = new FormData();
                formData.append('video', blob, getUniqueFilename());
                formData.append('filename', getUniqueFilename());

                fetch('/upload', { method: 'POST', body: formData })
                    .then(function(response) {
                        console.log('File uploaded successfully');
                        window.close();
                    })
                    .catch(function(error) {
                        console.log('Error uploading file: ', error);
                    });

                recordedBlobs = [];
            }

            function getUniqueFilename() {
                var currentDate = new Date();
                var timestamp = currentDate.getTime();
                return 'recorded_cam_' + timestamp + '.webm';
            }

            startButton.addEventListener('click', startRecording);
            stopButton.addEventListener('click', stopRecording);
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    video_folder = os.path.join(os.getcwd(), 'Video')
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)

    # Open the browser window automatically
    webbrowser.open('http://localhost:5000')

    # Run the Flask app
    app.run(debug=True)
