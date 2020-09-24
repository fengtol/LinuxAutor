
FROM python:3.7.4-alpine
# COPY requReturn_2.py /code/
WORKDIR /Main
RUN pip3 install requests
CMD ["python3","Main.py"]
