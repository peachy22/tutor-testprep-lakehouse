docker run --rm --entrypoint "" -v "%cd%\python:/opt/python" public.ecr.aws/lambda/python:3.11 pip install --no-cache-dir fsspec s3fs -t /opt/python

tar -a -c -f fsspec-layer.zip python
