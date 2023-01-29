from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nome de Usuário",
        required=True,
        max_length=100
    )
    password = forms.CharField(
        label="Senha",
        required=True,
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-group"
            }
        )
    )

class SignupForm(forms.Form):
    player_name = forms.CharField(
        label="Seu Nome",
        required=True,
        max_length=200,
    )
    user_mail = forms.EmailField(
        label="Seu E-mail",
        required=True,
        max_length=100,
        widget=forms.EmailInput(
            attrs ={
                "class": "form-control",
                "placeholder": "seu_nome@email.com"
            }
        )
    )
    username = forms.CharField(
        label="Nome de Usuário",
        required=True,
        max_length=50
    )
    password = forms.CharField(
        label="Senha",
        required=True,
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-group"
            }
        )
    )
    password_confirm = forms.CharField(
        label="Confirmar Senha",
        required=True,
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-group"
            }
        )
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if " " in username:
                raise forms.ValidationError("O nome de usuário não pode conter espaços")
            else:
                return username

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("As senhas não combinam")
            else:
                return password_confirm
    