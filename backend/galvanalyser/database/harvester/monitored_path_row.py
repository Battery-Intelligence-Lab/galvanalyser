import psycopg2
import json
from galvanalyser.database import Row


class MonitoredPathRow(Row):
    def __init__(
        self, harvester_id, monitored_for, path, id_=None
    ):
        self.harvester_id = harvester_id
        if monitored_for is None:
            self.monitored_for = []
        else:
            self.monitored_for = monitored_for
        self.path = path
        self.id = id_

    def __str__(self):
        return (
            'MonitoredPathRow(harvester_id={}, monitored_for={} '
            'path={}, id={})'
        ).format(
            self.harvester_id,
            self.monitored_for,
            self.path,
            self.id
        )

    def to_dict(self):
        obj = {
            'harvester_id': self.harvester_id,
            'monitored_for': self.monitored_for,
            'path': self.path,
            'id': self.id,
        }
        return obj

    def _insert_monitored_paths(self, cursor):
        if len(self.monitored_for) > 0:
            monitored_for_rows = b','.join(
                cursor.mogrify(
                    "(%s,%s)", [self.id, x]
                )
                for x in self.monitored_for
            )
            cursor.execute(
                (
                    b"INSERT INTO harvesters.monitored_for "
                    b"(path_id, user_id) VALUES " + monitored_for_rows
                ),
            )

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO harvesters.monitored_path "
                    "(harvester_id, path) VALUES (%s, %s) "
                    "RETURNING id"
                ),
                [self.harvester_id, self.path],
            )
            self.id = cursor.fetchone()[0]

            self._insert_monitored_paths(cursor)

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE harvesters.monitored_path SET "
                    "harvester_id = (%s), "
                    "path = (%s) "
                    "WHERE id=(%s)"
                ),
                [
                    self.harvester_id,
                    self.path, self.id
                ],
            )
            cursor.execute(
                (
                    "DELETE FROM harvesters.monitored_for "
                    "WHERE path_id=(%s)"
                ),
                [self.id],
            )
            self._insert_monitored_paths(cursor)

    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM harvesters.monitored_path "
                    "WHERE id=(%s)"
                ),
                [self.id],
            )

    @staticmethod
    def _get_monitored_for(id_, cursor):
        cursor.execute(
            (
                "SELECT user_id FROM "
                "harvesters.monitored_for "
                "WHERE path_id=(%s)"
            ),
            [id_],
        )
        records = cursor.fetchall()
        return [result[0] for result in records]

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT harvester_id, path FROM "
                    "harvesters.monitored_path "
                    "WHERE id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return MonitoredPathRow(
                harvester_id=result[0],
                monitored_for=(
                    MonitoredPathRow._get_monitored_for(result[0], cursor)
                ),
                path=result[1],
                id_=id_,
            )

    @staticmethod
    def select_from_harvester_id(harvester_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT path, id FROM "
                    "harvesters.monitored_path "
                    "WHERE harvester_id=(%s)"
                ),
                [harvester_id],
            )
            records = cursor.fetchall()
            return [
                MonitoredPathRow(
                    harvester_id=harvester_id,
                    monitored_for=(
                        MonitoredPathRow._get_monitored_for(result[1], cursor)
                    ),
                    path=result[0],
                    id_=result[1],
                )
                for result in records
            ]

    @staticmethod
    def select_from_harvester_id_and_path(harvester_id, path, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id FROM "
                    "harvesters.monitored_path "
                    "WHERE harvester_id=(%s) AND path=(%s)"
                ),
                [harvester_id, path],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return MonitoredPathRow(
                harvester_id=harvester_id,
                monitored_for=(
                    MonitoredPathRow._get_monitored_for(result[0], cursor)
                ),
                path=path,
                id_=result[0],
            )
