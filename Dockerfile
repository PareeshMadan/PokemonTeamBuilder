from python:3.9.1
ADD . /python-flask
WORKDIR /python-flask
RUN pip install -r requirements.txt

#Expose the required port
EXPOSE 8080

#Run the command
CMD gunicorn app:app -b 0.0.0.0:8080
