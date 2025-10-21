from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed
from models import User
from email_validator import validate_email, EmailNotValidError

class SignupForm(FlaskForm):
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Crear cuenta")

    def validate_email(self, field):
        try:
            validate_email(field.data)
        except EmailNotValidError:
            raise ValidationError("Correo inválido.")
        if User.get_by_email(field.data):
            raise ValidationError("El email ya está registrado.")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember_me = BooleanField("Recordarme")
    submit = SubmitField("Iniciar sesión")

class ProductForm(FlaskForm):
    title = StringField("Nombre del zapato", validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField("Descripción", validators=[DataRequired(), Length(min=10)])
    price = DecimalField("Precio (en pesos)", validators=[DataRequired(), NumberRange(min=0)])
    size = StringField("Talla", validators=[Length(max=50)])
    image = FileField("Imagen", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Solo imágenes')])
    submit = SubmitField("Guardar")

class EditProductForm(ProductForm):
    submit = SubmitField("Actualizar")
