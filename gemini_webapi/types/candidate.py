from dataclasses import dataclass, field
from typing import List
from .image import Image, WebImage, GeneratedImage

@dataclass
class Candidate:
    """
    A single reply candidate object in the model output. A full response from Gemini usually contains multiple reply candidates.

    Parameters
    ----------
    rcid: `str`
        Reply candidate ID to build the metadata
    text: `str`
        Text output
    web_images: `List[WebImage]`, optional
        List of web images in reply, can be empty.
    generated_images: `List[GeneratedImage]`, optional
        List of generated images in reply, can be empty
    """

    rcid: str
    text: str
    web_images: List[WebImage] = field(default_factory=list)
    generated_images: List[GeneratedImage] = field(default_factory=list)

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Candidate(rcid='{self.rcid}', text='{len(self.text) <= 20 and self.text or self.text[:20] + '...'}', images={self.images})"

    @property
    def images(self) -> List[Image]:
        return self.web_images + self.generated_images