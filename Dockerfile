FROM aarch64/python:3.6-alpine
# COPY requReturn_2.py /code/
ADD ./ /Main
WORKDIR /Main
RUN pip3 install requests
CMD ["python3","Main.py"]
