from pathlib import Path
from pprint import pprint

from django.test import SimpleTestCase

from social_media.mimic.ok.log_requests.mocking import LogRequestMockTask, LogRequestMockPipeline, \
    LoadBurpSuiteRequestsFilter, ConvertToLogRequestFilter, UpdateTimestampsFilter
from social_media.mimic.ok.log_requests.reader import BurpSuiteRequestsReader, OkLogStreamDecoder, OkLogStreamEncoder
from social_media.mimic.ok.requests.log.externallog import ExternalLogRequest, ExternalLogParams


class LogRequestsTestCase(SimpleTestCase):

    def test_burp_suite_reader(self):
        reader = BurpSuiteRequestsReader()
        # file_name = 'burp_requests_test_case.xml'
        file_name = 'before_login_requests.xml'
        file_path = Path(__file__).parent / file_name

        log_stream_decoder = OkLogStreamDecoder(reader)
        log_stream_encoder = OkLogStreamEncoder()
        for raw_body in reader.read(file_path):
            original_url_encoded_body = OkLogStreamDecoder.decode_zlib(raw_body)
            decoded_original = log_stream_decoder.decode_request(raw_body)

            # Compare how the data is encoded back to the original urlencoded body
            original_url_encoded_body = OkLogStreamDecoder.decode_zlib(raw_body)
            re_url_encoded_body = log_stream_encoder.to_urlencoded(decoded_original)
            self.maxDiff = None
            self.assertEqual(original_url_encoded_body, re_url_encoded_body.decode('utf-8'), 'URL encoding failed')

            # Compare how the data is encoded back to the original byte representation
            encoded_from_original = log_stream_encoder.encode(decoded_original)
            # We must be able to decode our own encoding
            copy_url_body = OkLogStreamDecoder.decode_zlib(encoded_from_original)
            self.assertEqual(original_url_encoded_body, copy_url_body, 'Encoding failed')

    def test_mock_pipeline(self):
        file_name = 'before_login_requests.xml'
        file_path = Path(__file__).parent / file_name
        task = LogRequestMockTask(file_path=str(file_path))

        task = LogRequestMockPipeline.execute_task(task)
        self.assertEqual(len(task.raw_requests), len(task.log_requests))
        for request in task.log_requests:
            self.assertIsInstance(request, ExternalLogRequest)
            self.assertIsInstance(request.params, ExternalLogParams)
            request_params_dict =request.params.to_execute_dict()

            self.assertIsInstance(request_params_dict, dict)
            self.assertIsInstance(request_params_dict['data'], str)



