import random

class ExerciseGenerator:
    def __init__(self):
        self.grammar_exercises = [
            {
                'question': 'Complete the sentence: "If I ___ (have) time, I would travel more."',
                'answer': 'had',
                'explanation': 'В условных предложениях второго типа используется Past Simple (had)'
            },
            {
                'question': 'Choose the correct form: "She ___ (go/goes/going) to school every day."',
                'answer': 'goes',
                'explanation': 'В Present Simple для третьего лица единственного числа добавляем -s'
            }
        ]
        
        self.vocabulary_exercises = [
            {
                'question': 'Find a synonym for "happy"',
                'answers': ['glad', 'joyful', 'pleased', 'delighted'],
                'explanation': 'Все эти слова означают "счастливый" с небольшими различиями в интенсивности'
            },
            {
                'question': 'What\'s the opposite of "big"?',
                'answer': 'small',
                'explanation': 'Big и small - базовые антонимы'
            }
        ]

    def get_exercise(self, exercise_type: str, level: str = 'A1'):
        """Возвращает случайное упражнение заданного типа и уровня"""
        if exercise_type == 'grammar':
            return random.choice(self.grammar_exercises)
        elif exercise_type == 'vocabulary':
            return random.choice(self.vocabulary_exercises)
        else:
            return {
                'question': 'Sorry, this type of exercise is not available yet.',
                'answer': None,
                'explanation': None
            } 