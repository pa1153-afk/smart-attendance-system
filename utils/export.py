# utils/export.py
# Purpose : Generates a CSV file from the attendance table.
#           Called by the GET /export route in app.py.
#
# TODO: import csv, io, and the db module
# TODO: implement generate_csv(date_filter=None)
#         - fetches attendance records from db.get_attendance()
#         - writes them to an in-memory StringIO buffer
#         - returns the buffer so Flask can send it as a file download
#
# CSV columns: Student Name, Student ID, Date, Time, Session ID
