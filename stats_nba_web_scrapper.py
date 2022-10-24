#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 11:52:02 2022

@author: rishabhpatni
"""
import json
import nba_api
import requests
from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
import time
import os
import glob

nba_season = '2020-21'
season_type = 'Regular Season'

# Get team ID based on team name
def get_team_id(team):
    for team1 in teams:
        if team1['abbreviation'] == team:
            return team1['teamId']
    return -1

# Get player ID based on player name
def get_player_id(first, last):
    for player in players:
        if player['firstName'] == first and player['lastName'] == last:
            return [player['playerId'], player["teamId"]]
    return -1


class PlayByPlayNBAApiDataset():
    def __init__(self, defender_distance_data, file_path = None):
        self.data= []
        self.len = 0
        data = pd.DataFrame(columns = ["GRID_TYPE", "gameid", "eventnum", "PLAYER_ID",
                                           "PLAYER_NAME", "TEAM_ID", "TEAM_NAME", "PERIOD", "MINUTES_REMAINING",
                                           "SECONDS_REMAINING", "SHOT_ZONE_AREA", "SHOT_ZONE_RANGE", "SHOT_DISTANCE",
                                           "LOC_X", "LOC_Y", "SHOT_ATTEMPTED_FLAG", "SHOT_MADE_FLAG", "GAME_DATE",
                                           "HTM", "VTM"])
        teams = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json').text)
        players = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json').text)
        
        if (file_path == None):
            counter = 0
            for player in players: 
                counter +=1;
                if counter%10 == 0:
                    print(f"{counter} player's shot data has been parsed through.")
                    time.sleep(15)

                if counter%50 == 0:
                    time.sleep(45)
                    print(f"{counter} player's shot data has been parsed through.")

                if (player["teamId"] == 0):
                    continue

                response = shotchartdetail.ShotChartDetail(
                    context_measure_simple = 'FGA',
                    team_id=player["teamId"],
                    player_id=player["playerId"],
                    season_nullable=nba_season,
                    season_type_all_star=season_type).get_data_frames()[0]

        

                
                data = pd.concat([data, response], ignore_index = True)
            data.to_csv('final_values.csv')
        else:
            data = pd.read_csv(file_path)[["GRID_TYPE", "GAME_ID", "GAME_EVENT_ID", "PLAYER_ID",
                                           "PLAYER_NAME", "TEAM_ID", "TEAM_NAME", "PERIOD", "MINUTES_REMAINING",
                                           "SECONDS_REMAINING", "SHOT_ZONE_AREA", "SHOT_ZONE_RANGE", "SHOT_DISTANCE",
                                           "LOC_X", "LOC_Y", "SHOT_ATTEMPTED_FLAG", "SHOT_MADE_FLAG", "GAME_DATE",
                                           "HTM", "VTM"]]
        print(len(data))
        data.columns = ["GRID_TYPE", "gameid", "eventnum", "PLAYER_ID",
                        "PLAYER_NAME", "TEAM_ID", "TEAM_NAME", "PERIOD", "MINUTES_REMAINING",
                        "SECONDS_REMAINING", "SHOT_ZONE_AREA", "SHOT_ZONE_RANGE", "SHOT_DISTANCE",
                        "x", "y", "SHOT_ATTEMPTED_FLAG", "SHOT_MADE_FLAG", "GAME_DATE", "HTM", "VTM"]
        
        
        files = glob.glob(os.path.join(defender_distance_data + "/*.csv"))
        # joining files with concat and read_csv
        defender_distance_data = pd.concat(map(pd.read_csv, files), ignore_index=True)
        defender_distance_data["shot_clock"] = 24 - (defender_distance_data["possession_start_time"] - defender_distance_data["time"])
        defender_distance_data = defender_distance_data[["gameid", "eventnum", "date", "player", 
                                                         "team", "opponent", "period", "time", 
                                                         "x", "y", "dribble_range", 
                                                         "touch_time", "closest_def_dist", "value", "made", 
                                                         "margin", "assisted", "assist_player" ,"shottype", "and1"]]
        
        defender_distance_data["time"] = defender_distance_data["time"].apply(lambda x: time.strftime("%M:%S", time.gmtime(x)))

        data = data.merge(defender_distance_data, on = ["gameid", "eventnum","x", "y"], how='left')
        data = data[["PLAYER_NAME", "TEAM_NAME", "PERIOD", "time", "SHOT_ZONE_AREA", "SHOT_DISTANCE","opponent", "x", "y", "dribble_range", "touch_time", "closest_def_dist", "value", "made", "margin", "shottype"]]
        data = data.dropna()
        players_included = list(data["PLAYER_NAME"].value_counts()[data["PLAYER_NAME"].value_counts() >= 200].index)
        data = data[data.PLAYER_NAME.isin(players_included)]
        data.columns = ["player_name", "team_name", "period", "time", "shot_zone", "shot_distance","opponent", "x", "y", "dribble_range", "touch_time", "closest_def_dist", "value", "made", "margin" ,"shot_type"]
        self.data = data
        self.len = data.shape[0]

        
    def __len__(self):
        return self.len

