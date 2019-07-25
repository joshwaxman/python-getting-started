from django import forms

class NeoForm(forms.Form):
    connection_string = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        help_text='Enter Neo4j Bolt connection string here.'
    )

    def clean(self):
        cleaned_data = super(NeoForm, self).clean()
        bolt = cleaned_data.get('connection_string')
        if not bolt:
            raise forms.ValidationError('You must enter some bolt connection string!')
