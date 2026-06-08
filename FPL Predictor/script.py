# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import fpl
import aiohttp
import asyncio
from prettytable import PrettyTable
import numpy as np
from fpl import FPL
import streamlit as st
import plotly.express
import pandas as pd
import fpl_data_loader
from fpl_data_loader.load import FplApiDataRaw
from fpl_data_loader.transform  import FplApiDataTransformed

from fpl_data_loader.load  import get_element_summary

#async def dataget():
#    async with aiohttp.ClientSession() as session:
#        fal = FPL(session)
#        players = await fal.get_players()

rawdata = FplApiDataRaw()

players = rawdata.elements_json
fixtures = rawdata.fixtures_json
teams = rawdata.teams_json

#create a set of dataframes for maniplulation
dfp = pd.DataFrame(players)
dff = pd.DataFrame(fixtures)
dft = pd.DataFrame(teams)

#generate static required values
#generate the current gameweek
gw = dff[dff['finished'] == True]['event'].max() + 1

#generate static conditions for calculation, the first is the player position
position_conditions = [
    (dfp['element_type'] == 1),
    (dfp['element_type'] == 2),
    (dfp['element_type'] == 3),
    (dfp['element_type'] == 4)
]
position_scoring_choices = [10,6,5,4]
clean_sheet_scoring_choices = [4,4,1,0]
defcon_scoring_choices = [0,10,12,12]
save_scoring_choices = [1,0,0,0]
conceded_scoring_choices =[-1,-1,0,0]

#append calculations to frames
dfp = dfp.assign(Minute_Points=((dfp['minutes'] / (gw * 30)).clip(upper=2)))
dfp = dfp.assign(Scoring_Points=(np.select(position_conditions,position_scoring_choices,default=0)*dfp['goals_scored'])/gw)
dfp = dfp.assign(Assist_Points=dfp['assists']*3/gw)
dfp = dfp.assign(Clean_Sheet_Points=np.select(position_conditions,clean_sheet_scoring_choices,default=0)*dfp['clean_sheets']/gw)
dfp = dfp.assign(Save_Points=np.select(position_conditions,save_scoring_choices,default=0)*dfp['saves']/gw)
dfp = dfp.assign(Defensive_Contribution_Points=dfp['clearances_blocks_interceptions']/(np.select(position_conditions,defcon_scoring_choices)*gw))
dfp = dfp.assign(Penalty_Save_Points=dfp['penalties_saved']*5/gw)
dfp = dfp.assign(Penalty_Miss_Points=dfp['penalties_missed']*-2/gw)
dfp = dfp.assign(Bonus_Points=dfp['bonus']/gw)
dfp = dfp.assign(Conceded_Points=dfp['goals_conceded']*np.select(position_conditions,conceded_scoring_choices,default=0)/(2*gw))
dfp = dfp.assign(Red_Card_Points=dfp['red_cards']*-3/gw)
dfp = dfp.assign(Yellow_Card_Points=dfp['yellow_cards']*-2/gw)
dfp = dfp.assign(Own_Goal_Points=dfp['own_goals']*-2/gw)

dfp = dfp.assign(D=dfp['Clean_Sheet_Points']+dfp['Penalty_Save_Points']+dfp['Save_Points']+dfp['Defensive_Contribution_Points']+dfp['Conceded_Points']+dfp['Own_Goal_Points'])
dfp = dfp.assign(N=dfp['Minute_Points']+dfp['Bonus_Points']+dfp['Red_Card_Points']+dfp['Yellow_Card_Points'])
dfp = dfp.assign(A=dfp['Scoring_Points']+dfp['Assist_Points']+dfp['Penalty_Miss_Points'])

dflast5 = dff[gw > dff['event'] > gw-6 ]

dft = dft.assign(OffensiveForm=dfp['bonus'])


#tests to work to
#player form (last 5)
#team data frame
#
#team offensive form
#team defensive form
#team offensive form

#dratios
#
# form+quality
#
#  d percent


#display
stats = dff['stats']
st.title("FPL Super Team")

st.title("Players")
st.dataframe(dfp)
st.title("Fixtures")
st.dataframe(dff)
st.title("Teams")
st.dataframe(dft)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
