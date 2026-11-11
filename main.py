import socket
from dataclasses import dataclass
import datetime
from email.utils import parsedate_to_datetime
import mimetypes
from typing import Optional
import ssl

@dataclass
class HttpResponse:
    version: str
    code: int
    status: str
    date: Optional[datetime.datetime]
    server: Optional[str]
    last_modified: Optional[datetime.datetime]
    etag: Optional[str]
    accept_ranges: Optional[str]
    content_length: Optional[int]
    content_type: Optional[str] # 나중에 enum으로 바꾸기
    redirect_location: Optional[str]
    content: str
    original: bytes
    parsed_headers: dict

def parse_http_date(date_str: Optional[str]) -> Optional[datetime.datetime]:
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None

def http_get(url: str, is_ssl: bool = False, port = None, user_agent = "SinokaHTTPLeran/1.0 (Linux; x86_64)") -> HttpResponse:
    _port = 0
    
    _port = port if port else (443 if is_ssl else 80)

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if is_ssl:
        context = ssl.create_default_context()

        client_socket = context.wrap_socket(raw_socket, server_hostname=url)
    else:
        client_socket = raw_socket

    client_socket.connect((url, _port))

    client_socket.sendall(
    bytes(
        f"GET / HTTP/1.1\r\n"
        f"Host: {url}\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Accept-Language: fr\r\n"
        f"Connection: close\r\n\r\n",
        "UTF-8"
    )
)

    raw_response = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        raw_response += chunk

    client_socket.close()

    headers_part, _, body_part = raw_response.partition(b"\r\n\r\n")
    
    headers_text = headers_part.decode("utf-8", errors="ignore")
    body_text = body_part.decode("utf-8", errors="ignore")

    data_by_line = headers_text.split("\r\n")

    status_line = data_by_line[0].split(" ", 2)
    protocol_version = status_line[0]
    code = int(status_line[1])
    status = status_line[2] if len(status_line) > 2 else ""

    protocol, version = protocol_version.split("/")

    if protocol != "HTTP":
        raise ValueError("Invalid protocol: Expected HTTP.")
    if version != "1.1":
        raise ValueError("Unsupported HTTP version: Only HTTP/1.1 is supported.")

    headers = {}

    for line in data_by_line[1:]:
        if line == "":
            break

        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    if headers.get("transfer-encoding") == "chunked":
        merged_body = b""
        pos = 0

        while True:
            crlf_index = body_part.find(b"\r\n", pos)
            if crlf_index == -1: break

            hex_bytes = body_part[pos:crlf_index].split(b";")[0].strip()
            if not hex_bytes:
                break
            body_size = int(hex_bytes, 16)

            if body_size == 0: break

            pos = crlf_index+2

            merged_body += body_part[pos:pos+body_size]

            pos += body_size+2

        body_text = merged_body.decode("utf-8", errors="ignore")

    return HttpResponse(
        version=version,
        code=code,
        status=status,
        date=parse_http_date(headers.get("date")),
        server=headers.get("server"),
        last_modified=parse_http_date(headers.get("last-modified")),
        etag=headers.get("etag"),
        accept_ranges=headers.get("accept-ranges"),
        content_length=int(headers["content-length"]) if "content-length" in headers else None,
        content_type=headers.get("content-type"),
        redirect_location=headers.get("location"),
        content=body_text,
        original=raw_response,
        parsed_headers=headers
    )

print(http_get("www.youtube.com", is_ssl=True).content)