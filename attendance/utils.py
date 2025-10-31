# attendance/utils.py (YANGILANGAN)
import cv2
import numpy as np
from deepface import DeepFace
from django.core.cache import cache
from django.conf import settings
import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class FaceRecognitionUtils:
    """Yuzni tanish utility klass"""

    # Cache vaqtlari
    CACHE_TIMEOUT = 3600  # 1 soat

    @staticmethod
    def get_embedding_from_image(image_path: str) -> Optional[np.ndarray]:
        """
        Rasm faylidan embedding olish (cached)
        """
        cache_key = f"embedding_{hash(image_path)}"
        cached = cache.get(cache_key)

        if cached is not None:
            return np.array(cached)

        try:
            start_time = time.time()
            rep = DeepFace.represent(
                img_path=image_path,
                model_name="VGG-Face",
                enforce_detection=True,
                detector_backend='opencv'
            )
            processing_time = time.time() - start_time

            if rep and 'embedding' in rep[0]:
                embedding = np.array(rep[0]['embedding'])
                cache.set(cache_key, embedding.tolist(), FaceRecognitionUtils.CACHE_TIMEOUT)
                logger.info(f"Embedding olish: {processing_time:.2f}s")
                return embedding

        except Exception as e:
            logger.error(f"Embedding olishda xatolik: {e}")

        return None

    @staticmethod
    def get_embedding_from_array(image_array: np.ndarray) -> Optional[np.ndarray]:
        """
        NumPy arraydan embedding olish
        """
        try:
            rep = DeepFace.represent(
                img_path=image_array,
                model_name="VGG-Face",
                enforce_detection=False
            )

            if rep and 'embedding' in rep[0]:
                return np.array(rep[0]['embedding'])

        except Exception as e:
            logger.error(f"Arraydan embedding olishda xatolik: {e}")

        return None

    @staticmethod
    def compare_embeddings(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Ikkita embedding orasidagi masofani hisoblash
        """
        try:
            return float(np.linalg.norm(embedding1 - embedding2))
        except Exception as e:
            logger.error(f"Embeddinglarni solishtirishda xatolik: {e}")
            return float('inf')

    @staticmethod
    def preprocess_image(image_array: np.ndarray) -> np.ndarray:
        """
        Rasmni oldindan qayta ishlash
        """
        try:
            # Rang kanalini tuzatish (BGR -> RGB)
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            # Kontrastni oshirish
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.0).apply(lab[:, :, 0])
            image_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

            return image_array

        except Exception as e:
            logger.warning(f"Rasmni qayta ishlashda xatolik: {e}")
            return image_array

    @staticmethod
    def validate_image_quality(image_array: np.ndarray) -> Tuple[bool, str]:
        """
        Rasm sifati tekshirish
        """
        if image_array is None:
            return False, "Rasm mavjud emas"

        height, width = image_array.shape[:2]

        # Minimal o'lcham
        if height < 100 or width < 100:
            return False, "Rasm hajmi juda kichik"

        # Yorug'lik sifati tekshirish
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array

        # Yorug'lik darajasi
        brightness = np.mean(gray)
        if brightness < 50:
            return False, "Rasm juda qorong'i"
        if brightness > 200:
            return False, "Rasm juda yorqin"

        return True, "Yaxshi"


def image_file_to_encoding(image_path: str) -> Optional[np.ndarray]:
    """Legacy funksiya - yangi klass orqali"""
    return FaceRecognitionUtils.get_embedding_from_image(image_path)


def compare_encoding(known_encoding: np.ndarray, unknown_image_path: str, threshold: float = 0.6) -> bool:
    """Legacy funksiya - yangi klass orqali"""
    unknown_encoding = FaceRecognitionUtils.get_embedding_from_image(unknown_image_path)
    if unknown_encoding is None:
        return False

    distance = FaceRecognitionUtils.compare_embeddings(known_encoding, unknown_encoding)
    return distance < threshold