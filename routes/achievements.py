import uuid
from datetime import datetime
from flask import abort
from linuxlab.models import FlagModel, ScoreboardModel, FlagSubmissionModel, AchievementsTrackerModel
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from linuxlab.db import db

flag_categorial_achievements = [
  { 
    "category": "basic",
    "name": "Just Baby Steps",
    "description": "Finish all Basic levels"
  },
  {
    "category": "intermediate",
    "name": "The Runner !",
    "description": "Finish all Intermediate levels"
  },
  {
    "category": "advance",
    "name": "I'm The Finalist !",
    "description": "Finish all Advance levels"
  },
]

ranks_achievements = {
  "1":  {
        "name": "Champion #1",
        "description": "Be the first to reach the highest score"
      },
  "2":  {
        "name": "Champion #2",
        "description": "Be the second to reach the highest score"
      },
  "3":  {
        "name": "Champion #3",
        "description": "Be the third to reach the highest score"
      }
}


def eligible_categorial_achievement(player_id, period, category):

  submissions_category = FlagSubmissionModel.query.filter(
  FlagSubmissionModel.player_id == player_id,
  FlagSubmissionModel.period == period,
  FlagModel.category == category).\
  join(FlagModel, FlagSubmissionModel.flag_id == FlagModel.id_flag).\
  with_entities(func.count(FlagSubmissionModel.id_flag_submissions)).scalar()

  flags_category = FlagModel.query.filter(FlagModel.category == category,
                                          FlagModel.period == period,
                                          FlagModel.delete_time == None,
                                          FlagModel.points > 0).\
  with_entities(func.count(FlagModel.id_flag)).scalar()


  if flags_category == submissions_category:
    return True
  
  return False


def check_achievements(player_id, period):

  for achievement in flag_categorial_achievements:
    
    already_achieved = has_achieved(player_id, period, achievement["name"])

    if not already_achieved:
      
      flags = FlagModel.query.filter_by(period=period, 
                                        category=achievement["category"]).all()

      if flags:

        eligible = eligible_categorial_achievement(player_id, period, achievement["category"])
        

        if eligible:
          
          achievement = AchievementsTrackerModel(
            id_achievements_tracker = uuid.uuid4().hex,
            player_id = player_id,
            achievement_name = achievement["name"],
            description = achievement["description"],
            period = period,
            collection_time = datetime.today()
          )
          
          try:
              db.session.add(achievement)
              db.session.commit()
          except SQLAlchemyError:
              abort(500)


def has_achieved(player_id, period, achievement_name):
  achievement_tracker = AchievementsTrackerModel.query.\
  filter_by(player_id=player_id, 
            period=period, 
            achievement_name=achievement_name).first()
  
  return achievement_tracker


def check_players_rank_achievement(period_select):

  not_already_achieved = []

  top_rank_players = ScoreboardModel.query.filter_by(period=period_select).\
    with_entities(ScoreboardModel.player_id).\
    order_by(ScoreboardModel.total_score.desc(), ScoreboardModel.create_time).limit(3)

  for index,player in enumerate(top_rank_players):
    rank_achievement = ranks_achievements[str(index+1)]
    
    already_achieved = has_achieved(player.player_id, period_select, rank_achievement["name"])
    if already_achieved == None:
      not_already_achieved.append({"player_id": top_rank_players[index].player_id, "rank": str(index+1)})


  if not_already_achieved:
    for player in not_already_achieved:
      player_id = player["player_id"]
      rank = player["rank"]
      achievement = AchievementsTrackerModel(
        id_achievements_tracker = uuid.uuid4().hex,
        player_id = player_id,
        achievement_name = ranks_achievements[rank]["name"],
        description = ranks_achievements[rank]["description"],
        period = period_select,
        collection_time = datetime.today()
      )
      
      try:
          db.session.add(achievement)
          db.session.commit()
      except SQLAlchemyError:
          abort(500)