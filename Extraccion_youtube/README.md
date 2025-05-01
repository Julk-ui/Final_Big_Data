To run **etl**, you need to run the following steps:

1. Install the dependencies

python -m pip install -r requirements.txt

pip install typer

typer==0.3.2
colorama==0.4.4
shellingham==1.4.0
pytest==6.2.4
SpeechRecognition==3.14.2
pyttsx3==2.90
pymongo==4.6.1
youtube-transcript-api==1.0.3


2. Initialize the application

python -m etl init

3. options :

add text
python -m etl add c:\images\prueba.png

list text
python -m etl list

clear text
python -m etl clear

typer==0.3.2
colorama==0.4.4
shellingham==1.4.0
pytest==6.2.4
SpeechRecognition==3.14.2
pyttsx3==2.90
pymongo==4.6.1
youtube-transcript-api==1.0.3
