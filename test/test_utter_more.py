import filecmp
from inspect import getsourcefile
import os.path as path, sys
cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, path.join(cur_dir[:cur_dir.rfind(path.sep)], 'src'))

import pytest

from utter_more import UtterMore
sys.path.pop(0)


DOUBLE_CURLY = '{{beginning}}{{middle}}{{end}}'
DC_ANS = ['{beginning}{middle}{end}', '{beginning}{middle}', '{beginning}{end}',
          '{beginning}', '{middle}{end}', '{middle}', '{end}', '']

SINGLE_CURLY = '{beginning}{middle}{end}'
SC_ANS = ['{beginning}{middle}{end}']

OR_CURLY = '(be|gin|ning)(mid|dle)(en|d)'
OC_ANS = ['bemiden', 'bemidd', 'bedleen', 'bedled',
          'ginmiden', 'ginmidd', 'gindleen', 'gindled',
          'ningmiden', 'ningmidd', 'ningdleen', 'ningdled']

COND_OR_CURLY = '(be^1|gin^2|ning)(mid*1|dle*2)(en*1|d*2)'
COC_ANS = ['bemiden', 'bemidd', 'bedleen', 'ginmidd', 'gindleen',
           'gindled', 'ningmiden', 'ningmidd', 'ningdleen', 'ningdled']

COND_AND_CURLY = '(be*1|gin*2|ning)(mid^1|dle^2)(en^1|d^2)'
CAC_ANS = ['bemiden', 'gindled']


@pytest.fixture()
def local_um():
    # A fresh and empty UtterMore every time
    um = UtterMore()
    return um
@pytest.fixture(scope='module')
def global_um():
    # Retains the utterances added to it
    um = UtterMore()
    return um


@pytest.mark.parametrize('template, utterances', [
    (DOUBLE_CURLY, DC_ANS),
    (SINGLE_CURLY, SC_ANS),
    (OR_CURLY, OC_ANS),
    (COND_OR_CURLY, COC_ANS),
    (COND_AND_CURLY, CAC_ANS)
])
def test_build_utterances(local_um, template, utterances):
    """
    Test edge case utterance templates
    """
    assert local_um.build_utterances(template) == utterances


def test_ibu_aut(global_um):
    """
    Test methods following UtterMore methods:
        - iter_build_utterances
        - add_utterance_template
    """
    global_um.add_utterance_template(DOUBLE_CURLY)
    global_um.add_utterance_template(SINGLE_CURLY)
    global_um.add_utterance_template(OR_CURLY)
    global_um.iter_build_utterances()
    assert global_um.utterances == [DC_ANS, SC_ANS, OC_ANS]


@pytest.mark.parametrize('fname, saved_as, written_as', [
    ('alexa_test', 'csv', None),
    ('csv_test', 'csv', None),
    ('txt_test', 'txt', None),
    ('file_override_test', 'txt', 'csv')
])
def test_saving_utterances(global_um, tmpdir, fname, saved_as, written_as):
    """
    Test the saving methods of UtterMore
    """
    written_as = written_as or saved_as
    test_dir = path.join(path.dirname(path.realpath(__file__)), 'test_files')

    if fname == 'alexa_test':
        global_um.save_for_alexa(tmpdir, fname)
    else:
        global_um.save_utterances(tmpdir, fname, saved_as, written_as=written_as)

    file_name = fname + '.' + saved_as
    assert filecmp.cmp(path.join(test_dir, file_name),
                       tmpdir.join(file_name))
