FROM python:3.11.14-trixie

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# following two lines are for a script file.
# they replaced the uvicorn line and will be the 
# entry point to uvicorn
# COPY ./start.sh /start.sh
# RUN chmod +x /start.sh

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]

