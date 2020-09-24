FROM aarch64/python:3.6-alpine
# COPY requReturn_2.py /code/
ADD ./ /
WORKDIR /
RUN mkdir /config
RUN pip3 install requests
CMD ["python3","/Main.py"]
