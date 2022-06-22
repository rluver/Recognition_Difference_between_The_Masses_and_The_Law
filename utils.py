import pandas as pd
from kiwipiepy import Kiwi

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
