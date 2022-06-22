import pandas as pd
import numpy as np
import itertools
from collections import Counter
from kiwipiepy import Kiwi


def sum_count_by_all(df, judgement, what):
    df[f'{what}_count'] = df[f'preprocessed_{what}s'].apply(lambda x: Counter(list(itertools.chain(*x))))
    objects = df.query(f'judgement=={judgement}').loc[:, f'{what}_count']
    
    count = Counter()
    for obj in objects:
        count.update(obj)

    return count


def sum_count_by_each(df, judgement, what):
    df[f'{what}_count'] = df[f'preprocessed_{what}s'].apply(lambda x: Counter(np.unique(list(itertools.chain(*x)))))
    return Counter(itertools.chain(*df.query(f'judgement=={judgement}').loc[:, f'{what}_count']))


def sum_count_by_video(df, judgement, what):
    df[f'{what}_count'] = df[f'preprocessed_{what}s'].apply(lambda x: Counter(list(itertools.chain(*x))))

    count = Counter()
    for video in df.video_id.unique():
        count_by_video = Counter(np.unique(list(itertools.chain(*df.query(f'judgement=={judgement} and video_id=="{video}"').loc[:, f'{what}_count']))))
        count.update(count_by_video)
        
    return count 


def sum_count(df, judgement, what, by):
    if by == 'all':
        return sum_count_by_all(df, judgement, what)

    if by == 'each':
        return sum_count_by_each(df, judgement, what)

    if by == 'video':
        return sum_count_by_video(df, judgement, what)


def get_count(df: pd.DataFrame, what='subject', by='each'):
    return [sum_count(df, i, what, by) for i in range(3)]
    
class PostpositionRemover:
    def __init__(self):
        self.kiwi = Kiwi()
        self.kiwi.prepare()
        
        self.remove_list = {
            'JX', 'JKS', 'JKO', 'JKG', 'JKC', 
            'XSN', 
            'EC', 
            'IC', 
            'EF','ETM', 
            'NNB', 
            'MM',
            'SF', 'SW', 
            'VCP',            
            'XSV'
            }

    def __call__(self, text: dict) -> tuple:
        return self.get_kiwi_results(text)

    def _get_last_postposition_index(self, analyzed_text: list) -> int:
        for i in range(len(analyzed_text)-1, -1, -1):            
            if analyzed_text[i][1] in self.remove_list:                
                index = analyzed_text[i][2]
            else:
                return index

    def _remove_postposition(self, texts: list) -> list:
        if texts is None:
            return []
        
        texts_with_kiwi_analyzed: object = self.kiwi.analyze(texts)

        texts_without_postposition = []
        for original_text, analyzed_text in zip(texts, texts_with_kiwi_analyzed):
            analyzed_text = analyzed_text[0][0]
            if len(analyzed_text) == 0:
                return []
            
            if analyzed_text[-1][1] in self.remove_list:
                index = self._get_last_postposition_index(analyzed_text)
                texts_without_postposition.append(original_text[:index])
            else:
                texts_without_postposition.append(original_text)

        return texts_without_postposition

    def get_kiwi_results(self, etri_analyzed_texts: dict) -> tuple:
        subjects_without_postposition = []
        objects_without_postposition = []

        for i in range(len(etri_analyzed_texts)):
            subjects, objects = etri_analyzed_texts.get(i).get('dependency').values()

            subject_without_postposition: list = self._remove_postposition(subjects)
            object_without_postposition: list = self._remove_postposition(objects)

            subjects_without_postposition.append(subject_without_postposition)
            objects_without_postposition.append(object_without_postposition)

        return subjects_without_postposition, objects_without_postposition
