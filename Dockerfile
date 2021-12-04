FROM python:3.9

WORKDIR /fantasyNBA

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8501

COPY . .

CMD ["streamlit", "run", "main.py"]
