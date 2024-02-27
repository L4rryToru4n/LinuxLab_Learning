import random
from linuxlab.models import PlayerModel, SessionModel, \
              ScoreboardModel, SubmissionGraphViewModel \


def players_graph(period_select):

  scoreboards = ScoreboardModel.query.filter(ScoreboardModel.period == period_select).\
          join(PlayerModel, ScoreboardModel.player_id == PlayerModel.id_player).\
              with_entities(PlayerModel.username, ScoreboardModel.player_id).all()

  players_data = []

  for scoreboard in scoreboards:

      submissions_data = []
      total_graph_points = 0
      graph_data = SubmissionGraphViewModel.query.filter_by(id_player=scoreboard.player_id, period=period_select).\
                                                  order_by(SubmissionGraphViewModel.submission_time.asc()).all()

      session_data = SessionModel.query.filter_by(player_id=scoreboard.player_id, period=period_select).\
                                  order_by(SessionModel.time_signin.asc()).first()
      player_entered_time = session_data.time_signin
      player_entered_timestamp = int(round(player_entered_time.timestamp() * 1000))

      submissions_data.append({
          'x': player_entered_timestamp, 'y': 0
      })

      # TODO : Add submission data
      for data in graph_data:
          timestamp = int(round(data.submission_time.timestamp() * 1000))
          total_graph_points = total_graph_points + data.points
          submissions_data.append({
              'x': timestamp, 'y': total_graph_points
          })

      players_data.append({
          "username": scoreboard.username,
          "submission_data": submissions_data
      })

  # TODO : Create a datasets_list and append with data, keys and value
  #        needed for the graph
  datasets = []

  for player in players_data:
      
      randomized_color_red = random.randrange(0, 255)
      randomized_color_green = random.randrange(0, 255)
      randomized_color_blue = random.randrange(0, 255)

      datasets.append({
          'label': player["username"],
          'backgroundColor': f"rgb({randomized_color_red}, {randomized_color_green}, {randomized_color_blue}",
          'borderColor': f"rgb({randomized_color_red}, {randomized_color_green}, {randomized_color_blue})",
          'fill': False,
          'data': player["submission_data"]
      })

  return datasets


def players_rank(period_select):

  scoreboards = ScoreboardModel.query.filter_by(period=period_select).\
          with_entities(ScoreboardModel.player_id, PlayerModel.username,
                      ScoreboardModel.total_score, ScoreboardModel.period).\
          join(PlayerModel, PlayerModel.id_player == ScoreboardModel.player_id).\
          order_by(ScoreboardModel.total_score.desc(), ScoreboardModel.update_time.asc()).all()
  
  return scoreboards