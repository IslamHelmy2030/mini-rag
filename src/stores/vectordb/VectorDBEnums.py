from enum import Enum

class VectorDBEnums(Enum):
    FAISS = "FAISS"
    HNSWLIB = "HNSWLIB"
    QDRANT = "QDRANT"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT="dot"