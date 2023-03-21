from rest_framework import serializers
from .models import Poll,Choice,Vote

class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'
        

class ChoiceListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # map the id field to the corresponding Choice instance
        choice_mapping = {choice.id: choice for choice in instance}
        choices = []

        # update or create each choice in the validated_data
        for choice_data in validated_data:
            choice_id = choice_data.get('id', None)
            if choice_id:
                choice = choice_mapping.pop(choice_id)
                choice.choice_text = choice_data.get('choice_text', choice.choice_text)
                choice.save()
                choices.append(choice)
            else:
                choices.append(Choice(**choice_data))

        # delete any remaining choices
        for choice in choice_mapping.values():
            choice.delete()

        return choices



class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'