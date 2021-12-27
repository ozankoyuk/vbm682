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
comparison_for_word_tag = {}

def read_and_fill_everything():
    for file in os.listdir("./Train/"):
        train_file = open(f"./Train/{file}", 'r')
        for lines in train_file:
            words_list.append([l.lower() for l in lines.split()])
        train_file.close()
        
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

            if word not in comparison_for_word_tag:
                comparison_for_word_tag[word] = {
                    'predicted': [tag]
                }
            else:
                comparison_for_word_tag[word]['predicted'].append(
                    tag
                )
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

# write_PosTags_file()

# write_TransitionProbs_file()

# write_Vocabulary_file()

# write_EmissionProbs_file()

# write_InitialProbs_file()

# TODO: 3) Test Kümesinin HMM kullanılarak POSTaglerin bulunması ve elde edilen sonuçların kütüğe yazılması.




TEST_all_transitions = {}
TEST_all_transition_probabilities = {}
TEST_all_tags_dict = {}
TEST_all_pos_tags_dict = {}
TEST_words_list = []
TEST_all_emission_probs = {}
TEST_temp_previous_tag = 'Q0'
TEST_most_likely = {}
TEST_all_words = {}
TEST_all_unique_words = []
TEST_initial_probs_list = []
TEST_comparison_for_word_tag = {}
sonuc_file_first_line = ""

def TEST_read_and_fill_everything():
    for file in os.listdir("./Test/"):
        train_file = open(f"./Test/{file}", 'r')
        for lines in train_file:
            TEST_words_list.append([l.lower() for l in lines.split()])
        train_file.close()
        
    # TEST_words_list = [ ...,  ["'/'", 'back/rb-hl', 'with/in-hl', 'the/at-hl', 'met/np-hl'], ....]
    for line in TEST_words_list:
        TEST_temp_previous_tag = 'Q0'
        tag = ''
        for words in line:
            word = words.split("/")[0]
            tag = words.split("/")[1]

            # hold every tag of the word, so we can find the
            # most likely one
            if word not in TEST_most_likely:
                TEST_most_likely[word] = {
                    'count': 1,
                    'tags': [tag]
                    }
            else:
                TEST_most_likely[word]['count'] += 1
                TEST_most_likely[word]['tags'].append(tag)
            
            # store all words for the train data
            if word not in TEST_all_words:
                TEST_all_words[word] = 1
            else:
                TEST_all_words[word] += 1

            # store all unique words to use in Vocabulary.txt
            if word not in TEST_all_unique_words:
                TEST_all_unique_words.append(word)

            # store all the tags
            if tag in TEST_all_tags_dict:
                TEST_all_tags_dict[tag] = TEST_all_tags_dict[tag] + 1
            else:
                TEST_all_tags_dict[tag] = 1

            # find and store the total occurance in the line
            if words in TEST_all_emission_probs.keys():
                TEST_all_emission_probs[words] += line.count(words)
            else:
                TEST_all_emission_probs[words] = line.count(words)

            # check if there is a tag before the current one.
            if TEST_temp_previous_tag == '':
                TEST_temp_previous_tag = tag

            # combine 2 tags with seperator '~'
            # this will generate TransitionProbs.txt
            combined_tags = TEST_temp_previous_tag + '~' + tag
            if combined_tags in TEST_all_transitions:
                TEST_all_transitions[combined_tags] += 1
            else:
                TEST_all_transitions[combined_tags] = 1

            # store POSTags counts/frequency for every tag 
            if TEST_temp_previous_tag in TEST_all_pos_tags_dict.keys():
                TEST_all_pos_tags_dict[TEST_temp_previous_tag] += 1
            else:
                TEST_all_pos_tags_dict[TEST_temp_previous_tag] = 1
            TEST_temp_previous_tag = tag

            if word not in TEST_comparison_for_word_tag:
                TEST_comparison_for_word_tag[word] = {
                    'true': [tag]
                }
            else:
                TEST_comparison_for_word_tag[word]['true'].append(
                    tag
                )

def TEST_write_PosTags_file():
    TEST_pos_tags_file = open('Test_PosTags.txt', 'w+')
    TEST_pos_tags_tabulate = []
    for _posTag_key in TEST_all_pos_tags_dict.keys():
        TEST_pos_tags_tabulate.append([
            _posTag_key,
            str(TEST_all_pos_tags_dict[_posTag_key])
            ])

    # sort into given order
    TEST_pos_tags_tabulate = sorted(
        TEST_pos_tags_tabulate,
        key=lambda x:(int(x[1])),
        reverse=True
        )

    print(
        tabulate(
            TEST_pos_tags_tabulate,
            headers=['Tag', 'Tag Frekansı']
            ),
        file=TEST_pos_tags_file
        )

def TEST_write_TransitionProbs_file():
    TEST_transition_probability_file = open('Test_TransitionProbs.txt', 'w+')
    TEST_transition_probability_tabulate = []
    for _transition_key in TEST_all_transitions.keys():
        # split tags with seperator
        _previous_tag = _transition_key.split('~')[0]
        _next_tag = _transition_key.split('~')[1]

        # if previous tag is exists in the POSTags
        if TEST_all_pos_tags_dict[_previous_tag] > 0:
            # use laplace smoothing
            # in order to get rid of zero probabilities
            # P(w,c) =  ( count(w,c) + 1 )/( SUM(count(w,c)) + V ) 
            transition_count = TEST_all_transitions[_transition_key] + 1
            laplace_divider = TEST_all_pos_tags_dict[_previous_tag] + len(TEST_all_tags_dict)
            TEST_all_transition_probabilities[_transition_key] = transition_count / laplace_divider

            # if this is the first tag, then we add the 'Begin' tag to show it
            if _previous_tag == 'Q0':
                _prob = round(TEST_all_transition_probabilities[_transition_key], 9)
                TEST_transition_probability_tabulate.append([
                    'Begin', _next_tag, _prob
                ])
                TEST_initial_probs_list.append([
                    _next_tag, _prob
                ])
            else:
                # if there is another tag before current one
                _prob = round(TEST_all_transition_probabilities[_transition_key], 9)
                TEST_transition_probability_tabulate.append([
                    _previous_tag, _next_tag, _prob
                ])
    # sort into given order
    TEST_transition_probability_tabulate = sorted(
        TEST_transition_probability_tabulate,
        key=lambda x:(x[0],x[1])
        )

    print(
        tabulate(
            TEST_transition_probability_tabulate,
            headers=['Tag A', 'Tag B', 'P(Tag_A, Tag_B)']
            ),
        file=TEST_transition_probability_file
        )

def TEST_write_Vocabulary_file():
    total_word_count = 0
    # find total word count from the data filled while parsing words
    for w, n in TEST_all_words.items():
        total_word_count += n

    TEST_vocabulary_freq_list = []
    TEST_vocabulary_file = open('Test_Vocabulary.txt', 'w+')
    sonuc_file_first_line = f"Toplam kelime sayısı: {total_word_count}\nTekil kelime sayısı: {len(TEST_all_unique_words)}\n"

    TEST_vocabulary_file.write(sonuc_file_first_line + '\n')

    # find most likely ones
    for word in TEST_most_likely.keys():
        # word : { 'tags':[...], 'count':123 }
        tags = TEST_most_likely[word]['tags']
        TEST_vocabulary_freq_list.append([
            word,
            TEST_most_likely[word]['count'],
            max(set(tags), key=tags.count) # find max occurrence in the tags
        ])

    # sort into given order
    TEST_vocabulary_freq_list = sorted(
        TEST_vocabulary_freq_list,
        key=lambda x:(x[1]),
        reverse=True
        )

    print(
        tabulate(
            TEST_vocabulary_freq_list,
            headers=['Kelime', 'Frekans', 'Most Likely Tag']
        ),
        file=TEST_vocabulary_file
    )

def TEST_write_EmissionProbs_file():
    TEST_emission_probability_tabulate = []
    TEST_emission_probability_file = open('Test_EmissionProbs.txt', 'w+')
    # TEST_all_emission_probs.keys   -> 'word/tag'
    # TEST_all_emission_probs.values -> count of the word
    for emission_key in TEST_all_emission_probs.keys():
        word = emission_key.split("/")[0]
        tag = emission_key.split("/")[1]

        # if tag is already exists in the tags
        if TEST_all_tags_dict[tag] > 0:

            # word count / tag count
            TEST_all_emission_probs[emission_key] = TEST_all_emission_probs[emission_key] / TEST_all_tags_dict[tag]

            _prob = round(TEST_all_emission_probs[emission_key], 9)

            TEST_emission_probability_tabulate.append([
                tag, word, _prob
            ])
    emission_probability_tabulate = sorted(TEST_emission_probability_tabulate, key=lambda x:(x[0],x[1]))
    print(
        tabulate(
            emission_probability_tabulate,
            headers=['Tag', 'Kelime', 'P(Kelime, Tag)']
            ),
        file=TEST_emission_probability_file
    )

def TEST_write_InitialProbs_file():
    # InitialProbs.txt file will be filled in here
    TEST_initial_probability_file = open('Test_InitialProbs.txt', 'w+')

    # TEST_initial_probs_list -> [.., ['tag', 'value'], ..]
    _TEST_initial_probs_list = sorted(
        TEST_initial_probs_list,
        key=lambda x:(x[0]) # order by tag
    )
    print(
        tabulate(
            _TEST_initial_probs_list,
            headers=['Tag', 'P(Tag|<s>)']
        ),
        file=TEST_initial_probability_file
    )
    # InitialProbs.txt filled

TEST_read_and_fill_everything()

# TEST_write_PosTags_file()

# TEST_write_TransitionProbs_file()

TEST_write_Vocabulary_file()

# TEST_write_EmissionProbs_file()

# TEST_write_InitialProbs_file()


# After this line, Question 3 - Part 3 starts
ca_file = open(f"./Test/ca41", 'r')
ca_lines = []
ca_words = {}
ca_words_count = 0

for lines in ca_file:
    ca_lines.append([l.lower() for l in lines.split()])
ca_file.close()

for line in ca_lines:
    for words in line:
        word = words.split("/")[0]
        tag = words.split("/")[1]
        ca_words_count += 1

        if word not in ca_words:
            ca_words[word] = {
                'tags': [tag]
            }
        else:
            ca_words[word]['tags'].append(tag)

for word in ca_words.keys():
    # find the most occurence of the tag
    ca_words[word] = max(
        set(ca_words[word]['tags']),
        key=ca_words[word]['tags'].count
    )

for word in comparison_for_word_tag.keys():
    # find the most occurence of the tag
    comparison_for_word_tag[word]['predicted'] = max(
        set(comparison_for_word_tag[word]['predicted']),
        key=comparison_for_word_tag[word]['predicted'].count
    )

for word in TEST_comparison_for_word_tag.keys():
    # find the most occurence of the tag
    TEST_comparison_for_word_tag[word]['true'] = max(
        set(TEST_comparison_for_word_tag[word]['true']),
        key=TEST_comparison_for_word_tag[word]['true'].count
    )

# intersection of TRAIN and TEST tags
intersection_words = [
    value
    for value in comparison_for_word_tag.keys() 
    if value in TEST_comparison_for_word_tag.keys() 
    ]

same_tag = {}
diff_tag = {}

# find same tags with TRAIN and TEST
for word in intersection_words:
    trained_word_tag = comparison_for_word_tag[word]['predicted']
    test_word_tag = TEST_comparison_for_word_tag[word]['true']

    if trained_word_tag != test_word_tag:
        diff_tag[word] = {
            'true': test_word_tag,
            'predicted': trained_word_tag
        }
    else:
        same_tag[word] = test_word_tag

# calcualte % of success
same_rate = len(same_tag)/(len(same_tag)+len(diff_tag))
diff_rate = len(diff_tag)/(len(same_tag)+len(diff_tag))

print(f"Same Tag Count : {len(same_tag)} | Success Rate : {same_rate}")
print(f"Diff Tag Count : {len(diff_tag)} | Success Rate : {diff_rate}")

# find intersection of ca41 tags and TRAIN tags
ca_intersection_words = [
    word
    for word in ca_words.keys()
    if word in comparison_for_word_tag.keys()
]

ca_file_same_tag = {}
ca_file_diff_tag = {}

# find same and different tags of ca41 file
for word in ca_intersection_words:
    trained_word_tag = comparison_for_word_tag[word]['predicted']
    test_word_tag = ca_words[word]

    if trained_word_tag != test_word_tag:
        ca_file_diff_tag[word] = {
            'true': test_word_tag,
            'predicted': trained_word_tag
        }
        # print(
        #     f"Word:{word}\nExpected:{trained_word_tag}\nTrue:{test_word_tag}"
        #     f"\n****************************"
        # )
    else:
        ca_file_same_tag[word] = test_word_tag

ca_file_same_rate = round(len(ca_file_same_tag)/(len(ca_file_same_tag)+len(ca_file_diff_tag)), 3)
ca_file_diff_rate = round(len(ca_file_diff_tag)/(len(ca_file_same_tag)+len(ca_file_diff_tag)), 3)

print(f"Same Tag Count of CA41 : {len(ca_file_same_tag)} | Success Rate : {ca_file_same_rate}")
print(f"Diff Tag Count of CA41 : {len(ca_file_diff_tag)} | Success Rate : {ca_file_diff_rate}")


sonuc_file = open('Sonuc.txt', 'w+')
# total words count in the ca41 file
sonuc_file.write(sonuc_file_first_line)
sonuc_file.write("---------------------------------------\n")

# correct and incorrect POSTag counts
sonuc_file.write(
    f"Dogru POSTag Sayisi  : {len(ca_file_same_tag)}\n"
    f"Dogru POSTag Orani   : {ca_file_same_rate}\n\n"
    f"Yanlis POSTag Sayisi : {len(ca_file_diff_tag)}\n"
    f"Yanlis POSTag Orani  : {ca_file_diff_rate}\n"
)
sonuc_file.write("---------------------------------------\n")
print(
    tabulate(
        _TEST_initial_probs_list,
        headers=['Tag', 'P(Tag|<s>)']
    ),
    file=TEST_initial_probability_file
)


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