FROM python:3.8-slim-buster

WORKDIR /app

# COPY requirements.txt requirements.txt
RUN pip install streamlit
RUN pip install espn_api
RUN pip install pandas

COPY . .

CMD [ "python3", "-m" , "streamlit", "run", "src/main.py"]