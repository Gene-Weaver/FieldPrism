FROM python:3.10.4

ADD FieldPrism.py .
ADD FieldSheetBuilder.py .

# RUN pip install cython depthai fpdf \
#     fonttools gps3 imageio ipython keyboard \
#     matplotlib numpy opencv-python pandas Pillow \
#     pybboxes pygame pypng PyQt5 PyQt5-Qt5 PyQt5-sip \
#     pyyaml qrcode qrtools requests \
#     scikit-image scipy seaborn tqdm urllib3
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
RUN pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113

CMD ["python", "./FieldPrism.py"]