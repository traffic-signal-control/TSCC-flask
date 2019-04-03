dataset_dict = {
            "scenario_1": "hangzhou_bc_tyc_1h_8_9_2231",
            "scenario_2": "hangzhou_kn_hz_1h_7_8_827",
            "scenario_3": "hangzhou_bc_tyc_1h_10_11_2021",
            "scenario_4": "hangzhou_bc_tyc_1h_7_8_1848",
            "scenario_5": "hangzhou_sb_sx_1h_7_8_1671"
        }

scenario_dict = dict([(v, k) for k, v in dataset_dict.items()])


user_result = {}
user_result['user_id'] = None
user_result['username'] = None
user_result['final_result'] = None
user_result['dataset_result'] = dict([(k, None) for k, v in dataset_dict.items()])
