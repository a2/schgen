#!/usr/bin/env python
import argparse
import simplejson as json
from postgres import pg_sync
import requests
import os
import model
import model_functions

schema = [
    ("Term", "varchar(32)"),
    ("Course", "varchar(32)"),
    ("PrefixName", "varchar(32)"),
    ("DivisionCode", "varchar(32)"),
    ("DivisionName", "varchar(64)"),
    ("CampusCode", "varchar(32)"),
    ("CampusName", "varchar(32)"),
    ("SchoolCode", "varchar(32)"),
    ("SchoolName", "varchar(64)"),
    ("DepartmentCode", "varchar(32)"),
    ("DepartmentName", "varchar(64)"),
    ("SubtermCode", "varchar(32)"),
    ("SubtermName", "varchar(64)"),
    ("CallNumber", "int"),
    ("NumEnrolled", "int"),
    ("MaxSize", "int"),
    ("EnrollmentStatus", "varchar(32)"),
    ("NumFixedUnits", "int"),
    ("MinUnits", "int"),
    ("MaxUnits", "int"),
    ("CourseTitle", "varchar(64)"),
    ("CourseSubtitle", "varchar(64)"),
    ("TypeCode", "varchar(32)"),
    ("TypeName", "varchar(32)"),
    ("Approval", "varchar(32)"),
    ("BulletinFlags", "varchar(32)"),
    ("ClassNotes", "varchar(64)"),
    ("MeetsOn1", "varchar(32)",),
    ("StartTime1", "time"),
    ("EndTime1", "time"),
    ("Building1", "varchar(32)"),
    ("Room1", "varchar(32)"),
    ("MeetsOn2", "varchar(32)"),
    ("StartTime2", "time"),
    ("EndTime2", "time"),
    ("Building2", "varchar(32)"),
    ("Room2", "varchar(32)"),
    ("MeetsOn3", "varchar(32)"),
    ("StartTime3", "time"),
    ("EndTime3", "time"),
    ("Building3", "varchar(32)"),
    ("Room3", "varchar(32)"),
    ("MeetsOn4", "varchar(32)"),
    ("StartTime4", "time"),
    ("EndTime4", "time"),
    ("Building4", "varchar(32)"),
    ("Room4", "varchar(32)"),
    ("MeetsOn5", "varchar(32)"),
    ("StartTime5", "time"),
    ("EndTime5", "time"),
    ("Building5", "varchar(32)"),
    ("Room5", "varchar(32)"),
    ("MeetsOn6", "varchar(32)"),
    ("StartTime6", "time"),
    ("EndTime6", "time"),
    ("Building6", "varchar(32)"),
    ("Room6", "varchar(32)"),
    ("Meets1", "varchar(64)"),
    ("Meets2", "varchar(64)"),
    ("Meets3", "varchar(64)"),
    ("Meets4", "varchar(64)"),
    ("Meets5", "varchar(64)"),
    ("Meets6", "varchar(64)"),
    ("Instructor1PID", "varchar(32)"),
    ("Instructor1Name", "varchar(32)"),
    ("Instructor2PID", "varchar(32)"),
    ("Instructor2Name", "varchar(32)"),
    ("Instructor3PID", "varchar(32)"),
    ("Instructor3Name", "varchar(32)"),
    ("Instructor4PID", "varchar(32)"),
    ("Instructor4Name", "varchar(32)"),
    ("PrefixLongname", "varchar(32)"),
    ("ExamMeetsOn", "varchar(32)"),
    ("ExamStartTime", "time"),
    ("ExamEndTime", "time"),
    ("ExamBuilding", "varchar(32)"),
    ("ExamRoom", "varchar(32)"),
    ("ExamMeet", "varchar(64)"),
    ("ExamDate", "varchar(32)"),
    ("ChargeMsg1", "varchar(32)"),
    ("ChargeAmt1", "varchar(32)"),
    ("ChargeMsg2", "varchar(32)"),
    ("ChargeAmt2", "varchar(32)"),
    ("Description", "text")
]

# these are given to us in a weird format and need to be massaged a little
special_fields = [
    'MeetsOn1',
    'StartTime1',
    'EndTime1',
    'Building1',
    'Room1',
    'MeetsOn2',
    'StartTime2',
    'EndTime2',
    'Building2',
    'Room2',
    'MeetsOn3',
    'StartTime3',
    'EndTime3',
    'Building3',
    'Room3',
    'MeetsOn4',
    'StartTime4',
    'EndTime4',
    'Building4',
    'Room4',
    'MeetsOn5',
    'StartTime5',
    'EndTime5',
    'Building5',
    'Room5',
    'MeetsOn6',
    'StartTime6',
    'EndTime6',
    'Building6',
    'Room6',
    'ExamMeetsOn',
    'ExamStartTime',
    'ExamEndTime',
    'ExamBuilding',
    'ExamRoom',
    'Description'
]
# format for meeting string (ex. "TR     03:00P-05:10PPUP PUPIN LABORA1332")
# these tuples are of the form (field, type, start_char, end_char)
meets_format = [
        ('MeetsOn', 'varchar(32)', 0, 7),
        ('StartTime', 'time', 7, 13),
        ('EndTime', 'time', 14, 20),
        ('Building', 'varchar(32)', 24, 36),
        ('Room', 'varchar(32)', 36, 42)
]

def _special_treatment(course, schema):
    num_meets = 6
    pairs = []
    for i in range(1, 1 + num_meets):
        meets = course['Meets' + str(i)]
        for item in meets_format:
            value = meets[item[2]:item[3]].strip()
            if value:
                pairs.append((item[0] + str(i), _typify(value, item[1])))
            else:
                pairs.append((item[0] + str(i), None))

    for prefix in ['Exam']:
        meets = course[prefix + 'Meet']
        for item in meets_format:
            value = meets[item[2]:item[3]].strip()
            if value:
                pairs.append((prefix + item[0], _typify(value, item[1])))
            else:
                pairs.append((prefix + item[0], None))
    return pairs

def create_table():
    print 'Creating courses table with proper schema...'
    pg = pg_sync()
    db_query = 'CREATE TABLE IF NOT EXISTS courses_t (%s);' % (", ".join(
            ['%s %s' % column for column in schema]))
    cursor = pg.cursor()
    cursor.execute(db_query)
    pg.commit()

def _finish(action):
    def f(cursor):
        print action
    return f

def drop_table():
    print 'Dropping courses table...'
    pg = pg_sync()
    db_query = 'DROP TABLE courses_t;'
    cursor = pg.cursor()
    cursor.execute(db_query)
    pg.commit()

def _typify(value, data_type):
    if data_type.startswith('varchar'):
        return '%s' % value.replace('\'','\\\'')
    if data_type == 'int':
        return str(int(value)) if value else 0
    if data_type == 'time':
        return '%sM' % value # given data is in form '09:00A'
    else:
        return None

def load_data_from_json(json_data):
    pg = pg_sync()
    query_queue = []
    for course in json_data:
        pairs = [(name, _typify(course[name], data_type)) for (name,
                data_type) in schema if name not in special_fields]
        pairs += _special_treatment(course, schema)
        [columns, values] = zip(*pairs)
        db_query = 'INSERT INTO courses_t (%s) VALUES (%s);' % (
                ', '.join(columns), ', '.join(["%s"] * len(values)))
        query_queue.append(values)
        if len(query_queue) == 1000:
            print 'submitting a batch'
            cursor = pg.cursor()
            cursor.executemany(db_query, query_queue)
            pg.commit()
            cursor.close()
            query_queue = []
    if query_queue:
        print 'submitting a batch'
        cursor = pg.cursor()
        cursor.executemany(db_query, query_queue)
        pg.commit()
        cursor.close()
        query_queue = []

def load_data_from_file(dump_file):
    with open(dump_file) as f:
        load_data_from_json(json.load(f))

def load_data_from_cuit():
    url = os.environ.get('COURSES_DATA_JSON_URL')
    r = requests.get(url)
    load_data_from_json(r.json())

def valid_query_arguments():
    return [func for func in dir(model_functions) if not "__" in func]

def get_recognized_arguments(accepted_queries, **kwargs):
    queries = {query: kwargs[query]
        for query in accepted_queries if query in kwargs}
    return queries

def attr_func_wrap(key, value):
    func = getattr(model_functions, key)
    value, fragment = func(value)
    return key, value, fragment

def build_sql_query(arguments):
    # We have a dict of query keys and values and call getattr with the key,
    # which returns a function pointer with the name of "key", which we call, which
    # provides a query fragment that function makes
    
    # slug is a list, each with (key, value, query_fragment)
    slug = [attr_func_wrap(key, value) for key, value in
            arguments.iteritems()]
    query_fragments = [fragment for _, _, fragment in slug]
    modified_arguments = {key: value for key, value, _ in slug}
    sql_query_fragments = {
        "select_body": ", ".join(model.SELECT),
        "table": model.TABLE,
        "query_fragments": " AND ".join(query_fragments),
        "order_by" : model.ORDERBY,
    }

    query = "SELECT %(select_body)s FROM %(table)s WHERE %(query_fragments)s ORDER BY %(order_by)s;" % sql_query_fragments
    
    return query, modified_arguments

def api_response(data, status_code=200, status_txt="OK"):
    return dict(data=data, status_code=status_code, status_txt=status_txt)

def error(status_code, status_txt, data=None):
    return api_response(status_code=status_code, status_txt=status_txt, data=data)

def finish(response):
    if response:
        return api_response(response)
    else:
        return error(status_code=204, status_txt="NO_CONTENT_FOR_REQUEST")

def on_sql_response(cursor):
    response = [model.build_response_dict(row) for row in cursor.fetchall()]
    return finish(response)

def query_database(**kwargs):
    pg = pg_sync()
    recognized_arguments = valid_query_arguments()
    queries = get_recognized_arguments(recognized_arguments, **kwargs)
    if not queries:
        return error(status_code=400, status_txt="MISSING_QUERY_ARGUMENTS")
    query, arguments = build_sql_query(queries)
    cursor = pg.cursor()
    cursor.execute(query, arguments)
    return on_sql_response(cursor)

def main():
    parser = argparse.ArgumentParser(description="""Read a directory of courses
            JSON dump file and writes to Postgres.""")
    parser.add_argument('--create', action='store_true', help="""create the
            courses_t table if it doesn't already exist""")
    parser.add_argument('--drop', action='store_true', help="""drop the
            courses_t table""")
    parser.add_argument('--load', action='store_true', help="""load courses data
            from CUIT""")
    args = parser.parse_args()
    if args.create:
        create_table()
    elif args.drop:
        drop_table()
    elif args.load:
        load_data_from_cuit()

if __name__ == "__main__":
    main()
