docker run --rm --entrypoint "" -v "%cd%\python:/opt/python" public.ecr.aws/lambda/python:3.11 pip install --no-cache-dir gspread pyathena -t /opt/python

tar -a -c -f gspread-layer.zip python
