import sys
import logging
import pymysql
import json
import os

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_proxy_host = os.environ['RDS_PROXY_HOST']
db_name = os.environ['DB_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create the database connection outside of the handler to allow connections to be
# re-used by subsequent function invocations.
try:
    conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit(1)

logger.info("SUCCESS: Connection to RDS for MySQL instance succeeded")

def lambda_handler(event, context):
    """
    This function fetches data from RDS database table
    """
    item_count = 0

    with conn.cursor() as cur:
    sql_query = """SELECT
    e.emp_no,
    e.first_name,
    e.last_name,
    t.title,
    d.dept_name,
    dm.first_name AS manager_first_name,
    dm.last_name AS manager_last_name,
    s.salary
FROM
    employees e
JOIN
    titles t ON e.emp_no = t.emp_no
JOIN
    dept_emp de ON e.emp_no = de.emp_no
JOIN
    departments d ON de.dept_no = d.dept_no
LEFT JOIN
    dept_manager dem ON d.dept_no = dem.dept_no
LEFT JOIN
    employees dm ON dem.emp_no = dm.emp_no
JOIN
    salaries s ON e.emp_no = s.emp_no
WHERE
    t.to_date = (SELECT MAX(to_date) FROM titles WHERE emp_no = e.emp_no)
    AND de.to_date = (SELECT MAX(to_date) FROM dept_emp WHERE emp_no = e.emp_no)
    AND s.to_date = (SELECT MAX(to_date) FROM salaries WHERE emp_no = e.emp_no)
    AND (dem.to_date IS NULL OR dem.to_date = (SELECT MAX(to_date) FROM dept_manager WHERE dept_no = d.dept_no))
ORDER BY
    e.hire_date desc
LIMIT 100;"""
        cur.execute(sql_query)
        logger.info("The following items have been fetched from database:")
        response_rows = [] # Use a list to store formatted rows
        for row in cur:
            item_count += 1
            logger.info(row)
            response_rows.append(str(row)) # Convert each row (tuple) to a string
    conn.commit()

    return "Fetched %d items from RDS for MySQL table \n %s" % (item_count, str(response_rows))
