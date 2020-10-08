# import logging
# import sys
#
# from ormy.column import Column, DateColumnType, StringColumnType
# from ormy.csv_database import CsvDatabase
# from ormy.model import Model
#
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
# log = logging.getLogger('app')
# log.setLevel(logging.INFO)
#
#
# def process_args():
#     args = {}
#     args['path_to_database'] = sys.argv[1]
#     return args
#
#
# def type_str(val):
#     return str(type(val).__name__)
#
#
# # TODO: is this needed?
#
#
# # TODO: implement the limit method to truncate the list of data.
# # TODO: implement count
# # TODO: implement sort
# # TODO: do you want to implement OR and AND?
# # TODO: implement join..? need to add carrier and outpatient data.
#
#
# CLM_DATE_FORMAT = '%Y%m%d'
#
#
# class Patient2(Model):
#     columns = [
#         Column('patient_id', StringColumnType(), file_column_name='DESYNPUF_ID'),
#         Column('service_date', DateColumnType(CLM_DATE_FORMAT), file_column_name='CLM_FROM_DT'),
#     ]
#
#
# class InPatient2(Patient2):
#     __csv_file__ = "inpatient.txt"
#     __table_name__ = "inpatient"
#     columns = Patient2.columns.copy()
#     columns.extend([
#         Column('diagnosis_0', StringColumnType(), file_column_name='ADMTNG_ICD9_DGNS_CD', tags=['diagnosis']),
#         Column('diagnosis_1', StringColumnType(), file_column_name='ICD9_DGNS_CD_1', tags=['diagnosis']),
#         Column('diagnosis_2', StringColumnType(), file_column_name='ICD9_DGNS_CD_2', tags=['diagnosis']),
#         Column('diagnosis_3', StringColumnType(), file_column_name='ICD9_DGNS_CD_3', tags=['diagnosis']),
#         Column('diagnosis_4', StringColumnType(), file_column_name='ICD9_DGNS_CD_4', tags=['diagnosis']),
#         Column('diagnosis_5', StringColumnType(), file_column_name='ICD9_DGNS_CD_5', tags=['diagnosis']),
#         Column('diagnosis_6', StringColumnType(), file_column_name='ICD9_DGNS_CD_6', tags=['diagnosis']),
#         Column('diagnosis_7', StringColumnType(), file_column_name='ICD9_DGNS_CD_7', tags=['diagnosis']),
#         Column('diagnosis_8', StringColumnType(), file_column_name='ICD9_DGNS_CD_8', tags=['diagnosis']),
#         Column('diagnosis_9', StringColumnType(), file_column_name='ICD9_DGNS_CD_9', tags=['diagnosis']),
#         Column('diagnosis_10', StringColumnType(), file_column_name='ICD9_DGNS_CD_10', tags=['diagnosis']),
#     ])
#
#     pass
#
#
# DIABETES_DIAGNOSIS_CODE = '250'
#
#
# def diabetes_diagnosis(v):
#     return v.startswith(DIABETES_DIAGNOSIS_CODE)
#
#
# def process():
#     args = process_args()
#
#     database = CsvDatabase(args['path_to_database'])
#     # in_patients = database.query(InPatient2).exec()
#     # in_patients = database.query(InPatient2).where('diagnosis_0').eq('43310').exec() # 25072).exec()
#     # in_patients = database.query(InPatient2).where_tag('diagnosis').eq('43310').exec()
#     # in_patients = database.query(InPatient2).where('diagnosis_1').lt('43310').exec()
#     in_patients = database.query(InPatient2).where('diagnosis_1').lt('43310').gt('3000').exec()
#
#     print("end of program")
#
#
# if __name__ == "__main__":
#     # TODO: add command line flags.
#     process()
