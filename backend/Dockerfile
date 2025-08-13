#base
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-devel

#working dir
WORKDIR /backend/

#copy
COPY requirements.txt .
COPY . .

#run
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#port
EXPOSE 8000

#command
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]