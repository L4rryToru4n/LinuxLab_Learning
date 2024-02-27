from typing import Any
from flask_wtf import FlaskForm
from wtforms import (IntegerField, StringField, TextAreaField, 
                     SubmitField, PasswordField, SelectField, 
                     DateField, RadioField, BooleanField,
                     FormField)
from wtforms.validators import (Email, EqualTo, Length, 
                                InputRequired, Optional, NumberRange, 
                                DataRequired)


class StringListField(TextAreaField):
  def _value(self):
    if self.data:
      return "\n".join(self.data)
    else:
      return ""
    
  def process_formdata(self, valuelist: list[Any]):
    if valuelist and valuelist[0]:
      self.data = [line.strip() for line in valuelist[0].split("\n")]
    else:
      self.data = []


class SignupForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=32, message="Max username length is 32 characters.")])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, message="Min password length is 8 characters.")]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[InputRequired(), EqualTo("password", message="Passwords don't match.")]
    )
    submit = SubmitField("Sign up")


class SigninForm(FlaskForm):
    email = StringField("Username / Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Sign in")


class AdministratorForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=32, message="Max username length is 32 characters.")])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[Optional(), Length(min=8, message="Min password length is 8 characters.")]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password", message="Passwords don't match.")]
    )
    submit = SubmitField("Create")


class PlayerForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=32, message="Max username length is 32 characters.")])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[Optional(), Length(min=8, message="Min password length is 8 characters.")]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password", message="Passwords don't match.")]
    )
    submit = SubmitField("Create")


class FlagSubmissionForm(FlaskForm):
    
    flag = StringField("Flag :", validators=[InputRequired(message="Please input the correct flag.")],
                       render_kw={"placeholder": "linuxlab{FLAG_STRING}"})
    submit = SubmitField("Submit")


class PeriodForm(FlaskForm):
    
    year_list = []

    year_list.append(("", "-- Select year"))
    for i in range(2023, 2075):
        year_list.append((str(i),str(i)))


    month_list = [("", "-- Select month"),("1","January"), ("2","February"), ("3","March"),
                ("4","April"), ("5","May"), ("6","June"), ("7","July"),
                ("8","August"), ("9","September"), ("10","October"),
                ("11","November"), ("12","December")]

    month_period = SelectField("Month",validators=[InputRequired(message="Please select a month")],choices=month_list)
    year_period = SelectField("Year",validators=[InputRequired(message="Please select a year")],choices=year_list)


class FlagForm(FlaskForm):
    category_list = [("basic", "Basic"), ("intermediate", "Intermediate"), ("advance", "Advance")]
    level_list = list()
    min_level = 0
    max_level = 20

    level_list.append((f"level_entry",f"Level-Entry"))
    for i in range(min_level, max_level):
        level_list.append((f"level_{i}",f"Level-{i}"))
    
    story = TextAreaField("Story")
    task = TextAreaField("Task")
    commands_needed = TextAreaField("Commands needed for solving")
    helpful_references = TextAreaField("Helpful references for playing")
    hint = TextAreaField("Hint")
    access_port = TextAreaField("Access Port")
    flag_string = TextAreaField("Flag String")
    level = SelectField("Level", validators=[DataRequired(message="Please select a level.")], choices=level_list)
    category = SelectField("Category", choices=category_list)
    points = IntegerField("Points", validators=[InputRequired(message="Please add the flag's point"), NumberRange(min=0)],
                         default=1)
    bonus_point = IntegerField("Bonus Point", validators=[InputRequired(message="Please add the bonus point"), NumberRange(min=0)], default=0)
    number_of_bonus = IntegerField("Number of Bonus", validators=[InputRequired(message="Please add the number of bonus"),
                                                                  NumberRange(min=0)], default=0)
    period = FormField(PeriodForm)
    is_active = BooleanField("Active Flag", default=False)
    submit = SubmitField("Create flag")


class QuestionForm(FlaskForm):
    quiz_list = list()
    min_level = 1
    max_level = 6

    for i in range(min_level, max_level):
        quiz_list.append((f"quiz_{i}",f"Quiz-{i}"))

    quiz = SelectField("Quiz", validators=[DataRequired(message="Please select a quiz number")], choices=quiz_list)
    question = TextAreaField("Question", validators=[InputRequired(message="Please add a question")])
    points = IntegerField("Points", 
                          validators=[InputRequired(message="Please add the question's points"), NumberRange(min=0)], 
                          default=1)
    is_active = BooleanField("Active Question", default=False)
    period = FormField(PeriodForm)
    submit = SubmitField("Create question")

    
class ChoicesForm(FlaskForm):
    question_choice = TextAreaField("Choice Answer", validators=[InputRequired(message="Please add a choice answer")])
    is_correct_answer = BooleanField("Correct Answer", default=False)
    submit = SubmitField("Create choice")


class ChoiceForm(FlaskForm):
    radio = RadioField("Radio")
    submit = SubmitField("Check answer")


class StatisticsPeriodForm(FlaskForm):
    period = SelectField("Select Period")
    submit = SubmitField("Apply")


class ReportPeriodForm(FlaskForm):
    period = SelectField("Select Period")
    submit = SubmitField("Apply")