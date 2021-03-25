from harvester_test_case import HarvesterTestCase
from timeit import default_timer as timer
import harvester.__main__ as harvester
from pygalvanalyser.harvester.harvester_row import HarvesterRow
from pygalvanalyser.harvester.monitored_path_row import MonitoredPathRow
from pygalvanalyser.harvester.observed_file_row import ObservedFileRow
from pygalvanalyser.experiment.dataset_row import DatasetRow
import pygalvanalyser.util.battery_exceptions as battery_exceptions
from harvester.ivium_input_file import IviumInputFile
from harvester.biologic_input_file import BiologicMprInputFile
from harvester.maccor_input_file import MaccorInputFile

import os
import json
from datetime import datetime, timezone, timedelta
import glob

class TestMaccorFileFormat(HarvesterTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*'):
            try:
                input_file = MaccorInputFile(filename)
            except battery_exceptions.UnsupportedFileTypeError:
                continue

            mapping = \
                input_file.get_standard_column_to_file_column_mapping()
            self.assertGreater(len(mapping), 0)

    def test_read_csv_files(self):
        files_found = 0
        for filename in glob.glob(self.DATA_DIR + '/*'):
            try:
                input_file = MaccorInputFile(filename)
                files_found += 1
            except battery_exceptions.UnsupportedFileTypeError:
                continue
            metadata, columns = input_file.load_metadata()
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            self.assertGreater(num_tasks, 0)
            data_generator = input_file.load_data(
                filename, ["Amps", "Volts"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])
        self.assertGreater(files_found, 0)


class TestIviumFileFormat(HarvesterTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*.idf'):
            input_file = IviumInputFile(filename)
            mapping = \
                input_file.get_standard_column_to_file_column_mapping()
            self.assertGreater(len(mapping), 0)
            row_raw = next(input_file.load_data(
                filename, ["amps"]
            ))
            row_converted = next(input_file.convert_units(
                input_file.load_data(
                    filename, ["amps"]
                )
            ))
            self.assertEqual(
                row_raw['amps'],
                row_converted['amps']
            )

    def test_read_idf_files(self):
        for filename in glob.glob(self.DATA_DIR + '/*.idf'):
            input_file = IviumInputFile(filename)
            metadata, columns = input_file.load_metadata()
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            num_tasks_from_metadata = len(
                metadata['misc_file_data']['ivium format metadata'][0]['Tasks']
            )
            self.assertEqual(num_tasks, num_tasks_from_metadata)
            data_generator = input_file.load_data(
                filename, ["amps", "volts", "test_time"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])

class TestBiologicFileFormat(HarvesterTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*.mpr'):
            input_file = BiologicMprInputFile(filename)
            mapping = \
                input_file.get_standard_column_to_file_column_mapping()
            self.assertGreater(len(mapping), 0)
            row_raw = next(input_file.load_data(
                filename, ["I/mA"]
            ))
            row_converted = next(input_file.convert_units(
                input_file.load_data(
                    filename, ["I/mA"]
                )
            ))
            self.assertEqual(
                1e-3 * row_raw['I/mA'],
                row_converted['I/mA']
            )

    def test_read_mpr_files(self):
        for filename in glob.glob(self.DATA_DIR + '/*.mpr'):
            input_file = BiologicMprInputFile(filename)
            metadata, columns = input_file.load_metadata()
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            self.assertGreater(num_tasks, 0)
            data_generator = input_file.load_data(
                filename, ["I/mA"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])


class TestHarvester(HarvesterTestCase):
    # well capture all the filename that failed here
    def setUp(self):
        self.verificationErrors = []

    # if any files failed, print errors here
    def tearDown(self):
        self.maxDiff = None
        self.assertEqual([], self.verificationErrors)

    def test_main(self):
        template = {
            "database_username": self.HARVESTER,
            "database_password": self.HARVESTER_PWD,
            "database_host": "galvanalyser_postgres",
            "database_port": 5433,
            "database_name": self.DATABASE,
            "machine_id": self.MACHINE_ID,
            "institution": self.HARVESTER_INSTITUTION,
        }
        if not os.path.exists('./config'):
            os.makedirs('./config')

        with open('./config/harvester-config.json', "w+") as json_file:
            json.dump(template, json_file, indent=4)

        harvester.main(None)

        # should have added files to database
        harvester_row = HarvesterRow.select_from_machine_id(
            self.MACHINE_ID,
            self.conn
        )
        self.assertIsNotNone(harvester_row)

        monitor_path = \
            MonitoredPathRow.select_from_harvester_id_and_path(
                harvester_row.id,
                self.DATA_DIR,
                self.conn
            )
        self.assertIsNotNone(monitor_path)
        file = ObservedFileRow.select_from_id_(
                    monitor_path.monitor_path_id,
                    self.conn
                )
        # check all files are in, then mark them stable for > 1 min
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                # check that filename is in list of files
                print(name)
                file = ObservedFileRow.select_from_id_and_path(
                    monitor_path.monitor_path_id,
                    name,
                    self.conn
                )
                self.assertIsNotNone(file)

                file.file_state = 'STABLE'
                file.last_observed_time = \
                    datetime.now(timezone.utc) - timedelta(minutes=1),
                file.insert(self.conn)
        self.conn.commit()


        # files are now stable, rerun main to insert them
        harvester.main(None)

        # check that they are all inserted successfully
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                file = ObservedFileRow.select_from_id_and_path(
                    monitor_path.monitor_path_id,
                    name,
                    self.conn
                )
                self.assertIsNotNone(file)
                try:
                    self.assertEqual(file.file_state, 'IMPORTED')
                except AssertionError as e:
                    self.verificationErrors.append(
                        'filename = {}, error = {}'.format(name, e)
                    )


if __name__ == '__main__':
    unittest.main()


