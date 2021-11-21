FROM python:3.9

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8501

# VOLUME C:\\Users\\vegterj\\Documents\\Git\\streamlit-nba-fantasy

# COPY . .

CMD ["streamlit", "run", "src/main.py"]

# docker run -it -d -v "${pwd}":/app .