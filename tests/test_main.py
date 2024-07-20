import sys
import os
import unittest
import logging
from unittest.mock import patch, mock_open, MagicMock

# Add the directory containing utils.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    setup_logging,
    create_temp_file,
    download_url_content,
    zip_files,
    delete_file,
    process_urls,
    save_as_text,
    save_as_pdf
)

class TestUtils(unittest.TestCase):

    @patch('utils.logging.basicConfig')
    def test_setup_logging(self, mock_basicConfig):
        setup_logging(logging.DEBUG)
        mock_basicConfig.assert_called_once_with(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    @patch('utils.open', new_callable=mock_open)
    @patch('utils.uuid.uuid4', return_value='1234')
    @patch('utils.tempfile.gettempdir', return_value=os.path.normpath('/tmp'))
    def test_create_temp_file(self, mock_tempdir, mock_uuid, mock_open):
        content = "Hello, world!"
        extension = ".txt"
        expected_filename = os.path.join(mock_tempdir(), '1234.txt')
        
        result = create_temp_file(content, extension)
        mock_open.assert_called_once_with(expected_filename, 'w')
        handle = mock_open()
        handle.write.assert_called_once_with(content)
        self.assertEqual(result, expected_filename)

    @patch('utils.requests.get')
    def test_download_url_content(self, mock_get):
        url = "http://example.com"
        mock_response = MagicMock()
        mock_response.text = "Example Content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = download_url_content(url)
        mock_get.assert_called_once_with(url)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, "Example Content")

    @patch('utils.zipfile.ZipFile')
    @patch('utils.tempfile.gettempdir', return_value=os.path.normpath('/tmp'))
    def test_zip_files(self, mock_tempdir, mock_zipfile):
        file_paths = ['file1.txt', 'file2.txt']
        zip_filename = 'test.zip'
        expected_zip_path = os.path.join(mock_tempdir(), zip_filename)
        
        result = zip_files(file_paths, zip_filename)
        mock_zipfile.assert_called_once_with(expected_zip_path, 'w')
        handle = mock_zipfile()
        handle.__enter__().write.assert_any_call('file1.txt', 'file1.txt')
        handle.__enter__().write.assert_any_call('file2.txt', 'file2.txt')
        self.assertEqual(result, expected_zip_path)

    @patch('utils.os.remove')
    def test_delete_file(self, mock_remove):
        file_path = 'file_to_delete.txt'
        delete_file(file_path)
        mock_remove.assert_called_once_with(file_path)

    @patch('utils.download_url_content', return_value="URL Content")
    @patch('utils.create_temp_file', return_value=os.path.join(os.path.normpath('/tmp'), 'tempfile.txt'))
    def test_process_urls(self, mock_create_temp_file, mock_download_url_content):
        urls = ['http://example.com']
        expected_file_paths = [os.path.join(os.path.normpath('/tmp'), 'tempfile.txt')]
        
        result = process_urls(urls, save_as_text)
        self.assertEqual(result, expected_file_paths)
        mock_download_url_content.assert_called_once_with('http://example.com')
        mock_create_temp_file.assert_called_once_with("URL Content", extension=".txt")

    @patch('utils.create_temp_file', return_value=os.path.join(os.path.normpath('/tmp'), 'tempfile.pdf'))
    def test_save_as_pdf(self, mock_create_temp_file):
        content = "<html><body>PDF Content</body></html>"
        result = save_as_pdf(content)
        mock_create_temp_file.assert_called_once_with(content, extension=".pdf")
        self.assertEqual(result, os.path.join(os.path.normpath('/tmp'), 'tempfile.pdf'))

if __name__ == '__main__':
    unittest.main()