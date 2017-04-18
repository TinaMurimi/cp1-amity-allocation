import sys
import psycopg2
import psycopg2.extras


ddl_commands = (

    """DROP TABLE IF EXISTS person CASCADE""",
    """DROP TABLE IF EXISTS room CASCADE""",
    """DROP TABLE IF EXISTS requests CASCADE""",
    """DROP TABLE IF EXISTS allocations CASCADE""",


    """CREATE TABLE IF NOT EXISTS person (
        person_id INTEGER,
        person_name VARCHAR(20) NOT NULL,
        person_gender VARCHAR (1) DEFAULT '' CONSTRAINT validate_person_gender CHECK (person_gender IN ('M','F', '')),
        role VARCHAR(6) CONSTRAINT validate_pType CHECK (role IN ('Staff','Fellow')),
        wants_accommodation VARCHAR(1) DEFAULT 'N' NOT NULL CHECK (wants_accommodation IN ('Y', 'N')),
        PRIMARY KEY (person_id)
    )
    """,

    """CREATE TABLE IF NOT EXISTS room (
        room_id INTEGER,
        room_name VARCHAR(10) NOT NULL,
        room_type VARCHAR(6) DEFAULT 'office' CONSTRAINT validate_room_type CHECK (room_type IN ('office','space')),
        max_no INTEGER NOT NULL CONSTRAINT can_accomodate CHECK (max_no BETWEEN 1 AND 6),
        room_gender VARCHAR (1) DEFAULT '' CONSTRAINT validate_rGender CHECK (room_gender IN ('M','F','')),
        occupancy INTEGER DEFAULT 0 CONSTRAINT check_allocated CHECK (occupancy BETWEEN 0 AND 6),
        PRIMARY KEY (room_id)
    )
    """,

    """CREATE TABLE IF NOT EXISTS allocations (
        person_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        CONSTRAINT person_id_2_fkey FOREIGN KEY (person_id) REFERENCES person MATCH SIMPLE ON DELETE NO ACTION,
        CONSTRAINT room_id_fkey FOREIGN KEY (room_id) REFERENCES room MATCH SIMPLE ON DELETE NO ACTION,
        PRIMARY KEY (person_id, room_id)
    )
    """,

    """CREATE OR REPLACE VIEW fellow AS
        SELECT * FROM person WHERE role = 'fellow'
    """,

    """CREATE OR REPLACE VIEW staff AS
        SELECT * FROM person WHERE role = 'staff'
    """,

    """CREATE OR REPLACE VIEW office AS
        SELECT * FROM room WHERE room_type = 'office'
    """,

    """CREATE OR REPLACE VIEW space AS
        SELECT * FROM room WHERE room_type = 'space'
    """
)

conn = None

try:
    # Create a new database session and returns a connection object
    conn = psycopg2.connect(database='cp1_amity',
                            user='amity', password='amity')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    for command in ddl_commands:
        cur.execute(command)

    cur.close()
    conn.commit()

except (Exception, psycopg2.DatabaseError) as error:
    if conn:
        conn.rollback()

    print ('Error %s' % error)
    sys.exit(1)

# Release the resources
finally:
    if conn is not None:
        conn.close()