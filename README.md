# Utter More
To customize Amazon's Alexa, you make what is called a skill. Do do something in the skill, you make an intent. To run the intent, you make an utterance. When that utterance is uttered, the intent is run. Since language is complex, there may be many different ways to say the same thing and you may want Alexa to pick up on all of those ways. Furthermore, you may have many variables for the utterances (called intent slots). Being verbose enough to cover every case can be tedious, so this takes care of that.

## Creating Utterances
Below are some examples to show its functionality.
### Formatting
There are two options currently:
1) OR statement `(a|b|c|...)` - Used if you want to allow multiple interchangeable words. For example, if `photo`, `picture` and `painting` are interchangeable in your utterances, then write `(photo|picture|painting)` in the place where it would be. The number of words to OR is arbitrary.
2) Optional Intent Slot `{{slot}}` - Used if the existence of an intent slot in your utterance is optional. For example, if you have an optional adverb you may write `I {adverb} love it` or just `I love it`. Instead you can write `I {{adverb}} love it` to capture both.

### Running the Code
Now with the formatting down, lets create some templates for the utterances. Something like:
```
"What is that {{descriptor}} (photo|picture) (of|from)"
```
and
```
"Download the (photo|picture) {{to_file_path}}"
```
To do this, we run the following:
``` python
from utter_more import UtterMore
um = UtterMore('What is that {{descriptor}} (photo|picture) (of|from)',
               'Download the (photo|picture) {{to_file_path}}')
um.iter_build_utterances()

from pprint import pprint
pprint(um.utterances)
```
And this will display:
``` python
[['What is that {descriptor} photo of?',
  'What is that {descriptor} photo from?',
  'What is that {descriptor} picture of?',
  'What is that {descriptor} picture from?',
  'What is that photo of?',
  'What is that photo from?',
  'What is that picture of?',
  'What is that picture from?'],
 ['Download the photo {to_file_path}',
  'Download the photo',
  'Download the picture {to_file_path}',
  'Download the picture']]
```
If we want to save the utterances so that we can upload them to our Alexa skill, we simply do:
``` python
um.save_for_alexa(PATH_TO_DIRECTORY, FILE_NAME)
```
Here we will find the CSV file properly formatted for uploading.

## Uploading the Utterances
1) After going to the tab for the intended intent, click on "Bulk Edit" in the top right corner of the page.

<p align="center">
  <kbd>
    <img width=650px align=center src="https://raw.githubusercontent.com/crumpstrr33/Utter-More/master/pics/intent_ui.png" />
  </kbd>
</p>

2) Browse for or drag and drop the previously made CSV and it will populate the text field.

<p align="center">
  <kbd>
    <img width=400px src="https://raw.githubusercontent.com/crumpstrr33/Utter-More/master/pics/bulk_edit.png" />
  </kbd>
  <kbd>
    <img width=400px src="https://raw.githubusercontent.com/crumpstrr33/Utter-More/master/pics/bulk_edit_filled.png" />
  </kbd>
</p>

3) Press "Submit" and the utterances field will be filled.

<p align="center">
  <kbd>
    <img width=650px src="https://raw.githubusercontent.com/crumpstrr33/Utter-More/master/pics/utterances.png" />
  </kbd>
</p>

And that's it, no need to manually type in potentially hundreds or thousands of annoyingly similar phrases.

## Other Features
* You can add utterance templates after making the class like so:
``` python
from utter_more import UtterMore

um = UtterMore()
um.add_utterance_template("What is that {{descriptor}} (photo|picture) (of|from)")
um.add_utterance_template("Download the (photo|picture) {{to_file_path}}")
um.save_for_alexa(PATH_TO_DIRECTORY, FILE_NAME)
```
This will produce the same CSV as above did
* You can also save it normally as either a regular CSV or a text file like so:
``` python
# Saves as utterances.txt with new line separators
um.save_utterances(PATH_TO_DIRECTORY, 'utterances', 'txt')
# Saves as utterances.csv as actual comma-separated values
um.save_utterances(PATH_TO_DIRECTORY, 'utterances', 'csv')
```
