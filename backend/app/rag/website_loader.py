
import aiohttp
import asyncio
import ipaddress
import socket

from bs4 import BeautifulSoup
from urllib.parse import urlparse


MAX_HTML_BYTES = 2 * 1024 * 1024


class PublicIPResolver(aiohttp.abc.AbstractResolver):

    async def resolve(
        self,
        host,
        port=0,
        family=socket.AF_INET,
    ):

        loop = asyncio.get_running_loop()

        addresses = await loop.getaddrinfo(
            host,
            port,
            family=family,
            type=socket.SOCK_STREAM,
        )

        results = []

        for address in addresses:

            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                raise ValueError(
                    "Private or non-public IP addresses are not allowed."
                )

            results.append({
                "hostname": host,
                "host": str(ip),
                "port": port,
                "family": address[0],
                "proto": address[2],
                "flags": address[3],
            })

        if not results:
            raise ValueError("No public IP addresses found.")

        return results

    async def close(self):
        pass


def load_website(url: str) -> dict:

    async def fetch_website():

        connector = aiohttp.TCPConnector(
            resolver=PublicIPResolver(),
            use_dns_cache=False,
        )

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        ) as session:

            async with session.get(
                url,
                allow_redirects=False,
            ) as response:

                if 300 <= response.status < 400:
                    raise ValueError(
                        "Website redirects are not currently supported."
                    )

                response.raise_for_status()

                # Check the declared response size first.
                content_length = response.headers.get("Content-Length")

                if content_length:
                    try:
                        if int(content_length) > MAX_HTML_BYTES:
                            raise ValueError(
                                "Website content exceeds the maximum allowed size of 2MB."
                            )
                    except ValueError as exc:
                        if "maximum allowed size" in str(exc):
                            raise
                        raise ValueError(
                            "Invalid Content-Length header."
                        ) from exc

                # Only accept HTML webpages.
                content_type = response.headers.get(
                    "Content-Type",
                    "",
                )

                if "text/html" not in content_type.lower():
                    raise ValueError(
                        "The URL must point to an HTML webpage."
                    )

                # Download HTML in chunks and enforce the actual size limit.
                html_content = bytearray()

                async for chunk in response.content.iter_chunked(
                    64 * 1024
                ):

                    html_content.extend(chunk)

                    if len(html_content) > MAX_HTML_BYTES:
                        raise ValueError(
                            "Website content exceeds the maximum allowed size of 2MB."
                        )

                # Decode downloaded HTML.
                try:
                    return html_content.decode(
                        response.charset or "utf-8",
                        errors="replace",
                    )

                except LookupError:
                    return html_content.decode(
                        "utf-8",
                        errors="replace",
                    )

    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    if not parsed_url.hostname:
        raise ValueError("Invalid website URL.")

    if parsed_url.username or parsed_url.password:
        raise ValueError("URLs containing credentials are not allowed.")

    html = asyncio.run(fetch_website())

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    #Extract the webpage title.
    page_title = ""

    if soup.title:
        page_title = soup.title.get_text(
            separator=" ",
            strip=True,
        )

        soup.title.decompose()


    # Remove unnecessary HTML elements.
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
    ]):
        element.decompose()

    # Extract readable webpage text.
    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    if not text:
        raise ValueError("No readable text found on the website.")

    return {
        "text": text,
        "page_title": page_title,
    }