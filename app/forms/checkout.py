
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CheckoutForm(FlaskForm):
    full_name = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=200)])
    phone = StringField('Téléphone', validators=[DataRequired(), Length(min=6, max=20)])
    address = StringField('Adresse', validators=[DataRequired(), Length(min=5, max=500)])
    city = StringField('Ville', validators=[DataRequired(), Length(min=2, max=100)])
    postal_code = StringField('Code postal', validators=[DataRequired(), Length(min=2, max=10)])
    country = StringField('Pays', validators=[DataRequired(), Length(min=2, max=100)])

    shipping_method = SelectField(
        'Mode de livraison',
        choices=[('standard', 'Standard'), ('express', 'Express')],
        default='standard',
        validators=[DataRequired()],
    )
    payment_method = SelectField(
        'Mode de paiement',
        choices=[('card', 'Carte (Stripe)'), ('cash', 'Paiement à la livraison')],
        default='card',
        validators=[DataRequired()],
    )

    submit = SubmitField('Confirmer la commande')

