
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6, max=128)])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')


class RegisterForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        'Confirmer le mot de passe',
        validators=[DataRequired(), EqualTo('password', message='Les mots de passe ne correspondent pas.')],
    )
    submit = SubmitField('Créer un compte')

