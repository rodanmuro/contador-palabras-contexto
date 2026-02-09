"""
Tests para WordCounter.
Validaciones de conteo de palabras determinístico.
"""

import unittest
from core.word_counter import WordCounter


class TestWordCounter(unittest.TestCase):
    """Suite de tests para WordCounter."""

    def setUp(self):
        self.counter = WordCounter()

    def test_count_simple_text(self):
        """Test: contar palabras en texto simple."""
        text = "El gato está en la casa"
        self.assertEqual(self.counter.count(text), 6)

    def test_count_with_punctuation(self):
        """Test: contar palabras con puntuación."""
        text = "Hola, mundo! ¿Cómo estás?"
        self.assertEqual(self.counter.count(text), 4)

    def test_count_empty_text(self):
        """Test: contar palabras en texto vacío."""
        self.assertEqual(self.counter.count(""), 0)
        self.assertEqual(self.counter.count("   "), 0)

    def test_count_with_numbers(self):
        """Test: contar palabras con números."""
        text = "Tengo 3 gatos y 5 perros"
        self.assertEqual(self.counter.count(text), 6)

    def test_extract_critical_tokens(self):
        """Test: extraer tokens críticos (números, fechas)."""
        text = "En 2024, el 80% de los datos se procesó el 15/02/2024"
        tokens = self.counter.extract_critical_tokens(text)
        self.assertIn("2024", tokens)
        self.assertIn("80%", tokens)

    def test_get_word_boundaries(self):
        """Test: obtener posiciones de palabras."""
        text = "Hola mundo"
        boundaries = self.counter.get_word_boundaries(text)
        self.assertEqual(len(boundaries), 2)


if __name__ == '__main__':
    unittest.main()
