from galvanalyser.database.util.battery_exceptions import UnsupportedFileTypeError
from itertools import accumulate
import traceback
from galvanalyser.database.experiment.timeseries_data_row import (
    RECORD_NO_COLUMN_ID,
    TEST_TIME_COLUMN_ID,
    VOLTAGE_COLUMN_ID,
    AMPS_COLUMN_ID,
    ENERGY_CAPACITY_COLUMN_ID,
    CHARGE_CAPACITY_COLUMN_ID,
    TEMPERATURE_COLUMN_ID,
    STEP_TIME_COLUMN_ID,
    IMPEDENCE_MAG_COLUMN_ID,
    IMPEDENCE_PHASE_COLUMN_ID,
    FREQUENCY_COLUMN_ID,
)
from .unit import Unit

# see https://gist.github.com/jsheedy/ed81cdf18190183b3b7d
# https://stackoverflow.com/a/30721460


class InputFile:
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata, self.column_info = self.load_metadata()

    def get_columns(self):
        name_to_type_id = self.get_file_column_to_standard_column_mapping()

        # verify that every file col has units
        for col, std in name_to_type_id.items():
            if col not in self.column_info:
                continue
            if 'unit' not in self.column_info[col]:
                raise RuntimeError((
                    "Unit not provided for standard column mapping.\n"
                    "file_column_to_standard_column is {}: {}\n"
                    "column_info is {}\n"
                ).format(col, std, self.column_info[col]))
            if self.column_info[col]['unit'] not in Unit.get_all_units():
                raise RuntimeError(
                    "Unknown unit {} provided for standard column mapping"
                    .format(self.column_info[col]['unit'])
                )

        columns = [
            (name, name_to_type_id.get(name, -1))
            for name, info in self.column_info.items()
            if info['has_data'] and info['is_numeric']
        ]

        return columns

    def get_test_start_date(self):
        return self.metadata["Date of Test"]

    def convert_unit(self, name, value):
        if 'unit' in self.column_info[name]:
            unit = self.column_info[name]['unit']
            value = Unit.convert(unit, value)
        return value

    def get_data_row_generator(
        self,
        column_name_to_id, last_values=None,
    ):
        # create some useful mappings
        name_to_type_id = {
            name: type_id
            for name, type_id in self.get_columns()
        }
        type_id_to_col_id = {
            name_to_type_id[name]: col_id
            for name, col_id in column_name_to_id.items()
        }

        sample_col_id = type_id_to_col_id.get(RECORD_NO_COLUMN_ID, None)

        # reconstruct previous row mapping col ids to values
        if last_values is not None:
            previous_row = {
                tsdr.column_id: tsdr.value for tsdr in last_values
            }
            last_rec_no = last_values[0].sample_no
        else:
            previous_row = {}
            for name, col_id in column_name_to_id.items():
                previous_row[col_id] = 0.0
            last_rec_no = -1

        # The psycopg2 cursor.copy_from method needs null values to be
        # represented as a literal '\N'
        def tsv_format(value):
            return str(value) if value is not None else "\\N"

        try:
            for index, row_with_names in enumerate(self.load_data(
                self.file_path, name_to_type_id.keys()
            )):
                # convert dict mapping names to values to dict
                # of col_id => value, use unit info
                # to convert to database units
                row = {
                    column_name_to_id[name]: self.convert_unit(name, value)
                    for name, value in row_with_names.items()
                }

                # get the current sample number
                rec_no = int(row.get(sample_col_id, index))
                if rec_no <= last_rec_no:
                    continue

                # yield the new timeseries_data row
                for col_id, value in row.items():
                    if col_id == sample_col_id:
                        continue
                    timeseries_data_row = [
                        rec_no,
                        col_id,
                        value,
                    ]
                    yield "\t".join(map(tsv_format, timeseries_data_row))
                previous_row = row

        except:
            traceback.print_exc()
            raise

    def load_data(self, file_path, available_desired_columns):
        raise UnsupportedFileTypeError

    def get_data_labels(self):
        raise UnsupportedFileTypeError

    def get_file_column_to_standard_column_mapping(self):
        """
            returns map of file column name strings to column id numbers
        """
        raise UnsupportedFileTypeError

    def load_metadata(self):
        raise UnsupportedFileTypeError
