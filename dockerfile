
FROM python
# COPY requReturn_2.py /code/
WORKDIR /Main
RUN pip3 install requests
CMD ['python3','Main.py']