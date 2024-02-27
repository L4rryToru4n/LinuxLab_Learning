from sqlalchemy import func, between
from linuxlab.models import PlayerModel, FlagModel, ScoreboardModel, \
            FlagSubmissionModel, Level0SubmissionTimeLengthViewModel, \
            LevelSubmissionTimeLengthViewModel, PlayersPlayingTimeLengthViewModel, \
            QuestionsModel, AnswersTrackerModel


def statistics_all_time_highest():
    
  all_time_highest = None

  data_subquery = ScoreboardModel.query.with_entities(func.max(ScoreboardModel.total_score)).scalar_subquery()
  all_time_highest_data = ScoreboardModel.query.filter(ScoreboardModel.total_score == data_subquery, 
                                                  PlayerModel.delete_time == None).\
      join(FlagSubmissionModel, ScoreboardModel.player_id == FlagSubmissionModel.player_id).\
      join(PlayerModel, ScoreboardModel.player_id == PlayerModel.id_player).\
      with_entities(ScoreboardModel.total_score, PlayerModel.username, FlagSubmissionModel.submission_time,\
                      PlayerModel.delete_time).\
      order_by(FlagSubmissionModel.submission_time.asc()).first()

  if all_time_highest_data:
      all_time_highest = {"score": all_time_highest_data.total_score, "username": all_time_highest_data.username}

  return all_time_highest


def statistics_total_points(period_select):

  total_points = 0

  total_points_data = FlagModel.query.filter(FlagModel.period == period_select).\
      with_entities(func.sum(FlagModel.points).label("total_points"), 
                  func.sum(FlagModel.bonus_point).label("total_bonus_point")).first()
  if total_points_data.total_points != None and total_points_data.total_bonus_point != None:
      total_points = int(total_points_data.total_points + total_points_data.total_bonus_point)

  return total_points


def statistics_periodic_highest(period_select):

  periodic_highest = None

  data_subquery = ScoreboardModel.query.filter_by(period=period_select).\
      with_entities(func.max(ScoreboardModel.total_score)).scalar_subquery()
  periodic_highest_data = ScoreboardModel.query.filter(ScoreboardModel.total_score == data_subquery,
                                                  ScoreboardModel.period == period_select).\
      join(PlayerModel, ScoreboardModel.player_id == PlayerModel.id_player).\
      with_entities(ScoreboardModel.total_score, PlayerModel.username).\
      order_by(ScoreboardModel.period.asc(), ScoreboardModel.update_time.asc()).first()
  
  if periodic_highest_data:
      periodic_highest = {"score": periodic_highest_data.total_score, "username": periodic_highest_data.username}

  return periodic_highest


def statistics_total_sessions(period_select):
    
  total_sessions = PlayersPlayingTimeLengthViewModel.query.filter(
      PlayersPlayingTimeLengthViewModel.period == period_select, 
      PlayersPlayingTimeLengthViewModel.playing_time != None).with_entities(
          func.count(PlayersPlayingTimeLengthViewModel.playing_time)
      ).scalar()
  
  return total_sessions


def statistics_session_total_playing_time(period_select):

  session_total_playing_time = PlayersPlayingTimeLengthViewModel.query.filter(
      PlayersPlayingTimeLengthViewModel.period == period_select, 
      PlayersPlayingTimeLengthViewModel.playing_time != None).with_entities(
          func.sec_to_time(
              func.sum(
                  func.time_to_sec(PlayersPlayingTimeLengthViewModel.playing_time)))
      ).scalar()

  return session_total_playing_time


def statistics_levels_solved(period_select):
  
  levels_total_submissions = FlagSubmissionModel.query.filter_by(period=period_select).\
      with_entities(FlagModel.level,
                    func.count(FlagSubmissionModel.id_flag_submissions).label("total_submission")).\
      join(FlagModel, FlagSubmissionModel.flag_id == FlagModel.id_flag).\
      group_by(FlagModel.level, FlagSubmissionModel.period).all()

  levels_solved = []
  
  for level in levels_total_submissions:
    levels_solved.append({"level": level.level.replace("_"," - ").title(),
                          "total_submission": level.total_submission})
    
  # levels_solved = [level._asdict() for level in levels_total_submissions]

  return levels_solved


def statistics_quizzes_answered(period_select):

  questions = AnswersTrackerModel.query.filter(QuestionsModel.period == period_select).\
    with_entities(AnswersTrackerModel.question_id, 
                  QuestionsModel.quiz, 
                  QuestionsModel.question,
                  QuestionsModel.period).\
    join(QuestionsModel, AnswersTrackerModel.question_id == QuestionsModel.id_question).\
    group_by(AnswersTrackerModel.question_id).all()

  quizzes_answered = []

  for question in questions:
    quizzes_answered_correct = QuestionsModel.query.filter(QuestionsModel.period == period_select,
                                                           QuestionsModel.id_question == question.question_id,
                                                           AnswersTrackerModel.answered_correct == 1).\
      with_entities(QuestionsModel.id_question, func.count(AnswersTrackerModel.answered_correct).\
                    label("answers_correct")).\
      join(AnswersTrackerModel, QuestionsModel.id_question == AnswersTrackerModel.question_id).first()
    
    quizzes_answered_incorrect = QuestionsModel.query.filter(QuestionsModel.period == period_select,
                                                           QuestionsModel.id_question == question.question_id,
                                                           AnswersTrackerModel.answered_correct == 0).\
      with_entities(QuestionsModel.id_question, func.count(AnswersTrackerModel.answered_correct).\
                    label("answers_incorrect")).\
      join(AnswersTrackerModel, QuestionsModel.id_question == AnswersTrackerModel.question_id).first()

    quizzes_answered.append({"quiz": question.quiz.replace("_"," - ").title(), 
                             "question": question.question, 
                             "answers_correct": quizzes_answered_correct.answers_correct,
                             "answers_incorrect": quizzes_answered_incorrect.answers_incorrect})
  return quizzes_answered


def statistics_level_0_stl_count(period_select):

  level_0_stl_count = Level0SubmissionTimeLengthViewModel.query.filter(
          Level0SubmissionTimeLengthViewModel.period == period_select).\
              with_entities(func.count(Level0SubmissionTimeLengthViewModel.player_id).\
                          label("count_total_level_0")).scalar()

  return level_0_stl_count

def statistics_level_0_stl_sum(period_select):

  level_0_stl_sum = Level0SubmissionTimeLengthViewModel.query.filter(
      Level0SubmissionTimeLengthViewModel.period == period_select).\
          with_entities(func.sec_to_time(
              func.sum(
                  func.time_to_sec(Level0SubmissionTimeLengthViewModel.submission_time_length))).\
                      label("sum_time_total_level_0")).scalar()

  return level_0_stl_sum


def statistics_level_stl_count(period_start, period_end):
    
  level_stl_count = LevelSubmissionTimeLengthViewModel.query.filter(between(
      LevelSubmissionTimeLengthViewModel.submission_time, period_start, period_end
  )).with_entities(func.count(LevelSubmissionTimeLengthViewModel.player_id).\
                      label("count_total_level")).scalar()

  return level_stl_count


def statistics_level_stl_sum(period_start, period_end):

  level_stl_sum = LevelSubmissionTimeLengthViewModel.query.filter(between(
      LevelSubmissionTimeLengthViewModel.submission_time, period_start, period_end
  )).with_entities(func.sec_to_time(
      func.sum(
          func.time_to_sec(LevelSubmissionTimeLengthViewModel.submission_time_length))).\
              label("sum_time_total_level")).scalar()

  return level_stl_sum