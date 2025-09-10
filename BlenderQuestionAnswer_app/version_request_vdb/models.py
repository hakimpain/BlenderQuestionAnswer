from django.db import models

class VectordbBlenderDocs(models.Model):
    path = models.CharField()
    version = models.CharField()
    embedding_model_name = models.CharField()
    embedding_source = models.IntegerField()
    vector_db_source = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.version