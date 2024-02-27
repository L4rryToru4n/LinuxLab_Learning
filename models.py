from linuxlab.db import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.mysql import INTEGER, TEXT, TINYTEXT, \
                                TIMESTAMP, DATE, TINYINT, DATETIME

class RolesUsersModel(db.Model):
    __tablename__ = "roles_users"
    id_roles_players = db.Column(INTEGER(10), primary_key=True)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"))
    role_id = db.Column(db.String(32), db.ForeignKey("roles.id_roles"))


class RoleModel(db.Model, RoleMixin):
    __tablename__ = "roles"
    id_roles = db.Column(INTEGER(10), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


class PlayerModel(db.Model, UserMixin):
    __tablename__ = "players"
    table_id = db.Column(INTEGER(10, unsigned=True), autoincrement="auto")
    id_player = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(DATETIME())
    flag_submissions = db.relationship("FlagSubmissionModel", back_populates="player", lazy="dynamic")
    achievements_tracker = db.relationship("AchievementsTrackerModel", back_populates="player", lazy="dynamic")
    hints_tracker = db.relationship("HintsTrackerModel", back_populates="player", lazy="dynamic")
    answers_tracker = db.relationship("AnswersTrackerModel", back_populates="player", lazy="dynamic")
    scoreboard = db.relationship("ScoreboardModel", back_populates="player", lazy="dynamic")
    sessions = db.relationship("SessionModel", back_populates="player", lazy="dynamic")
    roles_users = db.relationship("RoleModel", secondary="roles_users", backref=db.backref("player", lazy="dynamic"))
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class AdministratorModel(db.Model):
    __tablename__ = "admins"
    table_id = db.Column(INTEGER(10, unsigned=True), autoincrement="auto")
    id_admin = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32))
    flag = db.relationship("FlagModel", back_populates="admin", lazy="dynamic")
    question = db.relationship("QuestionsModel", back_populates="admin", lazy="dynamic")
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class FlagModel(db.Model):
    __tablename__ = "flags"
    id_flag = db.Column(INTEGER(10, unsigned=True), primary_key=True)
    story = db.Column(TEXT())
    task = db.Column(TEXT())
    commands_needed = db.Column(TEXT())
    helpful_references = db.Column(TEXT())
    hint = db.Column(TEXT())
    access_port = db.Column(TEXT())
    flag_string = db.Column(TINYTEXT())
    admin_id = db.Column(db.String(32), db.ForeignKey("admins.id_admin"), nullable=False)
    admin = db.relationship("AdministratorModel", back_populates="flag")
    level = db.Column(db.String(32), nullable=False)
    category = db.Column(db.String(32))
    points = db.Column(INTEGER(10, unsigned=True), nullable=False)
    bonus_point = db.Column(INTEGER(10, unsigned=True))
    number_of_bonus = db.Column(INTEGER(10, unsigned=True))
    period = db.Column(DATE())
    is_active = db.Column(TINYINT(1))
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())
    flag_submissions = db.relationship("FlagSubmissionModel", back_populates="flag", lazy="dynamic")


class QuestionsModel(db.Model):
    __tablename__ = "questions"
    id_question = db.Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement="auto")
    admin_id = db.Column(db.String(32), db.ForeignKey("admins.id_admin"), nullable=False)
    admin = db.relationship("AdministratorModel", back_populates="question")
    quiz = db.Column(db.String(32), nullable=False)
    question = db.Column(TEXT(), nullable=False)
    points = db.Column(INTEGER(10, unsigned=True))
    is_active = db.Column(TINYINT(1))
    period = db.Column(DATE())
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())
    question_choices = db.relationship("QuestionChoicesModel", back_populates="question", lazy="dynamic")
    answers_tracker = db.relationship("AnswersTrackerModel", back_populates="question", lazy="dynamic")


class QuestionChoicesModel(db.Model):
    __tablename__ = "question_choices"
    id_question_choice = db.Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement="auto")
    question_id = db.Column(INTEGER(10), db.ForeignKey("questions.id_question"))
    question = db.relationship("QuestionsModel", back_populates="question_choices")
    question_choice = db.Column(TINYTEXT(), nullable=False)
    is_correct_answer = db.Column(TINYINT())
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class AchievementsTrackerModel(db.Model):
    __tablename__ = "achievements_tracker"
    id_achievements_tracker = db.Column(db.String(32), primary_key=True)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    player = db.relationship("PlayerModel", back_populates="achievements_tracker")
    achievement_name = db.Column(db.String(32), nullable=False)
    description = db.Column(TEXT())
    period = db.Column(DATE())
    collection_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class HintsTrackerModel(db.Model):
    __tablename__ = "hints_tracker"
    id_achievements_tracker = db.Column(db.String(32), primary_key=True)
    achievement_name = db.Column(db.String(32), nullable=False)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    player = db.relationship("PlayerModel", back_populates="hints_tracker")
    period = db.Column(DATE())
    collection_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class AnswersTrackerModel(db.Model):
    __tablename__ = "answers_tracker"
    id_answers_tracker = db.Column(db.String(32), primary_key=True)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    player = db.relationship("PlayerModel", back_populates="answers_tracker")
    question_id = db.Column(INTEGER(10), db.ForeignKey("questions.id_question"), nullable=False)
    question = db.relationship("QuestionsModel", back_populates="answers_tracker")
    answered_correct = db.Column(TINYINT(1))
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class FlagSubmissionModel(db.Model):
    __tablename__ = "flag_submissions"
    id_flag_submissions = db.Column(db.String(32), primary_key=True, autoincrement="auto")
    flag_id = db.Column(db.String(32), db.ForeignKey("flags.id_flag"), nullable=False)
    flag = db.relationship("FlagModel", back_populates="flag_submissions")
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    player = db.relationship("PlayerModel", back_populates="flag_submissions")
    period = db.Column(DATE())
    submission_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class ScoreboardModel(db.Model):
    __tablename__ = "scoreboard"
    id_scoreboard = db.Column(db.String(32), primary_key=True)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    player = db.relationship("PlayerModel", back_populates="scoreboard")
    total_score = db.Column(INTEGER(10, unsigned=True))
    period = db.Column(DATE())
    create_time = db.Column(TIMESTAMP())
    update_time = db.Column(TIMESTAMP())
    delete_time = db.Column(TIMESTAMP())


class SessionModel(db.Model):
    __tablename__ = "sessions"
    id_session = db.Column(db.String(32), primary_key=True)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    player = db.relationship("PlayerModel", back_populates="sessions")
    time_signin = db.Column(TIMESTAMP())
    time_signout = db.Column(TIMESTAMP())
    last_activity = db.Column(TIMESTAMP())
    period = db.Column(DATE())


class PlayersPlayingTimeLengthViewModel(db.Model):
    __tablename__ = "players_playing_time_length"
    id_session = db.Column(db.String(32), primary_key=True)
    player_id = db.Column(db.String(32), db.ForeignKey("players.id_player"), nullable=False)
    playing_time = db.Column(db.DateTime())
    period = db.Column(DATE())

class SubmissionGraphViewModel(db.Model):
    __tablename__ = "submission_graph"
    id_flag_submissions = db.Column(db.String(32), primary_key=True)
    id_player = db.Column(db.String(32))
    username = db.Column(db.String(32))
    points = db.Column(INTEGER(10, unsigned=True))
    submission_time = db.Column(TIMESTAMP())
    period = db.Column(DATE())


class Level0SubmissionTimeLengthViewModel(db.Model):
    __tablename__ = "level_0_submission_time_length"
    id_flag_submissions = db.Column(db.String(32), primary_key=True)
    id_session = db.Column(db.String(32))
    player_id = db.Column(db.String(32))
    level = db.Column(db.String(32))
    submission_time_length = db.Column(db.DateTime())
    submission_time = db.Column(TIMESTAMP())
    period = db.Column(DATE())


class LevelSubmissionTimeLengthViewModel(db.Model):
    __tablename__ = "level_submission_time_length"
    id_flag_submissions = db.Column(db.String(32), primary_key=True)
    player_id = db.Column(db.String(32))
    level = db.Column(db.String(32))
    submission_time_length = db.Column(db.DateTime())
    submission_time = db.Column(TIMESTAMP())
