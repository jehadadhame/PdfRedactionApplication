to run this first you have to build it

``docker build -t pdfredaction-fastapi:latest .``         

then you can run it 

``docker run --rm -p 9999:9999 --name pdfredaction pdfredaction-fastapi:latest``
