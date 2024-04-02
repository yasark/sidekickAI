from typing import Optional, Union, Iterator

from core.document_loaders.parser.base import BaseBlobParser
from core.document_loaders.blob_loaders import Blob
from core.documents.base import Document


class PyPDFParser(BaseBlobParser):
    """Load `PDF` using `pypdf`"""

    def __init__(
        self, password: Optional[Union[str, bytes]] = None, extract_images: bool = False
    ):
        self.password = password
        self.extract_images = extract_images

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse the blob."""
        import pypdf

        with blob.as_bytes_io() as pdf_file_obj:
            pdf_reader = pypdf.PdfReader(pdf_file_obj, password=self.password)
            yield from [
                Document(
                    page_content=page.extract_text()
                    #+ self._extract_images_from_page(page)
                ,
                    metadata={"source": blob.source, "page": page_number},
                )
                for page_number, page in enumerate(pdf_reader.pages)
            ]
