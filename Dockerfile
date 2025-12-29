# Sử dụng Python 3.10 nhẹ nhất
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết (để build numpy/chromadb)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào
COPY . .

# Mở cổng 8501 (Cổng mặc định của Streamlit)
EXPOSE 8501

# Lệnh kiểm tra sức khỏe (Healthcheck)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Lệnh chạy ứng dụng
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]