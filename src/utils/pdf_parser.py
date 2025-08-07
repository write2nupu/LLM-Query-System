from __future__ import annotations

import io
from typing import Optional

import aiohttp
from pypdf import PdfReader


class PDFParser:
    def __init__(self, uri: Optional[str] = None) -> None:
        """
        Initialize the PDFParser with an optional URI to a PDF file.

        >>> parser = PDFParser("https://getsamplefiles.com/download/pdf/sample-1.pdf")
        >>> isinstance(parser, PDFParser) == True
        True
        """
        self.uri = uri
        self._session: Optional[aiohttp.ClientSession] = None

    async def _init_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _fetch_pdf(self, uri: Optional[str] = None) -> bytes:
        """
        Fetch the PDF file from the given URI and return its bytes.

        >>> import asyncio
        >>> async def main():
        ...     parser = PDFParser("https://getsamplefiles.com/download/pdf/sample-1
        ...     pdf_bytes = await parser._fetch_pdf()
        ...     assert isinstance(pdf_bytes, bytes)
        ...     await parser.close()
        ...
        >>> asyncio.run(main())
        """
        uri = uri or self.uri

        assert uri is not None, "URI must be provided to fetch PDF."

        session = await self._init_session()

        async with session.get(uri) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch PDF: {response.status}")
            return await response.read()

    async def parse_pdf(self, uri: Optional[str] = None) -> str:
        """Parse the PDF file from the given URI and return its text content.

        >>> import asyncio
        >>> async def main():
        ...     parser = PDFParser("https://getsamplefiles.com/download/pdf/sample-1.pdf")
        ...     pdf_str = await parser.parse_pdf()
        ...     assert isinstance(pdf_str, str)
        ...     await parser.close()
        ...
        >>> asyncio.run(main())
        """
        pdf_bytes = await self._fetch_pdf(uri or self.uri)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
