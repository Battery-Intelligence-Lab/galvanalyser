import psycopg2


class MetaDataRow:
    def __init__(
        self, experiment_id, label_name, lower_bound, upper_bound, info=None
    ):
        self.experiment_id = experiment_id
        self.label_name = label_name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.info = info

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.metadata "
                    "(experiment_id, label_name, sample_range, info) "
                    "VALUES (%s, %s, '[%s, %s)', %s)"
                ),
                [
                    self.experiment_id,
                    self.label_name,
                    self.lower_bound,
                    self.upper_bound,
                    self.info,
                ],
            )

    @staticmethod
    def select_from_experiment_id(experiment_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT label_name, sample_range, info "
                    "FROM experiment.metadata "
                    "WHERE experiment_id=(%s)"
                ),
                [experiment_id],
            )
            records = cursor.fetchall()
            return [
                MetaDataRow(
                    experiment_id=experiment_id,
                    label_name=result[0],
                    lower_bound=result[1].lower,
                    upper_bound=result[1].upper,
                    info=result[2],
                )
                for result in records
            ]

    @staticmethod
    def select_from_experiment_id_and_label_name(
        experiment_id, label_name, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT sample_range, info FROM experiment.metadata "
                    "WHERE experiment_id=(%s) AND label_name=(%s)"
                ),
                [experiment_id, label_name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return MetaDataRow(
                experiment_id=experiment_id,
                label_name=label_name,
                lower_bound=result[0][0],
                upper_bound=result[0][1],
                info=result[1],
            )
