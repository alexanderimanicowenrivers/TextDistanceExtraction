import spacy
import logging

from spacy.pipeline import EntityRuler
from typing import List, Tuple, Optional

logging.getLogger().setLevel(logging.INFO)
data = [
    "You are 5'7 tall", "5 ft 10 inches", "My brother is 7ft 5", "5foot 10 in",
    "5 foot 9", "5feet 10 is my height", '33mm', '160,5 cm',
    'I did a 12 km run yesterday', '12miles', 'It was 180.5 cm in length',
    '23 metres', 'the island is 12 nautical miles from here'
]
logging.info('Loading measurement words')

#work on for the interview
cm = ['centimetres', 'centimetre', 'centimeter', 'cm']
mm = ['millimetere', 'millimeters', 'millimeter', 'mm']
mile = ['miles', 'mile', 'mi ']
inch = ['inch', 'in', 'inches']
foot = [
    'foot',
    'feet',
    'ft',
]
km = ['kilometers', 'kilometer', 'km']
m = ['metres', 'm ', 'meter']
nm = ['nautical', 'nautical mile', 'nautical miles']
yd = ['yard', 'yd']

#leave for now
fur = ['furlong', 'fur']
leg = ['league', 'lea']
fthm = ['fathom', 'ftm']
acr = ['acre']
sq = ['square', 'sq']
cb = ['cubic']
mim = ['micrometre', 'micrometers']
nanm = ['nanometre', 'nanometers']
measuremenent_words = cm + mm + sq + cb + mile + inch + foot + yd + fur + leg + fthm + acr + nm + mim + nanm
set_cm = set(cm)
set_mm = set(mm)
set_mile = set(mile)
set_inch = set(inch)
set_foot = set(foot)
set_km = set(km)
set_m = set(m)
set_nm = set(nm)
set_yd = set(yd)

assert len(measuremenent_words) == 36

logging.info('Test: measuremenent_words = PASSED')


def create_spacey_extractor():
    """
    :return spacy model which extracts measurements:
    """
    nlp = spacy.load("en_core_web_sm")
    weights_pattern = [{
        "LIKE_NUM": True
    }, {
        "LOWER": {
            "IN": measuremenent_words
        }
    }]
    patterns = [{"label": "QUANTITY", "pattern": weights_pattern}]
    ruler = EntityRuler(nlp, patterns=patterns)
    nlp.add_pipe(ruler, before="ner")

    return nlp


nlp = create_spacey_extractor()
logging.info('Loaded Spacey Extractor')


def add_space_text(sentence: str) -> str:
    """
    :param sentence: str, sentence to clean by adding face in between measurement words and numbers
    :param measuremenent_words: list, of measurement words
    :return: string, with space inserted between measurement words and numbers
    """
    lower_sentence = sentence.lower()

    for measuremenent_word in measuremenent_words:
        if measuremenent_word in lower_sentence:
            split_sentence = lower_sentence.split(measuremenent_word)
            tmp = ''
            for i in range((len(split_sentence) - 1)):
                tmp += split_sentence[i].strip(
                ) + ' ' + measuremenent_word.strip() + ' '
            lower_sentence = tmp + split_sentence[i + 1].strip()
    return lower_sentence


assert add_space_text('5feet 10 is my height') == "5 feet 10 is my height"
logging.info('Test: add_space_text = PASSED')


def extraction(data: List[str]) -> List[List[Tuple[str, str]]]:
    """
    :param data: list, each str is a line of language to be processed.
    :return: list of extracted entities for each sentence.
    """
    data_processed = []  # type: List
    for sentence in data:
        sent = add_space_text(sentence)
        doc = nlp(sent)
        data_processed += [[(ent.text, ent.label_) for ent in doc.ents]]
    return data_processed


assert extraction(data) == [[("5'7", 'CARDINAL')],
                            [('5 ft', 'QUANTITY'), ('10 in', 'QUANTITY')],
                            [('7 ft 5', 'QUANTITY')],
                            [('5 foot', 'QUANTITY'), ('10 in', 'QUANTITY')],
                            [('5 foot', 'QUANTITY'), ('9', 'CARDINAL')],
                            [('5 feet', 'QUANTITY')], [('33 mm', 'QUANTITY')],
                            [('160,5 cm', 'QUANTITY')],
                            [('12 km', 'QUANTITY'), ('yesterday', 'DATE')],
                            [('12 mile', 'QUANTITY')], [('180.5 cm',
                                                         'QUANTITY')],
                            [('23 metres', 'QUANTITY')],
                            [('12 nautical mile', 'QUANTITY')]]

logging.info('Test: extraction = PASSED')


def detailed_mesaurements(data_processed: List[List[Tuple[str, str]]]
                         ) -> List[List[Tuple[str, str]]]:
    """
    :param data_processed: list
    :return: list, adds missing details to measurements such as inches if a number is followed by a quantity in foot.
    """
    new_list = []  # type: List[List[Tuple[str, str]]]
    new_val = [("", "")]  # type: List[Tuple[str, str]]
    for i, quants in enumerate(data_processed):

        if len(quants) == 1:  #can't contain any info to correct measurements
            new_list += [quants]

        else:
            if bool(set_foot & set(quants[0][0].split())
                   ) and not bool(set_inch & set(quants[1][0].split())):
                # if foot is in the str but inches aren't, usually these are always seen together when measuring height etc.
                new_val = [quants[0], (quants[1][0] + ' in', quants[1][1])]
                new_list += [new_val]
            else:
                new_list += [quants]
    return new_list


assert detailed_mesaurements(extraction(data)) == [[("5'7", 'CARDINAL')],
                                                   [('5 ft', 'QUANTITY'),
                                                    ('10 in', 'QUANTITY')],
                                                   [('7 ft 5', 'QUANTITY')],
                                                   [('5 foot', 'QUANTITY'),
                                                    ('10 in', 'QUANTITY')],
                                                   [('5 foot', 'QUANTITY'),
                                                    ('9 in', 'CARDINAL')],
                                                   [('5 feet', 'QUANTITY')],
                                                   [('33 mm', 'QUANTITY')],
                                                   [('160,5 cm', 'QUANTITY')],
                                                   [('12 km', 'QUANTITY'),
                                                    ('yesterday', 'DATE')],
                                                   [('12 mile', 'QUANTITY')],
                                                   [('180.5 cm', 'QUANTITY')],
                                                   [('23 metres', 'QUANTITY')],
                                                   [('12 nautical mile',
                                                     'QUANTITY')]]

logging.info('Test: extraction = PASSED')

# Imperial --> Metric --> CM


def mi_km(unit: float) -> float:
    return (unit * 1.60934)


assert mi_km(1.0) == 1.60934


def ft_m(unit: float) -> float:
    return (unit * 0.3048)


assert ft_m(1.0) == 0.3048


def in_cm(unit: float) -> float:
    return (unit * 2.54)


assert in_cm(1.0) == 2.54


def yard_m(unit: float) -> float:
    return (unit / 0.9144)


assert yard_m(1.0) == (1 / 0.9144)


def nautile_km(unit: float) -> float:
    return (unit * 1.15078)


assert nautile_km(1) == (1.15078)


def mm_cm(unit: float) -> float:
    return (unit / 10.0)


assert mm_cm(1.0) == (1 / 10.0)


def m_cm(unit: float) -> float:
    return (unit * 100)


assert m_cm(1.0) == (100)


def km_cm(unit: float) -> float:
    return m_cm((unit * 1000))


assert km_cm(1.0) == (1000 * 100)


def mi_cm(unit: float) -> float:
    return km_cm(mi_km(unit))


assert mi_cm(1.0) == (160934.0)


def ft_cm(unit: float) -> float:
    return m_cm(ft_m(unit))


assert ft_cm(1.0) == (30.48)


def yard_cm(unit: float) -> float:
    return m_cm(yard_m(unit))


assert yard_cm(1.0) == (109.36132983377078)


def nautile_cm(unit: float) -> float:
    return km_cm(nautile_km(unit))


assert nautile_cm(1.0) == (115078.0)

logging.info('Test: meaurements --> cm = PASSED')


def comma_to_dot(sent: str) -> str:
    return sent.replace(',', '.')


assert comma_to_dot(
    "testing , will , be , this") == 'testing . will . be . this'

logging.info('Test: comma_to_dot = PASSED')


def convert_to_cm(val_string: str) -> float:
    """
    :param val_string: str, measurement
    :return: float, cm measurement
    """
    # replace ' with ft
    if "'" in val_string:
        n1 = len(val_string.split("'"))
        if n1 >= 2:
            val_string = val_string.replace("'", " ft ")

    list_vals = list(val_string.split())
    set_of_measure = set(list_vals[1:])
    val = float(comma_to_dot(list_vals[0]))  #type: float

    if len(list_vals) <= 2:  # one measure

        if bool(set_of_measure & set_nm):
            return nautile_cm(val)

        if bool(set_of_measure & set_km):
            return km_cm(val)

        if bool(set_of_measure & set_mile):
            return mi_cm(val)

        if bool(set_of_measure & set_foot):
            return ft_cm(val)

        if bool(set_of_measure & set_m):
            return m_cm(val)

        if bool(set_of_measure & set_yd):
            return yard_cm(val)

        if bool(set_of_measure & set_inch):
            return in_cm(val)

        if bool(set_of_measure & set_mm):
            return mm_cm(val)

        if bool(set_of_measure & set_cm):
            return (val)

    elif len(list_vals) == 3:

        if bool(set_of_measure & set_nm):
            return nautile_cm(val)

        val_i = float(list_vals[2])

        if bool(set_of_measure & set_foot):
            return ft_cm(val) + in_cm(val_i)

    return 0.0


assert convert_to_cm("5'11") == 180.34
assert convert_to_cm("9 nautical miles ") == 1035701.9999999999

logging.info('Test: convert_to_cm = PASSED')


def normalise_measurements(
        measurements_extracted: List[List[Tuple[str, str]]]) -> List[float]:
    """
    :param measurements_extracted: list, of extracted measurements
    :return: normalised values in cm
    """
    measurements_normalised = []  #type: List
    for inp_list in measurements_extracted:
        cm = 0.0
        for val, ex_typ in inp_list:
            if ex_typ in ['QUANTITY', 'CARDINAL']:
                try:
                    cm += convert_to_cm(val)
                except:
                    cm += 0.0
        measurements_normalised += [cm]

    return measurements_normalised


assert normalise_measurements([
    [('7 ft 5', 'QUANTITY')],
    [('5 foot', 'QUANTITY'), ('10 in', 'QUANTITY')],
    [('5 foot', 'QUANTITY'), ('9 in', 'CARDINAL')],
]) == [226.05999999999997, 177.8, 175.26]

logging.info('Test: normalise_measurements = PASSED')


def clean_failed_extractions(normalised_measurements: List[float]) -> List:
    """
    :param data: list of measurements extracted and normalised to cm
    :return: list of normalised measurements with failed extractions replaced with None. 
    """
    normalised_measurements_new = [
        v if v > 0.0 else "None" for v in normalised_measurements
    ]  #type: List[object]
    return normalised_measurements_new


assert clean_failed_extractions([170.18, 177.8, 0.0,
                                 0.0]) == [170.18, 177.8, "None", "None"]

logging.info('Test: clean_failed_extractions = PASSED')


def extract_normalised_measurements(data: List[str]) -> List[object]:
    """
    :param data:
    :return: list of measurements extracted and normalised to cm
    """
    data_processed = extraction(data)
    measurements_extracted = detailed_mesaurements(data_processed)
    normalised_measurements = normalise_measurements(measurements_extracted)
    return clean_failed_extractions(normalised_measurements)


assert extract_normalised_measurements(data) == [
    170.18, 177.8, 226.05999999999997, 177.8, 175.26, 152.4, 3.3, 160.5,
    1200000.0, 1931208.0000000002, 180.5, 2300.0, 1380935.9999999998
]

logging.info('Loaded Successfully')
