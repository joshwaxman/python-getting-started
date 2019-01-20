from django import forms

class TrupForm(forms.Form):
    pasuk = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        help_text='Enter pasuk (with trup) here.'
    )

    def clean(self):
        cleaned_data = super(TrupForm, self).clean()
        pasuk = cleaned_data.get('pasuk')
        if not pasuk:
            raise forms.ValidationError('You must enter some pasuk!')
