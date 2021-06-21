import os
import json
import sys
import unittest

# Add the project directory to the pythonpath
test_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(test_dir)
lambda_dir = os.path.join(project_dir, 'lambda_function')
tests_dir = os.path.join(project_dir, 'tests')
events_dir = os.path.join(tests_dir, 'events')
sys.path.insert(0, lambda_dir)

from lambda_function import lambda_handler


class TestPipeline(unittest.TestCase):
    """-------------------------------------------------------------------
    Tests running the suite of a2e tsdat pipelines against a test
    aws bucket.
    -------------------------------------------------------------------"""
    def setUp(self) -> None:
        # Set the environment variables for storage
        os.environ['STORAGE_CLASSNAME'] = 'tsdat.io.AwsStorage'
        os.environ['RETAIN_INPUT_FILES'] = 'True'
        os.environ['STORAGE_BUCKET'] = 'a2e-tsdat-test-output'

    def tearDown(self) -> None:
        super().tearDown()

    def run_pipeline(self, pipeline, location):
        json_file = os.path.join(events_dir, pipeline, location, 's3-event.json')
        with open(json_file) as f:
            event = json.load(f)
            lambda_handler(event, '')

    def test_buoy(self):
        self.run_pipeline('a2e_buoy_ingest', 'humboldt')
        self.run_pipeline('a2e_buoy_ingest', 'morro')

    def test_imu(self):
        self.run_pipeline('a2e_imu_ingest', 'humboldt')
        self.run_pipeline('a2e_imu_ingest', 'morro')

    def test_lidar(self):
        self.run_pipeline('a2e_lidar_ingest', 'humboldt')
        self.run_pipeline('a2e_lidar_ingest', 'morro')

    def test_waves(self):
        self.run_pipeline('a2e_waves_ingest', 'humboldt')
        self.run_pipeline('a2e_waves_ingest', 'morro')


if __name__ == '__main__':
    unittest.main()



# a2e-tsdat-test
