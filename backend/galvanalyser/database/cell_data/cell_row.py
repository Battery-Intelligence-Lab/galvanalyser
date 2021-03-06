import psycopg2
from galvanalyser.database import Row


class CellRow(Row):
    def __init__(
        self,
        name,
        id=None,
        manufacturer=None,
        form_factor=None,
        link_to_datasheet=None,
        anode_chemistry=None,
        cathode_chemistry=None,
        nominal_capacity=None,
        nominal_cell_weight=None,
    ):
        self.id = id
        self.name = name
        self.manufacturer = manufacturer
        self.form_factor = form_factor
        self.link_to_datasheet = link_to_datasheet
        self.anode_chemistry = anode_chemistry
        self.cathode_chemistry = cathode_chemistry
        self.nominal_capacity = nominal_capacity
        self.nominal_cell_weight = nominal_cell_weight

    def to_dict(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'form_factor': self.form_factor,
            'link_to_datasheet': self.link_to_datasheet,
            'anode_chemistry': self.anode_chemistry,
            'cathode_chemistry': self.cathode_chemistry,
            'nominal_capacity': self.nominal_capacity,
            'nominal_cell_weight': self.nominal_cell_weight,
        }
        return obj

    def __eq__(self, other):
        if isinstance(other, CellRow):
            return (
                self.id == other.id and
                self.name == other.name and
                self.manufacturer == other.manufacturer and
                self.form_factor == other.form_factor and
                self.link_to_datasheet == other.link_to_datasheet and
                self.anode_chemistry == other.anode_chemistry and
                self.cathode_chemistry == other.cathode_chemistry and
                self.nominal_capacity == other.nominal_capacity and
                self.nominal_cell_weight == other.nominal_cell_weight
            )

        return False

    def __repr__(self):
        return ('CellRow({}, {}, {}, {}, {}, {}, {}, {})'
                .format(
                    self.id,
                    self.name,
                    self.manufacturer,
                    self.form_factor,
                    self.link_to_datasheet,
                    self.anode_chemistry,
                    self.cathode_chemistry,
                    self.nominal_capacity,
                    self.nominal_cell_weight,
                ))

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO cell_data.cell ("
                    "name, manufacturer, form_factor, "
                    "link_to_datasheet, anode_chemistry, "
                    "cathode_chemistry, nominal_capacity, "
                    "nominal_cell_weight) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id"
                ),
                [
                    self.name,
                    self.manufacturer,
                    self.form_factor,
                    self.link_to_datasheet,
                    self.anode_chemistry,
                    self.cathode_chemistry,
                    self.nominal_capacity,
                    self.nominal_cell_weight,
                ],
            )
            result = cursor.fetchone()
            self.id = result[0]

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE cell_data.cell SET "
                    "name = (%s), "
                    "manufacturer = (%s), form_factor = (%s), "
                    "link_to_datasheet = (%s), anode_chemistry = (%s), "
                    "cathode_chemistry = (%s), nominal_capacity = (%s), "
                    "nominal_cell_weight = (%s) "
                    "WHERE id=(%s)"
                ),
                [
                    self.name,
                    self.manufacturer, self.form_factor,
                    self.link_to_datasheet, self.anode_chemistry,
                    self.cathode_chemistry, self.nominal_capacity,
                    self.nominal_cell_weight, self.id
                ],
            )

    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM cell_data.cell "
                    "WHERE id=(%s)"
                ),
                [self.id],
            )

    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, manufacturer, form_factor, "
                    "link_to_datasheet, anode_chemistry, "
                    "cathode_chemistry, nominal_capacity, "
                    "nominal_cell_weight FROM "
                    "cell_data.cell"
                ),
            )
            records = cursor.fetchall()
            return [
                CellRow(
                    id=result[0],
                    name=result[1],
                    manufacturer=result[2],
                    form_factor=result[3],
                    link_to_datasheet=result[4],
                    anode_chemistry=result[5],
                    cathode_chemistry=result[6],
                    nominal_capacity=result[7],
                    nominal_cell_weight=result[8],
                )
                for result in records
            ]

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT name, manufacturer, form_factor, "
                    "link_to_datasheet, anode_chemistry, "
                    "cathode_chemistry, nominal_capacity, "
                    "nominal_cell_weight FROM "
                    "cell_data.cell "
                    "WHERE id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return CellRow(
                id=id_,
                name=result[0],
                manufacturer=result[1],
                form_factor=result[2],
                link_to_datasheet=result[3],
                anode_chemistry=result[4],
                cathode_chemistry=result[5],
                nominal_capacity=result[6],
                nominal_cell_weight=result[7],
            )

    @staticmethod
    def select_from_name(name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, manufacturer, form_factor, "
                    "link_to_datasheet, anode_chemistry, "
                    "cathode_chemistry, nominal_capacity, "
                    "nominal_cell_weight FROM "
                    "cell_data.cell "
                    "WHERE name=(%s)"
                ),
                [name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return CellRow(
                id=result[0],
                name=name,
                manufacturer=result[1],
                form_factor=result[2],
                link_to_datasheet=result[3],
                anode_chemistry=result[4],
                cathode_chemistry=result[5],
                nominal_capacity=result[6],
                nominal_cell_weight=result[7],
            )
