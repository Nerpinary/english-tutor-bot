class ExerciseGenerator:
    def generate_exercise(self, type: str):
        exercises = {
            'grammar': [
                "Complete the sentence: If I ___ (have) time, I would travel more.",
                "Choose correct form: She (go/goes/going) to school every day."
            ],
            'vocabulary': [
                "Find a synonym for 'happy'",
                "Use 'conduct' in a sentence"
            ]
        }
        return exercises[type][0]  # Можно рандомизировать 