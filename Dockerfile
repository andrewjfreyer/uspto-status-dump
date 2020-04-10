FROM python:3

MAINTAINER Andrew J Freyer "andrew.freyer@gmail.com"

#INSTALL EXCEL STUFFS
RUN pip3 install pyexcel
RUN pip3 install python-dateutil --upgrade

#EXECUTE SCRIPT
CMD [ "python3", "/src/uspto-status-dump.py" ]

