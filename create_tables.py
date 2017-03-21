import sys
import psycopg2
import psycopg2.extras


command = (

    """DROP TABLE IF EXISTS person CASCADE""",
    """DROP TABLE IF EXISTS room CASCADE""",
    """DROP TABLE IF EXISTS requests CASCADE""",
    """DROP TABLE IF EXISTS allocations CASCADE""",

    """CREATE TABLE IF NOT EXISTS person (
        pid VARCHAR(20),
        first_name VARCHAR(10) NOT NULL,
        last_name VARCHAR(10) NOT NULL,
        other_name VARCHAR(10),
        pType VARCHAR(6) DEFAULT 'fellow' CONSTRAINT validate_pType CHECK (pType IN ('staff','fellow')),
        date_of_join VARCHAR(8) NOT NULL DEFAULT to_char(CURRENT_DATE+1, 'DD-MM-YY'),
        date_of_depart VARCHAR(8),
        pStatus BOOLEAN DEFAULT '1' CONSTRAINT validate_pstatus CHECK (pStatus IN ('0', '1')),
        PRIMARY KEY (pid)
    )
    """,

    """CREATE TABLE IF NOT EXISTS room (
        rid SERIAL,
        room_name VARCHAR(10) NOT NULL,
        description VARCHAR(30),
        rType VARCHAR(6) DEFAULT 'office' CONSTRAINT validate_rType CHECK (rType IN ('office','lspace')),
        max_no INT NOT NULL CONSTRAINT can_accomodate CHECK (max_no BETWEEN 1 AND 6),
        allocated INT DEFAULT 0 CONSTRAINT check_allocated CHECK (allocated BETWEEN 0 AND 6),
        rStatus BOOLEAN DEFAULT '1' CONSTRAINT validate_rstatus CHECK (rStatus IN ('0', '1')),
        PRIMARY KEY (rid)
    )
    """,

    """CREATE TABLE IF NOT EXISTS requests (
        reqid SERIAL,
        pid VARCHAR(20) NOT NULL,
        rType VARCHAR(6) NOT NULL CONSTRAINT validate_req_rType CHECK (rType IN ('office','lspace')),
        req_date VARCHAR(8) NOT NULL DEFAULT to_char(CURRENT_DATE, 'DD-MM-YY'),
        CONSTRAINT person_id_fkey FOREIGN KEY (pid) REFERENCES person MATCH SIMPLE ON DELETE NO ACTION,
        PRIMARY KEY (reqid)
    )
    """,

    """CREATE TABLE IF NOT EXISTS allocations (
        reqid INTEGER NOT NULL,
        pid VARCHAR(20) NOT NULL,
        rid INTEGER NOT NULL,
        inDate VARCHAR(8) NOT NULL DEFAULT to_char(CURRENT_DATE + INTERVAL '1 day', 'DD-MM-YY'),
        outDate VARCHAR(8) DEFAULT to_char(CURRENT_DATE + INTERVAL '6 months', 'DD-MM-YY'),

        CONSTRAINT request_id_fkey FOREIGN KEY (reqid) REFERENCES requests MATCH SIMPLE ON DELETE CASCADE,
        CONSTRAINT person_id_2_fkey FOREIGN KEY (pid) REFERENCES person MATCH SIMPLE ON DELETE NO ACTION,
        CONSTRAINT room_id_fkey FOREIGN KEY (reqid) REFERENCES room MATCH SIMPLE ON DELETE NO ACTION,
        CONSTRAINT date_check CHECK (inDate <= outDate),
        UNIQUE (reqid),
        PRIMARY KEY (pid, rid)
    )
    """,

    """CREATE OR REPLACE VIEW fellow AS
        SELECT * FROM person WHERE pType = 'fellow'
    """,

    """CREATE OR REPLACE VIEW staff AS
        SELECT * FROM person WHERE pType = 'staff'
    """,

    """CREATE OR REPLACE VIEW office AS
        SELECT * FROM room WHERE rType = 'office'
    """,

    """CREATE OR REPLACE VIEW lspace AS
        SELECT * FROM room WHERE rType = 'living space'
    """,

    """CREATE OR REPLACE VIEW available_space AS
        SELECT * FROM room WHERE rStatus = '1' AND rType = 'living space'
    """,
    
    """CREATE OR REPLACE VIEW available_office AS
        SELECT * FROM room WHERE rStatus = '1' AND rType = 'living space'
    """,

    """CREATE OR REPLACE FUNCTION update_room_status() 
        RETURNS TRIGGER AS
        $BODY$

            BEGIN
                IF NEW.allocated = OLD.max_no THEN
                    NEW.rstatus = '0';
                END IF;
            END;
        $BODY$
        LANGUAGE 'plpgsql'
    """,

    """CREATE TRIGGER availaility_update
        AFTER UPDATE ON room
        FOR EACH ROW
        EXECUTE PROCEDURE update_room_status()
    """
)

# USE VIEWS TO SELECT STAFF AND FELLOWS & SPACE AND OFFICE

conn = None

try:
    # Create a new database session and returns a connection object
    conn = psycopg2.connect(database='cp1_amity', user='amity', password='amity')
    #cur = conn.cursor()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    for c in command:
        print (c)
        cur.execute(c)
    
    cur.close()
    conn.commit()

except (Exception, psycopg2.DatabaseError) as error:
    if conn:
        conn.rollback()

    print ('Error %s' % error )
    sys.exit(1)

# Release the resources
finally:
    if conn is not None:
        conn.close()