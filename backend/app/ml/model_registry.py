from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDisasterModel(ABC):
    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Execute model prediction."""
        pass

    @abstractmethod
    def load_model(self) -> bool:
        """Load trained weights or fallback to demo rules engine."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return model readiness status."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return model specifications."""
        pass
