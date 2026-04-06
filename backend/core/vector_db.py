"""
FAISS Vector Database for SportShield AI.
Stores and searches perceptual hash vectors for fast similarity matching.
"""

import faiss
import numpy as np
import os
import json


class VectorDB:
    """FAISS-backed vector database for media fingerprint storage and search."""

    def __init__(self, dimension: int = 256, index_path: str = None):
        """
        Initialize the vector database.
        
        Args:
            dimension: Vector dimension (hash_size^2, default 16x16=256)
            index_path: Path to save/load the FAISS index
        """
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = (
            index_path.replace(".index", "_meta.json") if index_path else None
        )

        # Use L2 distance index — similar images have small L2 distance
        self.index = faiss.IndexFlatL2(dimension)

        # Metadata: map FAISS internal IDs to asset IDs
        self.id_map: dict[int, str] = {}
        self.next_id = 0

        # Try to load existing index
        if index_path and os.path.exists(index_path):
            self.load()

    def add(self, asset_id: str, vector: np.ndarray) -> int:
        """
        Add a fingerprint vector to the index.
        
        Args:
            asset_id: The asset ID this vector belongs to
            vector: The fingerprint vector (float32)
            
        Returns:
            Internal FAISS ID
        """
        vec = vector.reshape(1, -1).astype(np.float32)
        self.index.add(vec)
        internal_id = self.next_id
        self.id_map[internal_id] = asset_id
        self.next_id += 1
        self.save()
        return internal_id

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[dict]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query fingerprint vector
            k: Number of nearest neighbors to return
            
        Returns:
            List of dicts with asset_id, distance, and confidence
        """
        if self.index.ntotal == 0:
            return []

        k = min(k, self.index.ntotal)
        vec = query_vector.reshape(1, -1).astype(np.float32)
        distances, indices = self.index.search(vec, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            asset_id = self.id_map.get(int(idx), "unknown")
            # Convert L2 distance to confidence score (0-1)
            # For binary-like vectors, max distance = dimension
            confidence = max(0, 1.0 - (dist / self.dimension))
            results.append(
                {
                    "asset_id": asset_id,
                    "distance": float(dist),
                    "confidence": float(confidence),
                    "internal_id": int(idx),
                }
            )

        return results

    def save(self):
        """Save the index and metadata to disk."""
        if not self.index_path:
            return
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        if self.metadata_path:
            meta = {"id_map": {str(k): v for k, v in self.id_map.items()},
                    "next_id": self.next_id}
            with open(self.metadata_path, "w") as f:
                json.dump(meta, f)

    def load(self):
        """Load the index and metadata from disk."""
        if self.index_path and os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        if self.metadata_path and os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                meta = json.load(f)
            self.id_map = {int(k): v for k, v in meta["id_map"].items()}
            self.next_id = meta["next_id"]

    @property
    def total_vectors(self) -> int:
        """Return the total number of vectors in the index."""
        return self.index.ntotal

    def reset(self):
        """Clear all vectors from the index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = {}
        self.next_id = 0
        self.save()
