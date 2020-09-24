FROM python
# COPY requReturn_2.py /code/
ADD ./ /Main
WORKDIR /Main
RUN pip3 install requests
CMD ["python3","Main.py"]
