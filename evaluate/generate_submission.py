import os
import shutil
import time

i = 0
while True:
    i += 1
    time.sleep(10)
    file_name = "signal_plan-userid-2019_01_01_19_20_{}-hangzhou_bc_tyc_1h_10_11_2021.txt".format(3+i)
    shutil.copy(
        "signal_plan_tmp.txt",
        os.path.join("submitted",
                     file_name))
    print("generated file ", file_name)


