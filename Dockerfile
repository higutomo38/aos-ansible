FROM python:3.6.12-slim-buster
RUN pip install --upgrade pip
RUN pip install nano
RUN pip install jmespath
RUN pip install requests
RUN pip install ansible==2.6.1
RUN mkdir /tmp/aos-ansible/
COPY . /tmp/aos-ansible/
RUN apt-get update && apt-get install -y python
RUN sed -i '1i import sys' /tmp/aos-ansible/module_utils/shared.py
RUN sed -i '2i sys.path.append(\"/usr/local/lib/python3.6/site-packages\")' /tmp/aos-ansible/module_utils/shared.py





