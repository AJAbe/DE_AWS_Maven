import sys
import awswrangler as wr

# this check counts the number of NULL rows in the temp_C column
# if any rows are NULL, the check returns a number > 0
NULL_DQ_CHECK = f"""
SELECT 
    sum(CASE WHEN close_val is null THEN 1 ELSE 0 END) AS res_col
FROM "de_stock_data_dec2024"."de_abe_project_polygon_stocks_dec2024_pq"
;
"""

# run the quality check
df = wr.athena.read_sql_query(sql=NULL_DQ_CHECK, database="de_stock_data_dec2024")

# exit if we get a result > 0
# else, the check was successful
if df['res_col'][0] > 0:
    sys.exit('Results returned. Quality check failed.')
else:
    print('Quality check passed.')

