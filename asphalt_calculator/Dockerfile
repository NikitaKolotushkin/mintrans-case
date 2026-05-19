# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends git
RUN rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/

COPY --from=common_src . /app/asphalt_common/

RUN pip install --no-cache-dir --user -r requirements/dev.txt
RUN pip install --no-cache-dir --user /app/asphalt_common/

COPY app/ app/

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY app/ app/
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]