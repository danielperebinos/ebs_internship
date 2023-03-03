from config.elastic import es
from apps.tasks.models import Comment
from apps.tasks.serializers import CommentSerializer


def upload_comment_to_elastic(comment: Comment):
    comment = dict(CommentSerializer(comment).data)
    try:
        es.add_document(es.text_index, comment)
    except Exception as e:
        print(f'Exception with message: {str(e)}')


def upload_comments_to_elastic(queryset=None):
    queryset = Comment.objects.all() if not queryset else queryset
    for comment in queryset:
        upload_comment_to_elastic(comment)
