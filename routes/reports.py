from sqlalchemy import func, between
from linuxlab.models import QuestionsModel, QuestionChoicesModel, ScoreboardModel, \
        Level0SubmissionTimeLengthViewModel, LevelSubmissionTimeLengthViewModel, \
        AnswersTrackerModel

def reports_total_score(period_select, id_player):
  total_score = None
  total_score_data = ScoreboardModel.query.filter_by(period=period_select, 
                                                player_id=id_player).first()
  if total_score_data:
     total_score = int(total_score_data.total_score)

  return total_score


def reports_level_0_stl(period_select, id_player):

  level_0_stl = Level0SubmissionTimeLengthViewModel.query.filter(
    Level0SubmissionTimeLengthViewModel.period == period_select,
    Level0SubmissionTimeLengthViewModel.player_id == id_player).\
    with_entities(
      Level0SubmissionTimeLengthViewModel.submission_time_length
    ).scalar()

  return level_0_stl


def reports_level_stl_count(period_start, period_end, id_player):

  level_stl_count = LevelSubmissionTimeLengthViewModel.query.filter(between(
      LevelSubmissionTimeLengthViewModel.submission_time, period_start, period_end
  ), LevelSubmissionTimeLengthViewModel.player_id == id_player).\
  with_entities(
      func.count(LevelSubmissionTimeLengthViewModel.id_flag_submissions).\
          label("total_submissions")).scalar()
  
  return level_stl_count 


def reports_level_stl_sum(period_start, period_end, id_player):

  level_stl_sum = LevelSubmissionTimeLengthViewModel.query.filter(between(
      LevelSubmissionTimeLengthViewModel.submission_time, period_start, period_end
  ), LevelSubmissionTimeLengthViewModel.player_id == id_player).\
  with_entities(
      func.sec_to_time(
          func.sum(
              func.time_to_sec(LevelSubmissionTimeLengthViewModel.submission_time_length))).\
      label("level_time_submissions")
  ).scalar()

  return level_stl_sum


def reports_totaL_quiz_score(period_select, id_player):
  
  total_quiz_score = None
  total_quiz_score_data = AnswersTrackerModel.query.filter(QuestionsModel.period == period_select,
                                                  AnswersTrackerModel.player_id == id_player,
                                                  AnswersTrackerModel.answered_correct == True).\
  join(QuestionsModel, AnswersTrackerModel.question_id == QuestionsModel.id_question).\
  with_entities(func.sum(QuestionsModel.points).label("total_quiz_score")).scalar()

  if total_quiz_score_data:
     total_quiz_score = int(total_quiz_score_data)
  
  return total_quiz_score


def reports_quizzes_points(period_select, id_player):

  quizzes_points_list = []

  quizzes_points = AnswersTrackerModel.query.filter(QuestionsModel.period == period_select,
                                                    AnswersTrackerModel.player_id == id_player,
                                                    AnswersTrackerModel.answered_correct == True).\
  join(QuestionsModel, AnswersTrackerModel.question_id == QuestionsModel.id_question).\
  with_entities(QuestionsModel.quiz, 
              func.sum(QuestionsModel.points).label("total_points")).\
  group_by(QuestionsModel.quiz).all()
    

  for point in quizzes_points:
      quizzes_points_list.append({"quiz": point.quiz.replace("_"," - ").title(),
                                  "total_points": point.total_points})
    
  return quizzes_points_list


def reports_quizzes_solved(period_select, id_player):

  quizzes_solved = []

  quizzes = AnswersTrackerModel.query.filter(QuestionsModel.period == period_select,
                                             AnswersTrackerModel.player_id == id_player).\
  join(QuestionsModel, AnswersTrackerModel.question_id == QuestionsModel.id_question).\
  join(QuestionChoicesModel, QuestionChoicesModel.question_id == QuestionsModel.id_question). \
  with_entities(QuestionsModel.quiz, QuestionChoicesModel.question_choice).\
  group_by(QuestionsModel.quiz).all()
  
  questions_answered = AnswersTrackerModel.query.filter(QuestionsModel.period == period_select,
                                                        AnswersTrackerModel.player_id == id_player,
                                                        QuestionChoicesModel.is_correct_answer == True).\
  join(QuestionsModel, AnswersTrackerModel.question_id == QuestionsModel.id_question).\
  join(QuestionChoicesModel, AnswersTrackerModel.question_id == QuestionChoicesModel.question_id).\
  with_entities(QuestionsModel.quiz, 
              QuestionsModel.question, 
              AnswersTrackerModel.answered_correct,
              QuestionChoicesModel.question_choice).\
  group_by(QuestionsModel.question).all()

  for quiz in quizzes:

    question_list = []
    for question in questions_answered:    

        if question.quiz == quiz.quiz:
            if question.answered_correct == 1:
                question_list.append({"question": question.question,
                                    "correct_answer": question.question_choice,
                                    "answered_correct": True})
            else:
                question_list.append({"question": question.question,
                                    "correct_answer": question.question_choice,
                                    "answered_correct": False})
    quizzes_solved.append({"quiz": quiz.quiz.replace("_", "-").title(), 
                            "questions": question_list})

  return quizzes_solved