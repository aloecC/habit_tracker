from rest_framework.exceptions import ValidationError


class RewardOrNiceHabitValidator:
    """Валидатор для проверки корректного указания вознаграждения/приятной привычки"""
    def __init__(self, reward_field, associated_habit_field):
        self.reward_field = reward_field
        self.associated_habit_field = associated_habit_field

    def __call__(self, attrs):
        reward = attrs.get(self.reward_field)
        associated_habit = attrs.get(self.associated_habit_field)

        if reward and associated_habit:
            raise ValidationError(
                "Вы не можете указать одновременно вознаграждение и связанную приятную привычку. "
                "Выберите что-то одно."
            )

        if not reward and not associated_habit:
            raise ValidationError(
                "Вы должны указать либо вознаграждение, либо связанную приятную привычку."
            )

        if associated_habit and not associated_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна быть приятной (is_pleasant=True)."
            )