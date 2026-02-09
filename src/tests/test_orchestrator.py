"""
Tests para RewriteOrchestrator.
Validaciones del flujo completo de reescritura.
"""

import unittest
from unittest.mock import Mock, patch
from models.dto import InputRequest, Mode
from core.rewrite_orchestrator import RewriteOrchestrator
from core.llm_client import LLMClient
from core.validators.hard_rules import HardRulesValidator


class TestRewriteOrchestrator(unittest.TestCase):
    """Suite de tests para RewriteOrchestrator."""

    def setUp(self):
        """Configuración inicial para cada test."""
        # Mock del cliente LLM
        self.mock_llm = Mock(spec=LLMClient)
        self.orchestrator = RewriteOrchestrator(
            llm_client=self.mock_llm,
            hard_rules_validator=HardRulesValidator()
        )

    def test_orchestrate_text_already_in_range(self):
        """Test: texto ya está dentro del rango."""
        request = InputRequest(
            input_text="Este es un texto con diez palabras exactamente dentro rango",
            min_words=5,
            max_words=15,
            mode=Mode.BALANCED,
            max_attempts=3
        )
        result = self.orchestrator.orchestrate(request)
        self.assertEqual(result.status, "ACCEPTED")
        self.assertEqual(result.total_attempts, 0)

    def test_orchestrate_validates_request(self):
        """Test: validación de solicitud inválida."""
        request = InputRequest(
            input_text="",  # Texto vacío
            min_words=10,
            max_words=50
        )
        result = self.orchestrator.orchestrate(request)
        self.assertEqual(result.status, "ERROR")

    def test_orchestrate_with_invalid_range(self):
        """Test: rango inválido (min > max)."""
        request = InputRequest(
            input_text="Texto de ejemplo",
            min_words=50,
            max_words=10  # Inválido
        )
        result = self.orchestrator.orchestrate(request)
        self.assertEqual(result.status, "ERROR")

    def test_calculate_target_words(self):
        """Test: cálculo del objetivo de palabras."""
        # Original menor que mínimo
        target = self.orchestrator._calculate_target_words(5, 10, 50)
        self.assertEqual(target, 10)

        # Original mayor que máximo
        target = self.orchestrator._calculate_target_words(100, 10, 50)
        self.assertEqual(target, 50)

        # Original dentro del rango
        target = self.orchestrator._calculate_target_words(30, 10, 50)
        self.assertEqual(target, 30)


if __name__ == '__main__':
    unittest.main()
