FROM python:3.10

WORKDIR /fantasyNBA

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8501

COPY . .

CMD ["streamlit", "run", "main.py"]
