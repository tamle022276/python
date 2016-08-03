#!/bin/bash
python pre_test.py --database_name=monopoly --user_name=dbc --user_password=dbc &
python pre_test.py --database_name=hela --user_name=dbc --user_password=dbc
wait
python uda_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python uda_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python uda_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python uda_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python uda_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=monopoly --user_name=dbc --user_password=dbc --ignore_error=3822 &
python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python bteq_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807 &
python tpt_python.py --database_name=hela --user_name=sitq_ldi_pll_user1 --user_password=sitq_ldi_pll_user1 &
wait
python post_test.py --database_name=monopoly --user_name=dbc --user_password=dbc &
python post_test.py --database_name=hela --user_name=dbc --user_password=dbc

