from django import forms

class TrupForm(forms.Form):
    pasuk = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        help_text='Write here your message!'
    )

    def clean(self):
        cleaned_data = super(TrupForm, self).clean()
        pasuk = cleaned_data.get('pasuk')
        if not pasuk:
            raise forms.ValidationError('You have to write something!')
