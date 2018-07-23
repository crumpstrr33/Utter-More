from itertools import product, chain
import sys
import re
import os


class UtterMore:

    def __init__(self, *utterance_templates):
        """
        A class to create utterances for a custom skill for Amazon's Alexa. It
        can be a tedious process if verbosity is desired because language is so
        flexible. So this will automatically creates all the utterances you want
        based on (a) given utterance template(s).

        There are two ways to format a template and they are as follows:

        (a|b|c|...) - This place a OR b OR c OR etc. in its place
        {{slot}} - This will place the slot {slot} or nothing in its place.

        For example, the template "What (is|are) (that|those) {{things}}?" will
        return the following utterances:

                    ['What is that {things}?',
                    'What is that ?',
                    'What is those {things}?',
                    'What is those ?',
                    'What are that {things}?',
                    'What are that ?',
                    'What are those {things}?',
                    'What are those ?']

        An arbitrary number of utterance templates can be passed to the class.
        Or utterance templates can be passed as a solo argument to
        self.build_utterances.

        Parameters:
        utterance_templates - Arbitrary number of utterance templates. Their
                              respective utterance can be created by running
                              self.iter_build_utterances which will save them
                              in self.utterances
        """
        self.utterance_templates = list(utterance_templates)
        self.utterances = []

    def iter_build_utterances(self):
        """
        Iteratively runs self.build_utterances for every utterance template
        given in the initialization (in self.utterance_templates) and stores
        the resulting utterances in self.utterances as a two-dimensional list
        where each list element is a list of all the utterances for a single
        template
        """
        for utterance_template in self.utterance_templates:
            self.utterances.append(self.build_utterances(utterance_template))

    @staticmethod
    def build_utterances(utterance_template):
        """
        Returns the made utterances given an utterance template. It supports
        the following substitutions:
        
        (a|b|c|...) - This place a OR b OR c OR etc. in its place
        {{slot}} - This will place the slot {slot} or nothing in its place.

        For example, the template "What (is|are) (that|those) {{things}}?" will
        return the following utterances:

                    ['What is that {things}?',
                    'What is that ?',
                    'What is those {things}?',
                    'What is those ?',
                    'What are that {things}?',
                    'What are that ?',
                    'What are those {things}?',
                    'What are those ?']

        Parameters:
        utterance_template - The template the utterances are created from
        """
        # Find every double bracketed keyword
        double_curlies = re.finditer(r'({{[^{}]*}})', utterance_template)
        # Find every single parenthesis keyword
        or_curlies = re.finditer(r'(\([^()]*\))', utterance_template)
        # Below turns "What (is|are) (that|those) {{things}} {place}?" into:
        #             "What {} {} {} {{place}}?"
        # Finds the above keywords and replaces with {} for formatting
        template = re.sub(r'{{[^{}]*}}|\([^(){}]*\)', '{}', utterance_template)
        # Turns {...} into {{...}} for literalize the curlies
        template = re.sub(r'\{[\w]+\}', lambda x: '{' + x.group(0) + '}', template)

        # Create dictionary mapping where the above occur to the occurance
        all_curlies = chain(double_curlies, or_curlies)
        index_dict = {curly.start(1): curly.group(1) for curly in all_curlies}

        processed_curlies = []
        for ind in sorted(index_dict.keys()):
            curly = index_dict[ind]
            # Double curlies are either single curlies or nothing
            if curly.startswith('{{'):
                processed_curlies.append([curly[1:-1], ''])
            # These are a choice of the words separated by the pip
            elif curly.startswith('('):
                processed_curlies.append(curly[1:-1].split('|'))

        # Fill in the template with every combination, removing excess whitespace
        return [' '.join(template.format(*edit).split()) for edit in product(*processed_curlies)]

    def add_utterance_template(self, utterance_template):
        """
        Adds another utterance template to the current list of them

        Parameters:
        utterance_template - Template to add to current list of templates
        """
        self.utterance_templates.append(utterance_template)

    def save_utterances(self, path, name, ftype, force=False, ftype_or=None):
        """
        Saves the current utterances to a file.

        Parameters:
        path - Path to the directory in which to save the file
        name - Name of the to be saved file
        ftype - File type (txt)
        force - (default False) If True, will automatically make the file. If a
                file of the same name exists, it will overwrite it. If False,
                it will throw an error of the file already exists.
        ftype_or - (default None) File type override; gives the ability to save
                   with a specific file extentsion but the actually writing
                   process is done as a different file type. For example, Alexa
                   needs a CSV that is new line-separated, not comma-separated
                   for some reason so if ftype_or='txt' but ftype='csv', it
                   will save it as a csv file but will write it as a text file.
        """
        # Allows saving with one file extension but as another
        ftype_or = ftype_or or ftype

        # Create full path name
        full_path = os.path.join(path, name + '.' + ftype)

        # Check if file already exists
        if os.path.exists(full_path) and not force:
            raise Exception('File already exists and force=False. ' +
                            'Set force=True to overwrite file.')

        # Open file and add every utterance
        with open(full_path, 'w') as f:
            if ftype_or == 'txt':
                for utterance in chain.from_iterable(self.utterances):
                    f.write('{}\n'.format(utterance.strip()))
            elif ftype_or == 'csv':
                csv_writer = csv.writer(f)
                csv_writer.writerow(chain.from_iterable(self.utterances))

    def save_to_upload_for_alexa(self, path, name, force=False):
        """
        Creates CSV in the format that Alexa needs (instead of comma-separated,
        it's new line-separated otherwise it won't upload correctly).

        Parameters:
        path - Path to the directory in which to save the file
        name - Name of the to be saved file
        force - (default False) If True, will automatically make the file. If a
                file of the same name exists, it will overwrite it. If False,
                it will throw an error of the file already exists.
        """
        self.save_utterances(path, name, 'csv', force=force, ftype_or='txt')


if __name__ == "__main__":
    utter_more = UtterMore(*sys.argv[1:])
    utter_more.add_utterance_template("This (one|guy|dude) (too|also), {thanks}!")
    utter_more.iter_build_utterances()

    utter_more.save_to_upload_for_alexa('', 'tmp', True)

    from pprint import pprint
    pprint(utter_more.utterances)
