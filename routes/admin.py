import uuid
import calendar
from datetime import datetime, timedelta, date
import functools
from flask import (Blueprint, render_template,
                   session, redirect, request, url_for,
                   abort, flash)
from sqlalchemy.exc import SQLAlchemyError
from linuxlab.db import db
from linuxlab.forms import SigninForm, AdministratorForm, PlayerForm, FlagForm, QuestionForm, \
                            ChoicesForm, StatisticsPeriodForm, ReportPeriodForm
from linuxlab.models import PlayerModel, AdministratorModel, FlagModel, QuestionsModel, \
                            QuestionChoicesModel, ScoreboardModel, AnswersTrackerModel, \
                            AchievementsTrackerModel
from linuxlab.routes.utilities import email_string_checker
from linuxlab.routes.statistics import statistics_all_time_highest, statistics_levels_solved, \
                                        statistics_level_0_stl_count, statistics_level_0_stl_sum, \
                                        statistics_level_stl_count, statistics_level_stl_sum, \
                                        statistics_total_sessions, statistics_session_total_playing_time, \
                                        statistics_total_points, statistics_periodic_highest, \
                                        statistics_quizzes_answered
from linuxlab.routes.reports import reports_total_score, reports_level_0_stl, reports_level_stl_count, \
                                        reports_level_stl_sum, reports_totaL_quiz_score, reports_quizzes_points, \
                                        reports_quizzes_solved
from linuxlab.routes.scoreboard import players_graph, players_rank
from linuxlab.routes.achievements import check_players_rank_achievement

from passlib.hash import pbkdf2_sha256
from collections import namedtuple


pages = Blueprint(
    "admin", __name__, template_folder="templates", static_folder="static"
)

Period = namedtuple("period", ["month_period", "year_period"])

def signin_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None or session.get("role") != "administrator":

            return redirect(url_for('.signin_admin'))
        
        return route(*args, **kwargs)

    return route_wrapper


@pages.route("/admin")
def home_admin():
    username = ""
    if session.get("email"):
        username = session.get("username")
    return render_template("admins/index.html", username=username)


@pages.route("/admin/signin", methods=["GET", "POST"])
def signin_admin():
    if session.get("email") and session.get("role") == "administrator":
        return redirect(url_for(".home_admin"))

    form = SigninForm()

    if form.validate_on_submit():
        admin = ""
        email = form.email.data
        is_email = email_string_checker(email)
        if email:
            if is_email:
                admin = AdministratorModel.query.filter(AdministratorModel.email == form.email.data).first()
            elif not is_email:
                admin = AdministratorModel.query.filter(AdministratorModel.username == form.email.data).first()
        else:
            flash("Please input your email / username", category="danger")
            redirect(url_for(".signin_admin"))

        if admin and pbkdf2_sha256.verify(form.password.data, admin.password):
            session["username"] = admin.username
            session["email"] = admin.email
            session["role"] = admin.role

            return redirect(url_for(".home_admin"))

        flash("Incorrect login credentials", category="danger")

    return render_template("admins/signin.html", form=form)


@pages.route("/signout-admin")
def signout_admin():
    session.clear()
    flash("You've been logged out")
    return redirect(url_for(".signin_admin"))


@pages.route("/admin/statistics-and-scoreboard", methods=["GET", "POST"])
@signin_required
def statistics_and_scoreboard_admin():
    all_time_highest = None
    total_points = 0
    periodic_highest = None
    avg_completion_time = timedelta(hours=0,minutes=0,seconds=0)    
    avg_playing = timedelta(hours=0,minutes=0,seconds=0)   
    levels_solved = None
    quizzes_answered = None
    period = ''
    datasets = None
    players = None

    form = StatisticsPeriodForm()

    # --- ALL TIME  STATISTICS --- #
    # Total players registered
    # TODO : Get a total of all registered players
    total_players = PlayerModel.query.filter_by(delete_time=None).\
        with_entities(PlayerModel.id_player).count()
    
    if total_players:
        # ALl time highest score
        # TODO :  Get the highest score of a player
        # Create a subquery for selecting with the
        # highest score available then get the players
        # table joined with flag submission.
        all_time_highest = statistics_all_time_highest()

        # --- PERIODIC STATISTICS --- #
        scoreboard_periods = ScoreboardModel.query.group_by(ScoreboardModel.period.desc()).\
            with_entities(ScoreboardModel.period).all()
        
        form = StatisticsPeriodForm()
        if scoreboard_periods:
            period_list = []
            for period in scoreboard_periods:
                period_list.append((period.period,period.period.strftime("%B %Y")))

            form = StatisticsPeriodForm(obj=scoreboard_periods)
            form.period.choices = period_list
            
            # Default dropdown selection, latest period
            period_select = period_list[0][0]
            period = period_select.strftime("%B %Y")

            # Get the first date of the month
            period_start = period_select.replace(day=1)
            # Get the last date of the month
            last_date_of_the_month = calendar.monthrange(period_select.year, period_select.month)[1]
            period_end = period_select.replace(day=last_date_of_the_month)

            # Total possible points
            # TODO : Get a total of all flag points
            total_points = statistics_total_points(period_select)


            # Periodic highest score
            # TODO : Get the highest score of a player
            #        based on current period
            periodic_highest = statistics_periodic_highest(period_select)
                
            
            # Average level completion time
            # TODO : Get all submissions of each level
            #        then calculate the average with
            #        all of the players that submited
            #        on each
            # For the first level, compare with time
            # a player has signed in then calculate
            # the rest with submission from previous 
            # levels
            #
            # MUST IMPLEMENT automatic sign out 
            # AFTER NO ACTIVITY IN 24 HOURS, IF
            # THERE'S STILL AN ACTIVITY THEN 
            # REFRESH THE SIGN OUT TIMER / ADD 
            # MORE 24 HOUR LIMIT BEFORE AUTO SIGN OUT
            
            level_0_stl_count = statistics_level_0_stl_count(period_select)
            level_stl_count = statistics_level_stl_count(period_start, period_end)


            if level_0_stl_count and level_stl_count:
                level_stl_sum = statistics_level_stl_sum(period_start, period_end)
                level_0_stl_sum = statistics_level_0_stl_sum(period_select)
                total_time_level_completion = level_0_stl_sum + level_stl_sum
                total_level_submission_completion = level_0_stl_count + level_stl_count
                avg_completion_time = total_time_level_completion / total_level_submission_completion
                
                # Trim the microseconds to three digits only
                avg_completion_time = str(avg_completion_time)[:-3]

            elif level_0_stl_count:
                level_0_stl_sum = statistics_level_0_stl_sum(period_select)
                avg_completion_time = level_0_stl_sum / level_0_stl_count

                # Trim the microseconds to three digits only    
                avg_completion_time = str(avg_completion_time)[:-3]

            # Average playing time
            # TODO : Get and sum all of the playing
            #        sessions and calculate the 
            #        average on all of the players
            total_sessions = statistics_total_sessions(period_select)
            session_total_playing_time = statistics_session_total_playing_time(period_select)

            if session_total_playing_time and total_sessions:
                avg_playing = session_total_playing_time / total_sessions

                # Trim the microseconds to three digits only
                avg_playing = str(avg_playing)[:-3] 


            # Number of levels solved
            # TODO : Get all submissions of each 
            #        level then sum submission on 
            #        each level
            levels_solved = statistics_levels_solved(period_select)

            # Quizzes answered
            # TODO : Get all questions of each
            #        quiz then join with tracked
            #        answers to get the number
            #        of correct and incorrect
            #        answers
            quizzes_answered = statistics_quizzes_answered(period_select)

            # Hints used
            # TODO (OPTIONAL): Get all hint's usage of each
            #        level then sum the usage on
            #        on each level
            
            # Players Graph
            datasets = players_graph(period_select)

            # Players rank table
            # TODO : Get all of the player's scoreboard data
            players = players_rank(period_select)

        if form.validate_on_submit():
            # Total possible points
            period_select = datetime.strptime(form.period.data, "%Y-%m-%d").date()
            # Get the first date of the month
            period_start = period_select.replace(day=1)
            # Get the last date of the month
            last_date_of_the_month = calendar.monthrange(period_select.year, period_select.month)[1]
            period_end = period_select.replace(day=last_date_of_the_month)
            
            total_points = statistics_total_points(period_select)
            
            # Periodic highest score
            periodic_highest = statistics_periodic_highest(period_select)


            # Average level completion time
            level_0_stl_count = statistics_level_0_stl_count(period_select)
            level_stl_count = statistics_level_stl_count(period_start, period_end)

            if level_0_stl_count and level_stl_count:
                level_stl_sum = statistics_level_stl_sum(period_start, period_end)
                level_0_stl_sum = statistics_level_0_stl_sum(period_select)
                total_time_level_completion = level_0_stl_sum + level_stl_sum
                total_level_submission_completion = level_0_stl_count + level_stl_count
                avg_completion_time = total_time_level_completion / total_level_submission_completion
                
                # Trim the microseconds to three digits only
                avg_completion_time = str(avg_completion_time)[:-3]

            elif level_0_stl_count:
                level_0_stl_sum = statistics_level_0_stl_sum(period_select)
                avg_completion_time = level_0_stl_sum / level_0_stl_count
            
                # Trim the microseconds to three digits only    
                avg_completion_time = str(avg_completion_time)[:-3]
            
            # Average playing time
            # TODO : Get and sum all of the playing
            #        sessions and calculate the 
            #        average on all of the players
            total_sessions = statistics_total_sessions(period_select)
            session_total_playing_time = statistics_session_total_playing_time(period_select)

            if session_total_playing_time and total_sessions:
                avg_playing = session_total_playing_time / total_sessions

                # Trim the microseconds to three digits only
                avg_playing = str(avg_playing)[:-3] 

            # Number of levels solved
            # TODO : Get all submissions of each 
            #        level then sum submission on 
            #        each level
            levels_solved = statistics_levels_solved(period_select)

            # Quizzes answered
            quizzes_answered = statistics_quizzes_answered(period_select)

            # Players graph
            datasets = players_graph(period_select)

            # Players rank table
            # TODO : Get all of the player's scoreboard data
            players = players_rank(period_select)
 
            return render_template("admins/statistics_and_scoreboard.html", total_players=total_players,
                                all_time_highest=all_time_highest, 
                                total_points=total_points,
                                periodic_highest=periodic_highest,
                                avg_completion=avg_completion_time,
                                avg_playing=avg_playing,
                                levels_solved=levels_solved,
                                quizzes_answered=quizzes_answered,
                                period=period, 
                                datasets_data=datasets, 
                                players=players,
                                form=form)

    return render_template("admins/statistics_and_scoreboard.html", total_players=total_players,
                            all_time_highest=all_time_highest, 
                            total_points=total_points,
                            periodic_highest=periodic_highest,
                            avg_completion=avg_completion_time,
                            avg_playing=avg_playing, 
                            levels_solved=levels_solved,
                            quizzes_answered=quizzes_answered,
                            period=period, 
                            datasets_data=datasets, 
                            players=players, 
                            form=form)


@pages.get("/admin/game-management")
@signin_required
def game_management():
    return render_template("admins/game_management.html")


@pages.get("/admin/question-management/")
@signin_required
def question_management():

    questions_data = QuestionsModel.query.filter(QuestionsModel.delete_time == None).\
        with_entities(QuestionsModel.id_question, QuestionsModel.quiz, QuestionsModel.question,
                    QuestionsModel.points, QuestionsModel.is_active).all()
    question_list = []

    for data in questions_data:
        question = QuestionsModel(
            id_question=data.id_question,
            quiz=data.quiz.replace("_"," - ").title(),
            question=data.question,
            points=data.points,
            is_active=data.is_active
        )
        question_list.append(question)
    

    return render_template("admins/questions/question_management.html", questions_data=question_list)


@pages.route("/admin/question-management/create/", methods=["GET", "POST"])
@signin_required
def question_create():
    form = QuestionForm()
    
    admin_username = session.get("username")
    admin_data = AdministratorModel.query.filter(AdministratorModel.username == admin_username).first()

    if form.validate_on_submit():
        question = QuestionsModel(
            quiz=form.quiz.data,
            admin_id=admin_data.id_admin,
            question=form.question.data,
            points=form.points.data,
            is_active=form.is_active.data,
            period=f"{form.period.data['year_period']}-{form.period.data['month_period']}-1",
            create_time=datetime.today()
        )
        try:
            db.session.add(question)
            db.session.commit()
            flash("Question created successfully", "success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".question_management"))

    return render_template("admins/questions/question_create.html", form=form)


@pages.route("/admin/question-management/edit/<string:id_question>", methods=["GET", "POST"])
@signin_required
def question_edit(id_question: str):

    question = QuestionsModel.query.filter_by(id_question=id_question).first()

    period = Period(question.period.month, question.period.year)

    form = QuestionForm(
        quiz=question.quiz,
        question=question.question,
        points=question.points,
        is_active=question.is_active,
        period=period
    )

    form.submit.label.text = "Update question"

    choices_data = QuestionChoicesModel.query.filter(QuestionChoicesModel.question_id == id_question, 
                                                     QuestionChoicesModel.delete_time == None).\
        with_entities(QuestionChoicesModel.id_question_choice, QuestionChoicesModel.question_choice,
                    QuestionChoicesModel.is_correct_answer).all()

    if form.validate_on_submit():

        year = form.period.year_period.data
        month = form.period.month_period.data
        period = f"{year}-{month}-1"

        question.quiz=form.quiz.data,
        question.question=form.question.data,
        question.points=form.points.data,
        question.is_active=form.is_active.data,
        question.period=period,
        question.update_time=datetime.today()
        try:
            db.session.commit()
            flash(f"Question ID-{id_question} edited successfully", "success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".question_management"))

    return render_template("admins/questions/question_edit.html", question=question, choices_data=choices_data, form=form)


@pages.route("/admin/question-management/delete/<string:id_question>", methods=["GET", "DELETE"])
@signin_required
def question_delete(id_question: str):
    
    question = QuestionsModel.query.filter_by(id_question=id_question).first()
    choices = QuestionChoicesModel.query.filter_by(question_id=id_question).all()

    for choice in choices:
        choice.delete_time = datetime.today()

    question.delete_time = datetime.today()

    try:
        db.session.commit()
        flash(f"Question ID-{id_question} deleted successfully", "success")
    except SQLAlchemyError:
        abort(500)

    return redirect(url_for(".question_management"))


@pages.route("/admin/question-management/edit/<string:id_question>/choices/create", methods=["GET", "POST"])
@signin_required
def choices_create(id_question: str):
    form = ChoicesForm()

    if form.validate_on_submit():

        choice = QuestionChoicesModel(
            question_id=id_question,
            question_choice=form.question_choice.data,
            is_correct_answer=form.is_correct_answer.data,
            create_time=datetime.today()
        )
        try:
            db.session.add(choice)
            db.session.commit()
            flash("Question choice created successfully", "success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".question_edit", id_question=id_question))

    return render_template("admins/choices/choice_create.html", form=form, id_question=id_question)


@pages.route("/admin/question-management/edit/<string:id_question>/"+
             "choices/edit/<string:id_question_choice>", methods=["GET", "POST"])
@signin_required
def choices_edit(id_question: str, id_question_choice: str):
    choice = QuestionChoicesModel.query.filter_by(id_question_choice=id_question_choice, 
                                                     question_id=id_question).first()

    form = ChoicesForm(obj=choice)
    form.submit.label.text = "Update choice"


    if form.validate_on_submit():
        choice.question_choice=form.question_choice.data,
        choice.is_correct_answer=form.is_correct_answer.data,
        choice.update_time=datetime.today()
        try:
            db.session.commit()
            flash(f"Choice ID-{id_question_choice} edited successfully", "success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".question_edit", id_question=id_question))

    return render_template("admins/choices/choice_edit.html", choice=choice, form=form)


@pages.route("/admin/question-management/edit/<string:id_question>/"+
             "choices/delete/<string:id_question_choice>", methods=["GET", "DELETE"])
@signin_required
def choices_delete(id_question: str, id_question_choice: str):

    choice = QuestionChoicesModel.query.filter_by(id_question_choice=id_question_choice,
                                                  question_id=id_question).first()
    choice.delete_time = datetime.today()
    try:
        db.session.commit()
        flash(f"Choice ID-{id_question_choice} deleted successfully", "success")
    except SQLAlchemyError:
        abort(500)

    return redirect(url_for(".question_edit", id_question=id_question))


@pages.get("/admin/flag-management/")
@signin_required
def flag_management():

    flags_data = FlagModel.query.filter(FlagModel.delete_time == None).\
        with_entities(FlagModel.id_flag, FlagModel.level, FlagModel.task,
                      FlagModel.points, FlagModel.period).all()
    flag_list = []

    for data in flags_data:
        flag = FlagModel(
            id_flag=data.id_flag,
            level=data.level.replace("_"," - ").title(),
            task=data.task,
            points=data.points,
            period=data.period.strftime("%B %Y"),
        )
        flag_list.append(flag)

    return render_template("admins/flags/flag_management.html", flags_data=flag_list)


@pages.route("/admin/reward_rank_achievements/")
@signin_required
def reward_rank_achievements():

    now = date.today()
    period_now = now.replace(day=1)
    # previous_period = period_now - relativedelta(months=1)
    # previous_period = previous_period.replace(day=1)

    check_players_rank_achievement(period_now)

    return redirect(url_for(".flag_management"))


@pages.route("/admin/flag-management/create/", methods=["GET", "POST"])
@signin_required
def flag_create():
    form = FlagForm()
    admin_username = session.get("username")
    admin_data = AdministratorModel.query.filter(AdministratorModel.username == admin_username).first()

    if form.validate_on_submit():
        # TODO : Get admin_id for FlagModel
        flag = FlagModel(
            story=form.story.data,
            task=form.task.data,
            commands_needed=form.commands_needed.data,
            helpful_references=form.helpful_references.data,
            hint=form.hint.data,
            access_port=form.access_port.data,
            flag_string=form.flag_string.data,
            admin_id=admin_data.id_admin,
            level=form.level.data,
            category=form.category.data,
            points=form.points.data,
            bonus_point=form.bonus_point.data,
            number_of_bonus=form.number_of_bonus.data,
            period=f"{form.period.data['year_period']}-{form.period.data['month_period']}-1",
            is_active=form.is_active.data,
            create_time=datetime.today()
        )
        try:
            db.session.add(flag)
            db.session.commit()
            flash("Flag created successfully", "success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".flag_management"))

    return render_template("admins/flags/flag_create.html", form=form)


@pages.route("/admin/flag-management/edit/<string:id_flag>", methods=["GET", "POST"])
@signin_required
def flag_edit(id_flag: str):

    # TODO : find id_flag from flags table
    flag = FlagModel.query.filter_by(id_flag=id_flag).first()

    period = Period(flag.period.month, flag.period.year)

    form = FlagForm(
        story=flag.story,
        task=flag.task,
        commands_needed=flag.commands_needed,
        helpful_references=flag.helpful_references,
        access_port=flag.access_port,
        hint=flag.hint,
        flag_string=flag.flag_string,
        level=flag.level,
        category=flag.category,
        points=flag.points,
        bonus_point=flag.bonus_point,
        number_of_bonus=flag.number_of_bonus,
        period=period,
        is_active=flag.is_active,
    )


    form.submit.label.text = "Update flag"
    
    if form.validate_on_submit():
        flag.story=form.story.data,
        flag.task=form.task.data,
        flag.commands_needed=form.commands_needed.data,
        flag.helpful_references=form.helpful_references.data,
        flag.access_port=form.access_port.data,
        flag.hint=form.hint.data,
        flag.flag_string=form.flag_string.data,
        flag.level=form.level.data,
        flag.category=form.category.data,
        flag.points=form.points.data,
        flag.bonus_point = form.bonus_point.data,
        flag.number_of_bonus = form.number_of_bonus.data,
        flag.period = f"{form.period.data['year_period']}-{form.period.data['month_period']}-1",
        flag.is_active=form.is_active.data,
        flag.update_time = datetime.today()

        try:
            # TODO : update the flag
            db.session.commit()
            flash(f"Flag ID-{id_flag} edited successfully", "success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".flag_management"))

    return render_template("admins/flags/flag_edit.html", flag=flag, form=form)


@pages.route("/admin/flag-management/delete/<string:id_flag>", methods=["GET", "DELETE"])
@signin_required
def flag_delete(id_flag: str):
    
    # TODO : find id_flag from flags table and perform soft delete
    flag = FlagModel.query.filter_by(id_flag=id_flag).first()
    flag.delete_time = datetime.today()
    try:
        db.session.commit()
        flash(f"Flag ID-{id_flag} deleted successfully", "success")
    except SQLAlchemyError:
        abort(500)

    return redirect(url_for(".flag_management"))


@pages.get("/admin/user-management/")
@signin_required
def user_management():

    players_data = PlayerModel.query.filter(PlayerModel.delete_time == None).\
        with_entities(PlayerModel.id_player, PlayerModel.username, PlayerModel.email).all()

    admins_data = AdministratorModel.query.filter(AdministratorModel.delete_time == None).\
        with_entities(AdministratorModel.id_admin, AdministratorModel.username, 
                      AdministratorModel.email).all()

    return render_template("admins/users/user_management.html", players_data=players_data, 
                           admins_data=admins_data)


@pages.route("/admin/user-management/player-report-and-statistics/<string:id_player>", methods=["GET", "POST"])
@signin_required
def player_report_and_statistics(id_player: str):

    report_periods = AnswersTrackerModel.query.join(QuestionsModel, 
                    AnswersTrackerModel.question_id == QuestionsModel.id_question).\
                                                group_by(QuestionsModel.period.desc()).\
                                            with_entities(QuestionsModel.period).all()
    
    statistic_periods = ScoreboardModel.query.group_by(ScoreboardModel.period.desc()).\
                                            with_entities(ScoreboardModel.period).all()
    
    player = PlayerModel.query.filter_by(id_player=id_player).first()
    player_username = player.username

    form = ReportPeriodForm()
    total_score = 0
    total_quiz_score = 0
    avg_completion_time = timedelta(hours=0, minutes=0, seconds=0)
    quizzes_points = None
    quizzes_solved = None
    achievements = None


    if statistic_periods:

        period_list = []
        for period in statistic_periods:
            period_list.append((period.period, period.period.strftime("%B %Y")))

        form.period.choices = period_list

        # Default dropdown selection, latest period
        period_select = period_list[0][0]

        # Get the first date of the month
        period_start = period_select.replace(day=1)
        # Get the last date of the month
        last_date_of_the_month = calendar.monthrange(period_select.year, period_select.month)[1]
        period_end = period_select.replace(day=last_date_of_the_month)

        # Total player's score
        # TODO : Get the player's total score
        
        total_score = reports_total_score(period_select, id_player)
        
        if total_score:

            # Average player's completion time
            # TODO : Get player's first time signin
            # in this period and the last submission
            # time then summed up the time to be
            # compared with the number of 
            # submissions
            level_0_stl = reports_level_0_stl(period_select, id_player)
            level_stl_count = reports_level_stl_count(period_start, period_end, player.id_player)

            if level_0_stl and level_stl_count:
                level_stl_sum = reports_level_stl_sum(period_start, period_end, player.id_player)

                total_time_level_completion = level_0_stl + level_stl_sum
                total_level_submission_completion = 1 + level_stl_count

                avg_completion_time = total_time_level_completion / total_level_submission_completion

                # Trim the microseconds to three digits only
                avg_completion_time = str(avg_completion_time)[:-3]

            elif level_0_stl:
                avg_completion_time = level_0_stl
                avg_completion_time = str(avg_completion_time)[:-3]

        if report_periods:
            # Total player's quiz score
            # TODO : Get the player's total quiz score
            total_quiz_score = reports_totaL_quiz_score(period_select, id_player)
            
            # Achievements Collected
            # TODO (OPTIONAL): Get player's
            # collected achievements 
            achievements = AchievementsTrackerModel.query.filter_by(player_id=player.id_player,
                                                                    period=period_select).all()
            # Quizzes Points
            # TODO : Get player's quizzes
            # points earned
            quizzes_points = reports_quizzes_points(period_select, id_player)

            # Quiz Questions Report
            # TODO : Get player's quiz
            # question answers
            quizzes_solved = reports_quizzes_solved(period_select, id_player)

        if form.validate_on_submit():

            period_select = datetime.strptime(form.period.data, "%Y-%m-%d")

            # Get the first date of the month
            period_start = period_select.replace(day=1)
            # Get the last date of the month
            last_date_of_the_month = calendar.monthrange(period_select.year, period_select.month)[1]
            period_end = period_select.replace(day=last_date_of_the_month)

            # Total player's score
            # TODO : Get the player's total score
            total_score = reports_total_score(period_select, id_player)
            
            # Total player's quiz score
            # TODO : Get the player's total quiz score            
            total_quiz_score = reports_totaL_quiz_score(period_select, id_player)

            # Average player's completion time
            # TODO : Get player's first time signin
            # in this period and the last submission
            # time then summed up the time to be
            # compared with the number of 
            # submissions
            level_0_stl = reports_level_0_stl(period_select, id_player)

            level_stl_count = reports_level_stl_count(period_start, period_end, player.id_player)

            if level_0_stl and level_stl_count:
                level_stl_sum = reports_level_stl_sum(period_start, period_end, player.id_player)

                total_time_level_completion = level_0_stl + level_stl_sum
                total_level_submission_completion = 1 + level_stl_count

                avg_completion_time = total_time_level_completion / total_level_submission_completion

                # Trim the microseconds to three digits only
                avg_completion_time = str(avg_completion_time)[:-3]
            elif level_0_stl:
                avg_completion_time = level_0_stl
                avg_completion_time = str(avg_completion_time)[:-3]
            
            # Achievements Collected
            # TODO (OPTIONAL): Get player's
            # collected achievements 
            achievements = AchievementsTrackerModel.query.filter_by(player_id=player.id_player,
                                                                    period=period_select).all()
            # Quizzes Points
            # TODO : Get player's quizzes
            # points earned
            quizzes_points = reports_quizzes_points(period_select, id_player)

            # Quiz Questions Report
            # TODO : Get player's quiz
            # question answers
            quizzes_solved = reports_quizzes_solved(period_select, id_player)
                
            return render_template("admins/users/player_report_and_statistics.html", 
                            player_username=player_username,
                            total_score=total_score, 
                            total_quiz_score=total_quiz_score, 
                            avg_completion_time=avg_completion_time,
                            quizzes_points=quizzes_points,
                            quizzes_solved=quizzes_solved,
                            achievements=achievements,
                            form=form)

    return render_template("admins/users/player_report_and_statistics.html", 
                           player_username=player_username,
                           total_score=total_score, 
                           total_quiz_score=total_quiz_score, 
                           avg_completion_time=avg_completion_time,
                           quizzes_points=quizzes_points,
                           quizzes_solved=quizzes_solved,
                           achievements=achievements,
                           form=form)


@pages.route("/admin/user-management/administrator/create/", methods=["GET", "POST"])
@signin_required
def administrator_create():
    form = AdministratorForm()

    if form.validate_on_submit():
        # TODO : Get admin_id for FlagModel

        administrator = AdministratorModel(
            id_admin=uuid.uuid4().hex,
            username=form.username.data,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
            role="administrator",
            create_time=datetime.today()
        )
        try:
            db.session.add(administrator)
            db.session.commit()
            flash("Admin created successfully", "admin_msg_success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".user_management"))

    return render_template("admins/users/administrator_create.html", form=form)


@pages.route("/admin/user-management/administrator/edit/<string:id_admin>", methods=["GET", "POST"])
@signin_required
def administrator_edit(id_admin: str):

    admin = AdministratorModel.query.filter_by(id_admin=id_admin).first()

    form = AdministratorForm(obj=admin)
    form.submit.label.text = "Update"
    
    if form.validate_on_submit():
        admin.username = form.username.data
        admin.email = form.email.data
        if form.password.data:
            admin.password = pbkdf2_sha256.hash(form.password.data)
        admin.update_time = datetime.today()

        try:
            # TODO : update the flag
            db.session.commit()
            flash(f"Admin : {admin.username} edited successfully", "admin_msg_success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".user_management"))

    return render_template("admins/users/administrator_edit.html", admin=admin, form=form)


@pages.route("/admin/user-management/admin/delete/<string:id_admin>", methods=["GET", "DELETE"])
@signin_required
def administrator_delete(id_admin: str):
    
    admin = AdministratorModel.query.filter_by(id_admin=id_admin).first()
    admin.delete_time = datetime.today()
    try:
        db.session.commit()
        flash(f"Administrator {admin.username} deleted successfully", "admin_msg_success")
    except SQLAlchemyError:
        abort(500)

    return redirect(url_for(".user_management"))


@pages.route("/admin/user-management/player/create/", methods=["GET", "POST"])
@signin_required
def player_create():
    form = PlayerForm()

    if form.validate_on_submit():
        # TODO : Get admin_id for FlagModel

        player = PlayerModel(
            id_player=uuid.uuid4().hex,
            username=form.username.data,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
            role="player",
            create_time=datetime.today()
        )
        try:
            db.session.add(player)
            db.session.commit()
            flash("Player created successfully", "player_msg_success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".user_management"))

    return render_template("admins/users/player_create.html", form=form)


@pages.route("/admin/user-management/player/edit/<string:id_player>", methods=["GET", "POST"])
@signin_required
def player_edit(id_player: str):

    player = PlayerModel.query.filter_by(id_player=id_player).first()

    form = PlayerForm(obj=player)
    form.submit.label.text = "Update"
    
    if form.validate_on_submit():
        player.username = form.username.data
        player.email = form.email.data
        if form.password.data:
            player.password = pbkdf2_sha256.hash(form.password.data)
        player.update_time = datetime.today()

        try:
            # TODO : update the flag
            db.session.commit()
            flash(f"Player : {player.username} edited successfully", "player_msg_success")
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".user_management"))

    return render_template("admins/users/player_edit.html", player=player, form=form)


@pages.route("/admin/user-management/player/delete/<string:id_player>", methods=["GET", "DELETE"])
@signin_required
def player_delete(id_player: str):
    
    player = PlayerModel.query.filter_by(id_player=id_player).first()
    player.delete_time = datetime.today()
    try:
        db.session.commit()
        flash(f"Player {player.username} deleted successfully", "player_msg_success")
    except SQLAlchemyError:
        abort(500)

    return redirect(url_for(".user_management"))