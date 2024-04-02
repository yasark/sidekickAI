import os
import re
import tempfile
from abc import ABC
from pathlib import Path
from typing import Union, Optional, Dict, Iterator
from urllib.parse import urlparse

import requests

from core.document_loaders.base import BaseLoader
from core.document_loaders.blob_loaders import Blob
from core.document_loaders.parser.pdf import PyPDFParser
from core.documents.base import Document


class BasePDFLoader(BaseLoader, ABC):
    """Base Loader class for `PDF` files.

    If the file is a web path, it will download it to a temporary file, use it, then
        clean up the temporary file after completion.
    """

    def __init__(self, file_path: Union[str, Path], *, headers: Optional[Dict] = None):
        """Initialize with a file path.

        Args:
            file_path: Either a local, S3 or web path to a PDF file.
            headers: Headers to use for GET request to download a file from a web path.
        """
        self.file_path = str(file_path)
        self.web_path = None
        self.headers = headers
        if "~" in self.file_path:
            self.file_path = os.path.expanduser(self.file_path)

        # If the file is a web path or S3, download it to a temporary file, and use that
        if not os.path.isfile(self.file_path) and self._is_valid_url(self.file_path):
            self.temp_dir = tempfile.TemporaryDirectory()
            _, suffix = os.path.splitext(self.file_path)
            if self._is_s3_presigned_url(self.file_path):
                suffix = urlparse(self.file_path).path.split("/")[-1]
            temp_pdf = os.path.join(self.temp_dir.name, f"tmp{suffix}")
            self.web_path = self.file_path
            if not self._is_s3_url(self.file_path):
                r = requests.get(self.file_path, headers=self.headers)
                if r.status_code != 200:
                    raise ValueError(
                        "Check the url of your file; returned status code %s"
                        % r.status_code
                    )

                with open(temp_pdf, mode="wb") as f:
                    f.write(r.content)
                self.file_path = str(temp_pdf)
        elif not os.path.isfile(self.file_path):
            raise ValueError("File path %s is not a valid file or url" % self.file_path)

    def __del__(self) -> None:
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if the url is valid."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    @staticmethod
    def _is_s3_url(url: str) -> bool:
        """check if the url is S3"""
        try:
            result = urlparse(url)
            if result.scheme == "s3" and result.netloc:
                return True
            return False
        except ValueError:
            return False

    @staticmethod
    def _is_s3_presigned_url(url: str) -> bool:
        """Check if the url is a presigned S3 url."""
        try:
            result = urlparse(url)
            return bool(re.search(r"\.s3\.amazonaws\.com$", result.netloc))
        except ValueError:
            return False

    @property
    def source(self) -> str:
        return self.web_path if self.web_path is not None else self.file_path


class PyPDFLoader(BasePDFLoader):
    """Load PDF using pypdf into list of documents.

    Loader chunks by page and stores page numbers in metadata.
    """

    def __init__(
            self,
            file_path: str,
            password: Optional[Union[str, bytes]] = None,
            headers: Optional[Dict] = None,
            extract_images: bool = False,
    ) -> None:
        """Initialize with a file path."""
        try:
            import pypdf  # noqa:F401
        except ImportError:
            raise ImportError(
                "pypdf package not found, please install it with " "`pip install pypdf`"
            )
        super().__init__(file_path, headers=headers)
        self.parser = PyPDFParser(password=password, extract_images=extract_images)

    def lazy_load(
            self,
    ) -> Iterator[Document]:
        """Lazy load given path as pages."""
        if self.web_path:
            blob = Blob.from_data(open(self.file_path, "rb").read(), path=self.web_path)
        else:
            blob = Blob.from_path(self.file_path)
        yield from self.parser.parse(blob)


if __name__ == '__main__':
    data_loader = PyPDFLoader(file_path="/Users/yasar/startup_home/repo/sidekickAI/data/resume_2024.pdf")
    data = data_loader.load()
    pages = data_loader.load_and_split()
    print(pages)
