FROM python:3

MAINTAINER Andrew J Freyer "andrew.freyer@gmail.com"

#INSTALL
RUN pip3 install python-dateutil --upgrade

#EXECUTE SCRIPT
CMD [ "python3", "/src/uspto-status-dump.py" ]

