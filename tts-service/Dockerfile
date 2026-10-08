FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
    piper-tts \
    flask \
    onnxruntime \
    onnx

RUN mkdir -p /app/voices

RUN python -m piper.download_voices \
    --data-dir /app/voices \
    en_US-lessac-medium
	

RUN python -m piper.download_voices \
    --data-dir /app/voices \
    ar_JO-kareem-medium
	
RUN python -c "import json; \
p='/app/voices/ar_JO-kareem-medium.onnx.json'; \
d=json.load(open(p, encoding='utf-8')); \
d['inference']['length_scale']=0.88; \
json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)"

EXPOSE 9026

CMD ["python", "-m", "piper.http_server", "--host", "0.0.0.0", "--port", "9026", "--data-dir", "/app/voices", "-m", "en_US-lessac-medium"]