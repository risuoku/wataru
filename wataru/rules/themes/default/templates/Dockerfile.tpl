FROM playground1

ENV JUPYTER_PATH /dockerwork/.jupyter
ENV IPYTHONDIR /dockerwork/.ipython

COPY . .

RUN pip3 install -r requirements.txt
