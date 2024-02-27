import uuid
import functools
import calendar
from datetime import datetime, timezone, date, timedelta
from dateutil.relativedelta import relativedelta
from flask import (Blueprint, render_template, session, redirect,
                    flash, url_for, abort, request, send_file)
from flask_mailman import EmailMessage
from sqlalchemy.exc import SQLAlchemyError
from linuxlab.db import db
from linuxlab.forms import SigninForm, SignupForm, FlagSubmissionForm, ChoiceForm, \
        ReportPeriodForm
from linuxlab.models import PlayerModel, FlagModel, AnswersTrackerModel, \
                                SessionModel, FlagSubmissionModel, QuestionsModel, \
                                QuestionChoicesModel, ScoreboardModel, AchievementsTrackerModel
from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from linuxlab.routes.utilities import email_string_checker, flag_checker, flag_format_strip
from linuxlab.routes.reports import reports_total_score, reports_level_0_stl, reports_level_stl_count, \
                                        reports_level_stl_sum, reports_totaL_quiz_score, reports_quizzes_points, \
                                        reports_quizzes_solved
from linuxlab.routes.scoreboard import players_graph, players_rank
from linuxlab.routes.achievements import check_achievements, check_players_rank_achievement

pages = Blueprint(
    "player", __name__, template_folder="templates", static_folder="static"
)

serializer = URLSafeTimedSerializer("secretserial")

@pages.before_request
def before_request():

    now = datetime.today()
    period_now = date.today().replace(day=1)
    now_aware_dt = now.replace(tzinfo=timezone.utc)
    try:
        check_ranked_achievement()
        last_active = session.get("last_active")
        delta = now_aware_dt - last_active
        role = session.get("role")
        
        if delta.days > 1 and role == "player":
            session['last_active'] = now

            session_id = session.get("session_id")
            session_data = SessionModel.query.filter_by(id_session=session_id)
            session_data.time_signout = now
            session_data.last_activity = now
            session_data.period = period_now

            db.session.commit()
            session.clear()
            return redirect(url_for('.signout'))
    except:
        pass

    try:
        session['last_active'] = now
        session_id = session.get("session_id")
        session_data = SessionModel.query.filter_by(id_session=session_id)
        session_data.last_activity = now
    except:
        pass


def signin_required_player(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None or session.get("role") != "player":

            return redirect(url_for('.signin'))
        
        return route(*args, **kwargs)

    return route_wrapper


@signin_required_player
def check_ranked_achievement():

    now = date.today()
    period_now = now.replace(day=1)

    if now == period_now:

        previous_period = period_now - relativedelta(months=1)
        previous_period = previous_period.replace(day=1)
        flags = FlagModel.query.filter_by(period=previous_period).all()

    if flags:
        try:
            check_players_rank_achievement(previous_period)
        except:
            pass


@pages.route("/")
def home():
    username = ""
    if session.get("email"):
        username = session.get("username")
    return render_template("players/index.html", username=username)


def generate_token(email):

    return serializer.dumps(email, salt="ovkrQAQubUvBOVYf")


@pages.route("/confirm_account/<token>")
def confirm_account(token):
        
    try:
        email = serializer.loads(token, salt="ovkrQAQubUvBOVYf", max_age=3600)

        player = PlayerModel.query.filter_by(email=email).first()
        player.confirmed_at = datetime.today()

        db.session.commit()
        
        flash("Thank you for your account confirmation. You may now sign-in.", "success")

    except SignatureExpired:
        return "<h1>Token is expired !</h1>"
    return redirect(url_for(".signin"))


@pages.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("email"):
        return redirect(url_for(".home"))

    form = SignupForm()

    token = generate_token(form.email.data)

    if form.validate_on_submit():
        player = PlayerModel(
                    id_player=uuid.uuid4().hex,
                    username=form.username.data,
                    email=form.email.data,
                    password=pbkdf2_sha256.hash(form.password.data),
                    role="player",
                    fs_uniquifier=token,
                    create_time=datetime.today(),
                )

        try:
            db.session.add(player)
            db.session.commit()

            link_url = url_for(".confirm_account", token=token, _external=True)

            msg = EmailMessage(
                'Confirm Your Registration',
                'Your Registration is successfull, please confirm' + 
                f'your account by clicking the link below :\n{link_url}',
                'larrydennis.ltoruan@gmail.com',
                [form.email.data],
                headers={'Message-ID': uuid.uuid4().hex},
            )

            msg.send()
            
            flash("User registered successfully, please confirm your account", "success")
        
        except SQLAlchemyError:
            abort(500)

        return redirect(url_for(".signin"))

    return render_template("players/signup.html", form=form)


@pages.route("/signin", methods=["GET", "POST"])
def signin():
    if session.get("email") and session.get("role") == "player":
        return redirect(url_for(".home"))

    form = SigninForm()

    if form.validate_on_submit():
        player = ""
        email = form.email.data
        is_email = email_string_checker(email)

        if email:
            if is_email:
                player = PlayerModel.query.filter(PlayerModel.email == form.email.data, PlayerModel.confirmed_at != None).first()
            elif not is_email:
                player = PlayerModel.query.filter(PlayerModel.username == form.email.data, PlayerModel.confirmed_at != None).first()
        else:
            flash("Please input your email / username", category="danger")
            redirect(url_for(".signin"))

        if player is None:

            flash("Please confirm your account.", category="danger")

        elif player and pbkdf2_sha256.verify(form.password.data, player.password):
            session["username"] = player.username
            session["email"] = player.email
            session["last_active"] = datetime.today()

            session_data = SessionModel(
                id_session=uuid.uuid4().hex,
                player_id=player.id_player,
                time_signin=datetime.today(),
                period=date.today().replace(day=1),
                last_activity=datetime.today()
            )

            session["session_id"] = session_data.id_session
            session["role"] = player.role

            db.session.add(session_data)
            db.session.commit()

            return redirect(url_for(".home"))
        
        else:
            flash("Incorrect login credentials", category="danger")

    return render_template("players/signin.html", form=form)


@pages.route("/signout")
def signout():

    session_id = session.get("session_id")
    session_data = SessionModel.query.filter_by(id_session=session_id).first()
    session_data.time_signout = datetime.today()
    db.session.commit()
    
    session.clear()
    flash("You've been logged out")
    return redirect(url_for(".signin"))


@pages.get("/levels/intro/")
def levels_intro():

    player_username = None

    if session.get("email") and session.get("role") == "player":
        player_username = session.get("username")

    return render_template("players/levels/level_intro.html", player_username=player_username)


@pages.get("/levels/entry/")
def levels_entry():
    period = date.today()
    period = period.replace(day=1)

    level_data = FlagModel.query.filter_by(level="level_entry", period=period, delete_time=None, is_active=True).first()

    if level_data:
        level = FlagModel(
            story=level_data.story,
            task=level_data.task,
            commands_needed=level_data.commands_needed,
            helpful_references=level_data.helpful_references.split(";"),
            access_port=level_data.access_port
        )
    else:
        level = None

    return render_template("players/levels/level_entry.html", level=level)


@pages.route("/levels/<string:level_number>/", methods=["GET", "POST"])
def levels(level_number):

    if int(level_number) > 19 or int(level_number) < 0:
        abort(404)
    
    period = date.today()
    period = period.replace(day=1)

    level_data = FlagModel.query.filter_by(level=f"level_{level_number}", 
                                           period=period,
                                           delete_time=None,
                                           is_active=True).first()
    
    if level_data:
        level = FlagModel(
            story=level_data.story,
            task=level_data.task,
            commands_needed=level_data.commands_needed,
            helpful_references=level_data.helpful_references.split(";"),
            hint=level_data.hint,
            access_port=level_data.access_port
        )
    else:
        level = None

    form = FlagSubmissionForm()

    if form.validate_on_submit():
        email_session = session.get("email")
        if email_session:
            flag_format = form.flag.data
            is_flag = flag_checker(flag_format)
            flag_string = flag_format_strip(flag_format)
            if is_flag:
                # TODO : check the player's flag with db's flag
                flag = FlagModel.query.filter_by(level=f"level_{level_number}",flag_string=flag_string).first()

                if flag:

                    # TODO : check whether the player had submited this flag
                    player = PlayerModel.query.filter_by(email=email_session).first()
                    has_submited = FlagSubmissionModel.query.filter(FlagSubmissionModel.flag_id == flag.id_flag, 
                                                                FlagSubmissionModel.player_id == player.id_player).first()
                    if not has_submited:

                        # TODO : update the information of submission in the submission table
                        # TODO : update the information of score in the scoreboard table
                        submission = FlagSubmissionModel(
                            id_flag_submissions = uuid.uuid4().hex,
                            flag_id = flag.id_flag,
                            player_id = player.id_player,
                            period = flag.period,
                            submission_time = datetime.today()
                        )
                        scoreboard_exists = ScoreboardModel.query.filter_by(player_id=player.id_player, period=flag.period).first()
                        
                        session_id = session.get("session_id")

                        activity = SessionModel.query.filter_by(id_session=session_id).first()

                        if not scoreboard_exists:
                            total_score = flag.points + flag.bonus_point
                            if flag.number_of_bonus > 0:
                                flag.number_of_bonus = flag.number_of_bonus - 1

                            scoreboard = ScoreboardModel(
                                id_scoreboard = uuid.uuid4().hex,
                                player_id = player.id_player,
                                total_score = total_score,
                                period = flag.period,
                                create_time = datetime.today()
                            )
                            activity.last_activity = datetime.today()

                            
                            try:
                                db.session.add(submission)
                                db.session.add(scoreboard)
                                db.session.commit()
                                
                                check_achievements(player.id_player, period)

                                flash("Correct flag !", "success")
                            except SQLAlchemyError:
                                abort(500)
                        
                        else:
                            scoreboard = ScoreboardModel.query.filter_by(id_scoreboard=scoreboard_exists.id_scoreboard).first()
                            scoreboard.total_score = scoreboard.total_score + flag.points
                            scoreboard.update_time = datetime.today()
                            activity.last_activity = datetime.today()

                            try:
                                db.session.add(submission)
                                db.session.commit()
                                check_achievements(player.id_player, period)
                                flash("Correct flag !", "success")
                            except SQLAlchemyError as e:
                                print(f"\n--- ERROR : {e} ---\n")
                                abort(500)

                        return redirect(url_for(".levels", level_number=level_number))
                    else:
                        flash("You've submited this flag.", category="info")
                        redirect(url_for(".levels", level_number=level_number))
                else: 
                    flash("Incorrect flag", category="danger")
                    redirect(url_for(".levels", level_number=level_number))
            else:
                flash("Incorrect flag", category="danger")
                redirect(url_for(".levels", level_number=level_number))
        else:
            return redirect(url_for(".signin"))
        
    return render_template(f"players/levels/level_{level_number}.html", level=level, form=form)


@pages.route("/quiz/<string:quiz_number>/", methods=["GET", "POST"])
def quizzes(quiz_number):

    if int(quiz_number) > 5 or int(quiz_number) < 1:
        abort(404)

    period = date.today()
    period = period.replace(day=1)

    # TODO : Get questions data
    questions = QuestionsModel.query.filter_by(quiz=f"quiz_{quiz_number}", 
                                               is_active=True, 
                                               delete_time=None, 
                                               period=period).all()
    
    if questions :

        form_list = []
        choice_number = 1

        for question in questions:

            # TODO : Get choices provided from question_choices
            choices = QuestionChoicesModel.query.filter_by(question_id=question.id_question, delete_time=None).\
                                                        with_entities(QuestionChoicesModel.id_question_choice,
                                                                    QuestionChoicesModel.question_choice)
            choices_list = []
            choice_form = ChoiceForm()

            for choice in choices:
                choices_list.append((choice.id_question_choice, choice.question_choice))

            choice_form.radio.label=question.question
            choice_form.radio.choices=choices_list
            choice_form.radio.name=f"choice-{choice_number}"
            choice_number = choice_number + 1
            
            form_list.append({"question": question.question, "choice_form": choice_form})
    else:
        form_list = None
        
    # TODO : Record the answers from the db sequentially and check
    # each received answer

    if request.method == "POST":
        email_session = session.get("email")
        if email_session:
            answers = []
            not_answered_exist = False
            for number in range(1 , choice_number):
                answers.append(request.form.get(f"choice-{number}"))

            for answer in answers:
                if not answer:
                    not_answered_exist = True
            
            if not_answered_exist:
                flash("Please choose an answer.", "danger")
                return redirect(url_for(".quizzes", quiz_number=quiz_number))

            already_answered_check = []
            for answer in answers:
                
                player = PlayerModel.query.filter_by(email=email_session).first()

                choice_check = QuestionChoicesModel.query.filter_by(id_question_choice=answer).\
                                join(QuestionsModel, 
                                            QuestionsModel.id_question == QuestionChoicesModel.question_id).\
                                first()
                already_answered = AnswersTrackerModel.query.filter_by(question_id=choice_check.question_id,
                                                                    player_id=player.id_player).first()
                if not already_answered:
                    already_answered_check.append(False)

                    tracker = AnswersTrackerModel(
                        id_answers_tracker = uuid.uuid4().hex,
                        player_id = player.id_player,
                        question_id = choice_check.question_id,
                        answered_correct = choice_check.is_correct_answer,
                        create_time = datetime.today()
                    )
                    
                    session_id = session.get("session_id")

                    activity = SessionModel.query.filter_by(id_session=session_id).first()
                    
                    activity.last_activity = datetime.today()

                    try:
                        db.session.add(tracker)
                        db.session.commit()                    
                    except SQLAlchemyError:
                        abort(500)
                else:
                    already_answered_check.append(True)

            all_checks = True

            for check in already_answered_check:
                if check == False:
                    all_checks = False
                    
            if all_checks == True:       
                flash("You've already completed this quiz.", "info")
                return redirect(url_for(".quizzes", quiz_number=quiz_number))

            flash("Submission complete", "success")
        else:
            return redirect(url_for(".signin"))


    return render_template(f"players/quizzes/quiz_{quiz_number}.html", form=form_list)


@pages.route("/report-and-statistics", methods=["GET", "POST"])
@signin_required_player
def report_and_statistics():

    report_periods = AnswersTrackerModel.query.join(QuestionsModel, 
                    AnswersTrackerModel.question_id == QuestionsModel.id_question).\
                                                group_by(QuestionsModel.period.desc()).\
                                            with_entities(QuestionsModel.period).all()
    statistic_periods = ScoreboardModel.query.group_by(ScoreboardModel.period.desc()).\
                                            with_entities(ScoreboardModel.period).all()
    
    # Get player's data
    email_session = session.get("email")
    player = PlayerModel.query.filter_by(email=email_session).first()
    
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

        form = ReportPeriodForm(obj=report_periods)
        form.period.choices = period_list

        # Default dropdown selection, latest period
        period_select = period_list[0][0]

        period_start = period_select
        last_date_of_the_month = calendar.monthrange(period_select.year, period_select.month)[1]
        period_end = period_select.replace(day=last_date_of_the_month)
        
        # Total player's score
        # TODO : Get the player's total score
        total_score = reports_total_score(period_select, player.id_player)

        # Average player's completion time
        # TODO : Get player's first time signin
        # in this period and the last submission
        # time then summed up the time to be
        # compared with the number of 
        # submissions
        level_0_stl = reports_level_0_stl(period_select, player.id_player)
        
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
            total_quiz_score = reports_totaL_quiz_score(period_select, player.id_player)
            
            # Achievements Collected
            # TODO (OPTIONAL): Get player's
            # collected achievements 
            achievements = AchievementsTrackerModel.query.filter_by(player_id=player.id_player,
                                                                    period=period_select).all()
            # Quizzes Points
            # TODO : Get player's quizzes
            # points earned            
            quizzes_points = reports_quizzes_points(period_select, player.id_player)

            # Quiz Questions Report
            # TODO : Get player's quiz
            # question answers
            quizzes_solved = reports_quizzes_solved(period_select, player.id_player)

        if form.validate_on_submit():

            period_select = datetime.strptime(form.period.data, "%Y-%m-%d")

            period_start = period_select
            period_end = period_select + relativedelta(months=1)

            # Total player's score
            # TODO : Get the player's total score
            total_score = reports_total_score(period_select, player.id_player)
            
            # Total player's quiz score
            # TODO : Get the player's total quiz score            
            total_quiz_score = reports_totaL_quiz_score(period_select, player.id_player)

            # Average player's completion time
            # TODO : Get player's first time signin
            # in this period and the last submission
            # time then summed up the time to be
            # compared with the number of 
            # submissions
            level_0_stl = reports_level_0_stl(period_select, player.id_player)

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
                # Trim the microseconds to three digits only
                avg_completion_time = str(avg_completion_time)[:-3]

            # Achievements Collected
            # TODO (OPTIONAL): Get player's
            # collected achievements 
            achievements = AchievementsTrackerModel.query.filter_by(player_id=player.id_player,
                                                                    period=period_select).all()
            # Quizzes Points
            # TODO : Get player's quizzes
            # points earned
            quizzes_points = reports_quizzes_points(period_select, player.id_player)

            # Quiz Questions Report
            # TODO : Get player's quiz
            # question answers
            quizzes_solved = reports_quizzes_solved(period_select, player.id_player)

            return render_template("players/report_and_statistics.html", total_score=total_score, 
                            total_quiz_score=total_quiz_score, 
                            avg_completion_time=avg_completion_time,
                            quizzes_points=quizzes_points,
                            quizzes_solved=quizzes_solved,
                            achievements=achievements,
                            form=form)

    return render_template("players/report_and_statistics.html", total_score=total_score, 
                           total_quiz_score=total_quiz_score, 
                           avg_completion_time=avg_completion_time,
                           quizzes_points=quizzes_points,
                           quizzes_solved=quizzes_solved,
                           achievements=achievements,
                           form=form)

@pages.get("/scoreboard")
def scoreboard():
    
    players = None
    period = ''
    datasets = None
    player_score = 0
     
    period_select = ScoreboardModel.query.group_by(ScoreboardModel.period.desc()).\
                                    with_entities(ScoreboardModel.period).first()
    player_email = session.get("email")
    player_role = session.get("role")

    if player_email and player_role == "player":

        currently_signedin = PlayerModel.query.filter_by(email=player_email).first()

        player_id = currently_signedin.id_player

        player_scoreboard = ScoreboardModel.query.filter_by(player_id=player_id, period=period_select.period).first()
        
        if player_scoreboard:
            player_score = player_scoreboard.total_score

    if period_select:

        period = period_select.period.strftime("%B %Y")

        # Players graph
        datasets = players_graph(period_select.period)
        
        # TODO : Get all of the player's scoreboard data
        # Players rank
        players = players_rank(period_select.period)

    return render_template("players/scoreboard.html", period=period, datasets_data=datasets, 
                           player_score=player_score, players=players)


@pages.get("/help")
def support():
    return render_template("players/help.html")


@pages.get("/help/ssh-installation")
def ssh_installation():
    return render_template("players/ssh_installation.html")


@pages.get("/help/putty-download")
def putty_download():
    path = "static/programs/putty-0.80-installer.msi"
    return send_file(path, as_attachment=True)