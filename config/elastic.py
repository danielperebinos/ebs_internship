from django.conf import settings
from drf_util import elastic

# Connection
elastic.ElasticUtil.hosts = [settings.ELASTIC_HOST]

# Prefixes
elastic.ElasticUtil.index_prefix = settings.ELASTIC_INDEX_PREFIX

# Indexes
elastic.ElasticUtil.text_index = 'text'


es = elastic.ElasticUtil()
es.init_indexes()

