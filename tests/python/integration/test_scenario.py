# -*- coding: utf-8 -*-
from dku_plugin_test_utils import dss_scenario

TEST_PROJECT_KEY = "TESTGLM"


def test_run_model(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="Test_Regression")


def test_run_classification(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="Test_Classification")


def test_run_splines(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="Test_Splines")
