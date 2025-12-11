# 1. Image cơ sở có Python
FROM python:3.10-slim

# 2. Cài đặt các thư viện hệ thống cần thiết cho Chrome/Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 3. Thêm repository của Google Chrome/Chromium
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# 4. Cài đặt Google Chrome (Đã tối ưu cho Headless)
RUN apt-get update && apt-get install -y google-chrome-stable

# 5. Cấu hình môi trường Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Sao chép code
COPY . .

# 7. Đặt lệnh chạy mặc định
CMD ["python", "stv.py"]
