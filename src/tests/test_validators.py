"""
Tests para Validadores.
Validaciones de reglas duras y similitud semántica.
"""

import unittest
from core.validators.hard_rules import HardRulesValidator
from core.validators.semantic import SemanticValidator


class TestHardRulesValidator(unittest.TestCase):
    """Suite de tests para HardRulesValidator."""

    def setUp(self):
        self.validator = HardRulesValidator()

    def test_numeric_preservation(self):
        """Test: preservación de números."""
        original = "El producto cuesta $25.99 y el descuento es del 15%"
        rewritten = "Este artículo tiene un precio de $25.99 con 15% de descuento"
        valid, reason = self.validator.validate(original, rewritten)
        self.assertTrue(valid)

    def test_numeric_not_preserved(self):
        """Test: detección de números no preservados."""
        original = "El descuento es del 25%"
        rewritten = "El descuento es del 30%"
        valid, reason = self.validator.validate(original, rewritten)
        self.assertFalse(valid)

    def test_critical_tokens_preserved(self):
        """Test: preservación de tokens críticos."""
        original = "Juan García trabajó con OpenAI"
        rewritten = "La persona Juan García colaboró con OpenAI"
        valid, reason = self.validator.validate(original, rewritten, ["Juan García", "OpenAI"])
        self.assertTrue(valid)


class TestSemanticValidator(unittest.TestCase):
    """Suite de tests para SemanticValidator."""

    def setUp(self):
        self.validator = SemanticValidator()

    def test_cosine_similarity(self):
        """Test: cálculo de similitud coseno."""
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        similarity = SemanticValidator._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0)

    def test_orthogonal_vectors(self):
        """Test: similitud de vectores ortogonales."""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        similarity = SemanticValidator._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 0.0)

    def test_validate_without_llm(self):
        """Test: validación sin cliente LLM."""
        valid, similarity, reason = self.validator.validate("texto1", "texto2", 0.75)
        self.assertTrue(valid)  # Sin LLM, siempre válido


if __name__ == '__main__':
    unittest.main()
