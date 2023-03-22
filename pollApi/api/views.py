from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Choice,Poll,Vote
from .serializers import PollSerializer,ChoiceSerializer,ChoiceListSerializer,VoteSerializer
from rest_framework import status
# Create your views here.

#Get All routes
@api_view(['GET'])
def routes(request):
    data ={
           "api/auth": {
                        'Create new user':'create-user/',
                        'Login user':'login-user/',
                        'update user':'update-user/',
                        'Generate Token for existing user':'token/',
                        'Generate Access Token':'token/refresh/',
        
           },
           "api/":{
                
                'poll/':"list of all polls",
                'poll/mypolls/':"list of polls by logined user",
                'poll/addpolls/':"Create Poll",
                'poll/editpolls/<int:poll_id>/':"edit existing poll",
                'poll/deletepolls/<int:poll_id>/':"delete existing poll",
                'poll/vote/<int:poll_id>/':"cast vote for a poll",
                'poll/polldetails/<int:poll_id>/': "Poll vote details"
            }
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def polls_list(request):
   
    polls = Poll.objects.all()
    serializer = PollSerializer(polls,many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_by_user(request):
    polls = Poll.objects.filter(owner=request.user)
    serializer = PollSerializer(polls,many=True)
    return Response(serializer.data)


@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def polls_add(request):
    if request.method == 'POST':
        serializer = PollSerializer(data=request.data, partial=True)
        print(serializer)
        if serializer.is_valid():
            poll = serializer.save(owner=request.user)
            print(poll)
            print(request.data)

            # Save choices
            new_choice1 = Choice.objects.create(poll=poll, choice_text=request.data['choice1'])
            new_choice1.save()
            
            new_choice2 = Choice.objects.create(poll=poll, choice_text=request.data['choice2'])
            new_choice2.save()
            

            return Response({
                "message": "Poll & Choices added successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"format": {
            "text":"poll text",
            "choice1":"poll choice 1",
            "choice2":"poll choice 2",
        }}, status=status.HTTP_200_OK)
    


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def polls_edit(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    if request.user != poll.owner:
        return Response({"message": "You are not authorized to edit this poll"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        serializer = PollSerializer(instance=poll, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Poll updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        serializer = PollSerializer(instance=poll)
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def polls_delete(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user != poll.owner:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    poll.delete()
    return Response({"message": "Poll deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



#editing choices to exsisting poll
@api_view(['PUT','GET'])
@permission_classes([IsAuthenticated])
def edit_choice(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    choices = poll.choice_set.all()
    if request.method == "PUT":
        if request.user != poll.owner:
            return Response({'error': 'You do not have permission to edit this poll.'}, status=status.HTTP_403_FORBIDDEN)

        choice_1 = poll.choice_set.filter(id=request.data.get('choice_1_id')).first()
        choice_2 = poll.choice_set.filter(id=request.data.get('choice_2_id')).first()
        

        if not choice_1 or not choice_2:
            return Response({'error': 'One or both choices do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        new_choice_1_data = {
            'text': request.data.get('choice_1_text', choice_1.choice_text)
        }
        new_choice_2_data = {
            'text': request.data.get('choice_2_text', choice_2.choice_text)
        }
        

        serializer_1 = Choice(choice_1.id, choice_text=new_choice_1_data['text'],poll=poll)
        serializer_2 = Choice(choice_2.id, choice_text=new_choice_2_data['text'],poll=poll)

        if serializer_1 and serializer_2:
            serializer_1.save()
            serializer_2.save()
            serializer_1.vote_set.all().delete()
            serializer_1.vote_set.all().delete()
            return Response({'message': 'Choices updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'One or both choices are invalid.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        poll_serializer = PollSerializer(poll)
        choiceserializer = ChoiceSerializer(choices,many=True)
        data = {
        'poll': poll_serializer.data,
        'choices': choiceserializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

        

        
        
@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def poll_vote(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
        choices = poll.choice_set.all()
    except Poll.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        poll = Poll.objects.get(pk=poll_id)
        if poll.active:
            choice_id = request.data.get('choice')
            if not poll.user_can_vote(request.user):
                return Response({"message": "You already voted this poll"}, status=status.HTTP_400_BAD_REQUEST)
            if choice_id:
                try:
                    choice = Choice.objects.get(id=choice_id)
                    vote = Vote(user=request.user,poll=poll,choice=choice)
                    vote.save()
                    return Response({"message": "Your Vote is Added Succesfully"},status=status.HTTP_201_CREATED)
                except Choice.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({"message": "No choice selected"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Poll is not active"},status=status.HTTP_400_BAD_REQUEST)
    else:
        poll_serializer = PollSerializer(poll)
        choiceserializer = ChoiceSerializer(choices,many=True)
        data = {
        'poll': poll_serializer.data,
        'choices': choiceserializer.data,
        "message": "You can cast vote only once. please choose your choice carefully",
        "format":{
            "choice":"choiceid (without quotes)"
        }
    }
        return Response(data, status=status.HTTP_200_OK)
    

#Poll vote detailes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def poll_detail(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    choices = poll.choice_set.all()

    choice_text1 = choices[0].choice_text
    choice_text2 = choices[1].choice_text

    votes_for_1 = choices[0].vote_set.all().count()
    votes_for_2 = choices[1].vote_set.all().count()


    poll_serializer = PollSerializer(poll)
    choiceserializer = ChoiceSerializer(choices,many=True)
    data = {
        'poll': poll_serializer.data,
        'choices': choiceserializer.data,
        'votes':{
                choice_text1:votes_for_1,
                choice_text2:votes_for_2
        }
        }
    return Response(data, status=status.HTTP_200_OK)