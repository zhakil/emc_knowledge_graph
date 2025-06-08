"""
Unit tests for EMCFileProcessor.
Dependencies (DeepSeekEMCService, EMCGraphManager) will be mocked.
File I/O for content extraction will also be mocked for most tests.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open, call
import asyncio
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from services.file_processing.emc_file_processor import (
    EMCFileProcessor, FileMetadata, ExtractionResult,
    EMCContentExtractor, FormatConverter # If these have complex logic, they might need own tests
)
# Mocked service types
# from services.ai_integration.deepseek_service import DeepSeekEMCService
# from services.knowledge_graph.graph_manager import EMCGraphManager

# A dummy DeepSeekEMCService class for type hinting if the actual import is problematic
class MockDeepSeekEMCService:
    async def extract_entities_from_text(self, text_content: str, session_id: str):
        return {"content": '{"entities": [], "relationships": []}'} # Default mock response

class MockEMCGraphManager:
    async def process_document_content(self, text_content: str, document_id: str, document_metadata: dict):
        return {"status": "completed", "entities_extracted_count": 0, "errors": []}


class TestEMCFileProcessor(unittest.TestCase):

    def setUp(self):
        self.mock_deepseek_service = AsyncMock(spec=MockDeepSeekEMCService)
        self.mock_graph_manager = AsyncMock(spec=MockEMCGraphManager)

        self.storage_path = Path("./test_uploads") # Use a test-specific path
        self.storage_path.mkdir(exist_ok=True) # Ensure it exists for tests that might touch FS

        self.processor = EMCFileProcessor(
            deepseek_service=self.mock_deepseek_service,
            storage_path=str(self.storage_path),
            graph_manager=self.mock_graph_manager
        )

        # Sample file path and ID
        self.sample_file_path = self.storage_path / "sample.pdf"
        self.sample_file_id = "file_pdf_sample_123"
        self.sample_content = "This is sample PDF content with EMC data."

        # Mock FileMetadata instance (as would be created by _extract_metadata)
        self.mocked_metadata = FileMetadata(
            file_id=self.sample_file_id,
            filename=self.sample_file_path.name,
            file_type="pdf",
            size_bytes=1000,
            mime_type="application/pdf",
            encoding=None,
            checksum="fake_checksum",
            upload_time=datetime.now(),
            processed=False,
            extraction_status="pending"
        )

        # Mock ExtractionResult from _extract_entities_with_ai
        self.mocked_extraction_result = ExtractionResult(
            file_id=self.sample_file_id,
            entities=[{"type": "EMCStandard", "name": "MockStd"}],
            relationships=[],
            content_summary="Mock summary",
            confidence_score=0.9,
            processing_time=0.1,
            extracted_at=datetime.now()
        )

    @patch('services.file_processing.emc_file_processor.Path.exists')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_metadata')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_content')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_entities_with_ai')
    async def test_process_file_happy_path_pdf(
        self, mock_ai_extract, mock_content_extract, mock_metadata_extract, mock_path_exists
    ):
        mock_path_exists.return_value = True # File exists
        mock_metadata_extract.return_value = self.mocked_metadata
        mock_content_extract.return_value = self.sample_content
        mock_ai_extract.return_value = self.mocked_extraction_result
        self.mock_graph_manager.process_document_content.return_value = {
            "status": "completed", "errors": []
        }

        metadata_out, extraction_out = await self.processor.process_file(self.sample_file_path, self.sample_file_id)

        mock_path_exists.assert_called_once()
        mock_metadata_extract.assert_called_once_with(Path(self.sample_file_path), self.sample_file_id)
        mock_content_extract.assert_called_once_with(Path(self.sample_file_path), self.mocked_metadata.mime_type)
        mock_ai_extract.assert_called_once_with(self.sample_file_id, self.sample_content, self.mocked_metadata)

        self.mock_graph_manager.process_document_content.assert_called_once_with(
            text_content=self.sample_content,
            document_id=self.sample_file_id,
            document_metadata=asdict(self.mocked_metadata) # Ensure it's called with dict
        )

        self.assertEqual(metadata_out.file_id, self.sample_file_id)
        self.assertTrue(metadata_out.processed)
        # Status might be 'completed' or 'completed_with_graph_errors' etc. depending on graph_summary
        # For this happy path, it should be related to successful completion.
        self.assertIn(metadata_out.extraction_status, ["completed_basic_extraction_only", "completed"]) # Depends on graph_summary content

        self.assertEqual(extraction_out.file_id, self.sample_file_id)
        self.assertEqual(len(extraction_out.entities), 1)

        # Check stats (simplified check)
        self.assertGreaterEqual(self.processor._processing_stats['entities_extracted'], 1)


    @patch('services.file_processing.emc_file_processor.Path.exists')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_metadata')
    async def test_process_file_unsupported_format(self, mock_metadata_extract, mock_path_exists):
        mock_path_exists.return_value = True
        unsupported_metadata = FileMetadata(
            file_id="unsupported_file", filename="test.unsupported", file_type="unsupported",
            size_bytes=100, mime_type="application/unknown", encoding=None, checksum="cs", upload_time=datetime.now()
        )
        mock_metadata_extract.return_value = unsupported_metadata

        # Make _is_supported_format return False for this file type
        with patch.object(self.processor, '_is_supported_format', return_value=False):
            metadata_out, extraction_out = await self.processor.process_file("test.unsupported")

        self.assertEqual(metadata_out.extraction_status, "unsupported_format")
        self.assertIsNone(extraction_out)
        self.mock_graph_manager.process_document_content.assert_not_called()

    @patch('services.file_processing.emc_file_processor.Path.exists')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_metadata')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_content')
    async def test_process_file_empty_content(self, mock_content_extract, mock_metadata_extract, mock_path_exists):
        mock_path_exists.return_value = True
        mock_metadata_extract.return_value = self.mocked_metadata
        mock_content_extract.return_value = "   " # Empty or whitespace content

        metadata_out, extraction_out = await self.processor.process_file(self.sample_file_path)

        self.assertEqual(metadata_out.extraction_status, "empty_content")
        self.assertIsNone(extraction_out)
        self.mock_graph_manager.process_document_content.assert_not_called()

    @patch('services.file_processing.emc_file_processor.Path.exists')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_metadata')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_content')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_entities_with_ai')
    async def test_process_file_graph_manager_fails(
        self, mock_ai_extract, mock_content_extract, mock_metadata_extract, mock_path_exists
    ):
        mock_path_exists.return_value = True
        mock_metadata_extract.return_value = self.mocked_metadata
        mock_content_extract.return_value = self.sample_content
        mock_ai_extract.return_value = self.mocked_extraction_result
        self.mock_graph_manager.process_document_content.side_effect = Exception("Graph DB connection error")

        metadata_out, extraction_out = await self.processor.process_file(self.sample_file_path)

        self.assertEqual(metadata_out.extraction_status, "graph_processing_failed")
        self.assertEqual(self.processor._processing_stats['graph_processing_invocation_errors'], 1)
        self.mock_graph_manager.process_document_content.assert_called_once() # It was called

    @patch('services.file_processing.emc_file_processor.Path.exists')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_metadata')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_content')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._extract_entities_with_ai')
    async def test_process_file_graph_processing_skipped_by_flag(
        self, mock_ai_extract, mock_content_extract, mock_metadata_extract, mock_path_exists
    ):
        mock_path_exists.return_value = True
        mock_metadata_extract.return_value = self.mocked_metadata
        mock_content_extract.return_value = self.sample_content
        mock_ai_extract.return_value = self.mocked_extraction_result

        metadata_out, extraction_out = await self.processor.process_file(
            self.sample_file_path, trigger_graph_processing=False # Explicitly skip
        )

        self.mock_graph_manager.process_document_content.assert_not_called()
        self.assertEqual(metadata_out.extraction_status, "completed_basic_extraction_only")


    # Test actual content extraction for a simple type like TXT
    # This requires mocking aiofiles.open
    @patch('services.file_processing.emc_file_processor.aiofiles.open', new_callable=AsyncMock)
    @patch('services.file_processing.emc_file_processor.Path.exists')
    @patch('services.file_processing.emc_file_processor.EMCFileProcessor._detect_encoding') # Mock encoding detection
    async def test_extract_text_content_integration(self, mock_detect_encoding, mock_path_exists, mock_aio_open):
        mock_path_exists.return_value = True
        mock_detect_encoding.return_value = 'utf-8' # Assume utf-8 for test

        # Setup mock for aiofiles.open().read()
        mock_file_handle = AsyncMock()
        mock_file_handle.read = AsyncMock(return_value="Simple text content.")
        # __aenter__ and __aexit__ are needed for async with context manager
        mock_aio_open.return_value.__aenter__.return_value = mock_file_handle
        mock_aio_open.return_value.__aexit__.return_value = None # Or an AsyncMock if it needs to return something

        txt_file_path = self.storage_path / "test.txt"
        content = await self.processor._extract_content(txt_file_path, "text/plain")

        self.assertEqual(content, "Simple text content.")
        mock_aio_open.assert_called_once_with(txt_file_path, 'r', encoding='utf-8')


    def tearDown(self):
        # Clean up any files created in storage_path if necessary,
        # but these tests primarily use mocks for file operations.
        pass

if __name__ == '__main__':
    unittest.main()
