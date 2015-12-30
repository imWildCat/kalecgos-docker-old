from django.db import models


# Create your models here.

# class User(models.Model):
#
#     name = models.CharField(max_length=31)
#     email = models.CharField(max_length=127)

class News(models.Model):
    ZONGHEXINWEN = 'ZH'
    XINWENTOUTIAO = 'XT'
    XINWENJUJIAO = 'XJ'
    YUANXIDONGTAI = 'YX'
    MEITICAIDA = 'MT'
    JIANGZUOBAOGAO = 'JB'
    TONGZHIGONGGAO = 'TZ'
    JIANGZUOYUGAO = 'JY'
    XIAOYUANCHUANZHEN = 'XY'
    YINGXIANGCAIDA = 'YX'
    LINGDAOJIANGHUA = 'LD'
    CAIDALUNTAN = 'LT'
    RENWUFENGCAI = 'RW'
    SHIPINCAIDA = 'SP'

    CATEGORY_CHOICES = (
        (ZONGHEXINWEN, '综合新闻'),
        (XINWENTOUTIAO, '新闻头条'),
        (XINWENJUJIAO, '新闻聚焦'),
        (YUANXIDONGTAI, '院系动态'),
        (MEITICAIDA, '媒体财大'),
        (JIANGZUOBAOGAO, '讲座报告'),
        (TONGZHIGONGGAO, '通知公告'),
        (JIANGZUOYUGAO, '讲座预告'),
        (XIAOYUANCHUANZHEN, '校园传真'),
        (YINGXIANGCAIDA, '影像财大'),
        (LINGDAOJIANGHUA, '领导讲话'),
        (CAIDALUNTAN, '财大论坛'),
        (RENWUFENGCAI, '人物风采'),
        (SHIPINCAIDA, '视频财大')
    )

    title = models.CharField(max_length=127, null=False)
    category = models.CharField(max_length=4,
                                null=False,
                                choices=CATEGORY_CHOICES)
    date = models.DateTimeField(null=False)
    editor = models.CharField(max_length=31, null=False)
    content = models.TextField(null=False)
