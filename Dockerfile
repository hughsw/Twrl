FROM python:3-jessie

RUN pip install python-binance

CMD ["/boot.py"]

ENV BINANCE_API_KEY=DUMMY-KEY  BINANCE_API_SECRET=DUMMY-SECRET

COPY boot.py /
