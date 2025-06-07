"""
Unit tests for EMCEntityExtractor, focusing on rule-based extraction.
"""

import unittest
import asyncio # For async methods, though rule-based might not be async here

from services.knowledge_graph.entity_extractor import EMCEntityExtractor
from services.knowledge_graph.emc_ontology import (
    NODE_EMC_STANDARD, NODE_FREQUENCY, NODE_FREQUENCY_RANGE,
    FrequencyNode, FrequencyRangeNode, EMCStandardNode
)

class TestEMCEntityExtractorRuleBased(unittest.TestCase):

    def setUp(self):
        # Initialize extractor without AI service for these rule-based tests
        self.extractor = EMCEntityExtractor(deepseek_service=None)

    def test_extract_emc_standards_simple(self):
        text = "The device complies with EN 55032 and IEC 61000-4-2."
        # The extract_entities method is async, so we need to run it in an event loop
        entities = asyncio.run(self.extractor.extract_entities(text, "doc1", use_ai=False, use_rules=True))

        self.assertEqual(len(entities), 2)

        standard_names = sorted([e['data']['name'] for e in entities if e['label'] == NODE_EMC_STANDARD])
        self.assertListEqual(standard_names, ["EN 55032", "IEC 61000-4-2"])

        for entity_info in entities:
            self.assertEqual(entity_info['label'], NODE_EMC_STANDARD)
            self.assertIsInstance(entity_info['data'], dict) # Data should be the dict form of the dataclass
            self.assertEqual(entity_info['data']['properties']['detection_method'], 'regex')

    def test_extract_frequencies_simple(self):
        text = "Tests were performed at 100 kHz, 2.4GHz, and 50MHz. Also a signal at 123.45 Mhz."
        entities = asyncio.run(self.extractor.extract_entities(text, "doc2", use_ai=False, use_rules=True))

        self.assertEqual(len(entities), 4)

        extracted_freqs = sorted([e['data']['name'] for e in entities if e['label'] == NODE_FREQUENCY])
        expected_freqs = sorted(["100kHz", "2.4GHz", "50MHz", "123.45Mhz"]) # Note: regex output keeps original casing for unit prefix
        self.assertListEqual(extracted_freqs, expected_freqs)

        # Check one frequency in detail
        freq_100khz_info = next(e for e in entities if e['data']['name'] == "100kHz")
        self.assertAlmostEqual(freq_100khz_info['data']['value_hz'], 100e3)
        self.assertEqual(freq_100khz_info['data']['unit'], "kHz")

        freq_2_4ghz_info = next(e for e in entities if e['data']['name'] == "2.4GHz")
        self.assertAlmostEqual(freq_2_4ghz_info['data']['value_hz'], 2.4e9)
        self.assertEqual(freq_2_4ghz_info['data']['unit'], "GHz")

        freq_123_45mhz_info = next(e for e in entities if e['data']['name'] == "123.45Mhz")
        self.assertAlmostEqual(freq_123_45mhz_info['data']['value_hz'], 123.45e6)
        self.assertEqual(freq_123_45mhz_info['data']['unit'], "Mhz")


    def test_extract_frequency_ranges_simple(self):
        text = "The scan range was 30MHz-1GHz. Another test covered 150 kHz to 80 MHz."
        entities = asyncio.run(self.extractor.extract_entities(text, "doc3", use_ai=False, use_rules=True))

        self.assertEqual(len(entities), 2)

        range_names = sorted([e['data']['name'] for e in entities if e['label'] == NODE_FREQUENCY_RANGE])
        expected_ranges = sorted(["150kHz-80MHz", "30MHz-1GHz"]) # Regex extracts original form
        self.assertListEqual(range_names, expected_ranges)

        # Check one range in detail
        range_30m_1g_info = next(e for e in entities if e['data']['name'] == "30MHz-1GHz")
        self.assertAlmostEqual(range_30m_1g_info['data']['min_value_hz'], 30e6)
        self.assertAlmostEqual(range_30m_1g_info['data']['max_value_hz'], 1e9)
        self.assertEqual(range_30m_1g_info['data']['unit'], "Hz") # Common unit is Hz for value_hz fields

    def test_no_entities_found(self):
        text = "This is a generic text without any specific EMC information."
        entities = asyncio.run(self.extractor.extract_entities(text, "doc4", use_ai=False, use_rules=True))
        self.assertEqual(len(entities), 0)

    def test_mixed_entities(self):
        text = "Product P1 complies with EN 55011. Tested from 1GHz to 18GHz. Max emission at 5.8 GHz."
        entities = asyncio.run(self.extractor.extract_entities(text, "doc5", use_ai=False, use_rules=True))

        labels = sorted([e['label'] for e in entities])
        self.assertListEqual(labels, [NODE_EMC_STANDARD, NODE_FREQUENCY, NODE_FREQUENCY_RANGE])

        std_entity = next(e for e in entities if e['label'] == NODE_EMC_STANDARD)
        self.assertEqual(std_entity['data']['name'], "EN 55011")

        freq_entity = next(e for e in entities if e['label'] == NODE_FREQUENCY)
        self.assertEqual(freq_entity['data']['name'], "5.8GHz")
        self.assertAlmostEqual(freq_entity['data']['value_hz'], 5.8e9)

        range_entity = next(e for e in entities if e['label'] == NODE_FREQUENCY_RANGE)
        self.assertEqual(range_entity['data']['name'], "1GHz-18GHz")
        self.assertAlmostEqual(range_entity['data']['min_value_hz'], 1e9)
        self.assertAlmostEqual(range_entity['data']['max_value_hz'], 18e9)

    def test_deduplication_within_rules(self):
        """ Test if the basic deduplication in extract_entities works for rule-based results."""
        text = "Uses EN 55032. Also, EN 55032 is mentioned again. And 50MHz, plus 50MHz."
        # The current rule-based extraction itself might produce duplicates if regex matches multiple times.
        # The extract_entities method has a basic deduplication step.
        entities = asyncio.run(self.extractor.extract_entities(text, "doc_dedup", use_ai=False, use_rules=True))

        standard_entities = [e for e in entities if e['label'] == NODE_EMC_STANDARD and e['data']['name'] == "EN 55032"]
        self.assertEqual(len(standard_entities), 1, "EN 55032 should be deduplicated")

        freq_entities = [e for e in entities if e['label'] == NODE_FREQUENCY and e['data']['name'] == "50MHz"]
        self.assertEqual(len(freq_entities), 1, "50MHz should be deduplicated")


if __name__ == '__main__':
    unittest.main()
