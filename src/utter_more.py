from itertools import product, chain
from csv import writer
from sys import argv
from os import path
import re


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
        template = re.sub(r'{{[^{}]*}}|\([^()]*\)', '{}', utterance_template)
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

    def save_utterances(self, path, name, saved_as, force=False, written_as=None):
        """
        Saves the current utterances to a file.

        Parameters:
        path - Path to the directory in which to save the file
        name - Name of the to be saved file
        saved_as - File type, file extension to save as (e.g. 'txt' or 'csv')
        force - (default False) If True, will automatically make the file. If a
                file of the same name exists, it will overwrite it. If False,
                it will throw an error of the file already exists.
        written_as - (default None) What type of file to be written as. If no
                     argument is given, then it will be written as what it is
                     saved as. For example, if we put saved_as='txt' and
                     written_as='csv', then the save file will have a .txt
                     extension but will be written as comma-separated values
                     like a CSV. Amazon's Alexa requires a CSV file but with
                     line separated values, so self.save_for_alexa uses
                     saved_as='csv' and written_as='txt'
        """
        # Allows saving with one file extension but as another
        written_as = written_as or saved_as

        # Create full path name
        full_path = path.join(path, name + '.' + saved_as)

        # Check if file already exists
        if path.exists(full_path) and not force:
            raise Exception('File already exists and force=False. ' +
                            'Set force=True to overwrite file.')
        # Check if unsupported file type
        if saved_as not in ['csv', 'txt']:
            raise Exception("File type '{}' is not supported.".format(ftype_or))

        # Open file and add every utterance
        with open(full_path, 'w') as f:
            if written_as == 'txt':
                for utterance in chain.from_iterable(self.utterances):
                    f.write('{}\n'.format(utterance.strip()))
            elif written_as == 'csv':
                csv_writer = writer(f)
                csv_writer.writerow(chain.from_iterable(self.utterances))

    def save_for_alexa(self, path, name, force=False):
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
        self.save_utterances(path, name, 'csv', force=force, written_as='txt')


if __name__ == "__main__":
    utter_more = UtterMore(*argv[1:])
    utter_more.iter_build_utterances()
    #utter_more.save_for_alexa('', 'tmp', True)

    from pprint import pprint
    pprint(utter_more.utterances)
