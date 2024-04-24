from dataclasses import dataclass, field
from typing import List
from .image import Image
from .candidate import Candidate

@dataclass
class ModelOutput:
    """
    Classified output from gemini.google.com

    Parameters
    ----------
    metadata: `List[str]`
        List of chat metadata `[cid, rid, rcid]`, can be shorter than 3 elements, like `[cid, rid]` or `[cid]` only
    candidates: `List[Candidate]`
        List of all candidates returned from gemini
    chosen: `int`, optional
        Index of the chosen candidate, by default will choose the first one
    """

    metadata: List[str]
    candidates: List[Candidate]
    chosen: int = 0

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"ModelOutput(metadata={self.metadata}, chosen={self.chosen}, candidates={self.candidates})"

    @property
    def text(self) -> str:
        return self.candidates[self.chosen].text

    @property
    def images(self) -> List[Image]:
        return self.candidates[self.chosen].images

    @property
    def rcid(self) -> str:
        return self.candidates[self.chosen].rcid