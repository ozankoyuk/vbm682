#%%
import sys
import os
# improves printing tables on console
from tabulate import tabulate 

all_transitions = {}
all_transition_probabilities = {}
all_tags_dict = {}
all_pos_tags_dict = {}
words_list = []
all_emission_probs = {}
_temp_previous_tag = 'Q0'
most_likely = {}
all_words = {}
all_unique_words = []
initial_probs_list = []

def read_and_fill_everything():
    for file in os.listdir("./Train/"):
        print('Reading file : ', file)
        train_file = open(f"./Train/{file}", 'r')
        for lines in train_file:
            words_list.append([l.lower() for l in lines.split()])
        train_file.close()
        break
        
    # words_list = [ ...,  ["'/'", 'back/rb-hl', 'with/in-hl', 'the/at-hl', 'met/np-hl'], ....]
    for line in words_list:
        _temp_previous_tag = 'Q0'
        tag = ''
        for words in line:
            word = words.split("/")[0]
            tag = words.split("/")[1]

            # hold every tag of the word, so we can find the
            # most likely one
            if word not in most_likely:
                most_likely[word] = {
                    'count': 1,
                    'tags': [tag]
                    }
            else:
                most_likely[word]['count'] += 1
                most_likely[word]['tags'].append(tag)
            
            # store all words for the train data
            if word not in all_words:
                all_words[word] = 1
            else:
                all_words[word] += 1

            # store all unique words to use in Vocabulary.txt
            if word not in all_unique_words:
                all_unique_words.append(word)

            # store all the tags
            if tag in all_tags_dict:
                all_tags_dict[tag] = all_tags_dict[tag] + 1
            else:
                all_tags_dict[tag] = 1

            # find and store the total occurance in the line
            if words in all_emission_probs.keys():
                all_emission_probs[words] += line.count(words)
            else:
                all_emission_probs[words] = line.count(words)

            # check if there is a tag before the current one.
            if _temp_previous_tag == '':
                _temp_previous_tag = tag

            # combine 2 tags with seperator '~'
            # this will generate TransitionProbs.txt
            combined_tags = _temp_previous_tag + '~' + tag
            if combined_tags in all_transitions:
                all_transitions[combined_tags] += 1
            else:
                all_transitions[combined_tags] = 1

            # store POSTags counts/frequency for every tag 
            if _temp_previous_tag in all_pos_tags_dict.keys():
                all_pos_tags_dict[_temp_previous_tag] += 1
            else:
                all_pos_tags_dict[_temp_previous_tag] = 1
            _temp_previous_tag = tag

def write_PosTags_file():
    pos_tags_file = open('PosTags.txt', 'w+')
    pos_tags_tabulate = []
    for _posTag_key in all_pos_tags_dict.keys():
        pos_tags_tabulate.append([
            _posTag_key,
            str(all_pos_tags_dict[_posTag_key])
            ])

    # sort into given order
    pos_tags_tabulate = sorted(
        pos_tags_tabulate,
        key=lambda x:(int(x[1])),
        reverse=True
        )

    print(
        tabulate(
            pos_tags_tabulate,
            headers=['Tag', 'Tag Frekansı']
            ),
        file=pos_tags_file
        )

def write_TransitionProbs_file():
    transition_probability_file = open('TransitionProbs.txt', 'w+')
    transition_probability_tabulate = []
    for _transition_key in all_transitions.keys():
        # split tags with seperator
        _previous_tag = _transition_key.split('~')[0]
        _next_tag = _transition_key.split('~')[1]

        # if previous tag is exists in the POSTags
        if all_pos_tags_dict[_previous_tag] > 0:
            # use laplace smoothing
            # in order to get rid of zero probabilities
            # P(w,c) =  ( count(w,c) + 1 )/( SUM(count(w,c)) + V ) 
            transition_count = all_transitions[_transition_key] + 1
            laplace_divider = all_pos_tags_dict[_previous_tag] + len(all_tags_dict)
            all_transition_probabilities[_transition_key] = transition_count / laplace_divider

            # if this is the first tag, then we add the 'Begin' tag to show it
            if _previous_tag == 'Q0':
                _prob = round(all_transition_probabilities[_transition_key], 9)
                transition_probability_tabulate.append([
                    'Begin', _next_tag, _prob
                ])
                initial_probs_list.append([
                    _next_tag, _prob
                ])
            else:
                # if there is another tag before current one
                _prob = round(all_transition_probabilities[_transition_key], 9)
                transition_probability_tabulate.append([
                    _previous_tag, _next_tag, _prob
                ])
    # sort into given order
    transition_probability_tabulate = sorted(
        transition_probability_tabulate,
        key=lambda x:(x[0],x[1])
        )

    print(
        tabulate(
            transition_probability_tabulate,
            headers=['Tag A', 'Tag B', 'P(Tag_A, Tag_B)']
            ),
        file=transition_probability_file
        )

def write_Vocabulary_file():
    total_word_count = 0
    # find total word count from the data filled while parsing words
    for w, n in all_words.items():
        total_word_count += n

    vocabulary_freq_list = []
    vocabulary_file = open('Vocabulary.txt', 'w+')
    vocabulary_file.write(
        f"Toplam kelime sayısı: {total_word_count}\nTekil kelime sayısı: {len(all_unique_words)}\n\n"
        )

    # find most likely ones
    for word in most_likely.keys():
        # word : { 'tags':[...], 'count':123 }
        tags = most_likely[word]['tags']
        vocabulary_freq_list.append([
            word,
            most_likely[word]['count'],
            max(set(tags), key=tags.count) # find max occurrence in the tags
        ])

    # sort into given order
    vocabulary_freq_list = sorted(
        vocabulary_freq_list,
        key=lambda x:(x[1]),
        reverse=True
        )

    print(
        tabulate(
            vocabulary_freq_list,
            headers=['Kelime', 'Frekans', 'Most Likely Tag']
        ),
        file=vocabulary_file
    )

def write_EmissionProbs_file():
    emission_probability_tabulate = []
    emission_probability_file = open('EmissionProbs.txt', 'w+')
    # all_emission_probs.keys   -> 'word/tag'
    # all_emission_probs.values -> count of the word
    for emission_key in all_emission_probs.keys():
        word = emission_key.split("/")[0]
        tag = emission_key.split("/")[1]

        # if tag is already exists in the tags
        if all_tags_dict[tag] > 0:

            # word count / tag count
            all_emission_probs[emission_key] = all_emission_probs[emission_key] / all_tags_dict[tag]

            _prob = round(all_emission_probs[emission_key], 9)

            emission_probability_tabulate.append([
                tag, word, _prob
            ])
    emission_probability_tabulate = sorted(emission_probability_tabulate, key=lambda x:(x[0],x[1]))
    print(
        tabulate(
            emission_probability_tabulate,
            headers=['Tag', 'Kelime', 'P(Kelime, Tag)']
            ),
        file=emission_probability_file
    )

def write_InitialProbs_file():
    # InitialProbs.txt file will be filled in here
    initial_probability_file = open('InitialProbs.txt', 'w+')

    # initial_probs_list -> [.., ['tag', 'value'], ..]
    _initial_probs_list = sorted(
        initial_probs_list,
        key=lambda x:(x[0]) # order by tag
    )
    print(
        tabulate(
            _initial_probs_list,
            headers=['Tag', 'P(Tag|<s>)']
        ),
        file=initial_probability_file
    )
    # InitialProbs.txt filled


read_and_fill_everything()

write_PosTags_file()

write_TransitionProbs_file()

write_Vocabulary_file()

write_EmissionProbs_file()

write_InitialProbs_file()

# TODO: 3) Test Kümesinin HMM kullanılarak POSTaglerin bulunması ve elde edilen sonuçların kütüğe yazılması.

print('Done')

# """                                                              
#   ___                   _  __                 _    
#  / _ \ ______ _ _ __   | |/ /___  _   _ _   _| | __
# | | | |_  / _` | '_ \  | ' // _ \| | | | | | | |/ /
# | |_| |/ / (_| | | | | | . \ (_) | |_| | |_| |   < 
#  \___//___\__,_|_| |_| |_|\_\___/ \__, |\__,_|_|\_\
#                                   |___/            
#  _   _   ____     ___    ____    _____    ___    _____   _____   _____ 
# | \ | | |___ \   / _ \  |___ \  |___ /   / _ \  |___ /  |___ /  |___  |
# |  \| |   __) | | | | |   __) |   |_ \  | | | |   |_ \    |_ \     / / 
# | |\  |  / __/  | |_| |  / __/   ___) | | |_| |  ___) |  ___) |   / /  
# |_| \_| |_____|  \___/  |_____| |____/   \___/  |____/  |____/   /_/                                           
# """