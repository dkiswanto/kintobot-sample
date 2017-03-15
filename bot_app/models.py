from django.db import models


class Task(models.Model):
    due_date = models.DateTimeField()
    text = models.TextField(max_length=1024)
    group_id = models.CharField(max_length=255)


class Result(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE) #reference task_id
    revoke_id = models.CharField(max_length=255)


# class Vote(models.Model):
#     name = models.CharField()
#
#
# class VoteOption(models.Model):
#     vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
#     option = models.CharField()
#
#     class Meta:
#         unique_together = ("vote", "option")
#
#
# class VoteSelected(models.Model):
#     vote_option = models.ForeignKey(VoteOption, on_delete=models.CASCADE)
#     name = models.CharField(unique=True)
#
#     class Meta:
#         unique_together = ("vote_option", "name")
