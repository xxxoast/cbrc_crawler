# -*- coding:utf-8 -*- 
# constants for chinese_to_arabic

from misc import unicode2utf8

CN_NUM = {
    u'〇' : 0, u'一' : 1, u'二' : 2, u'三' : 3, u'四' : 4, u'五' : 5, u'六' : 6, u'七' : 7, u'八' : 8, u'九' : 9, u'零' : 0,
    u'壹' : 1, u'贰' : 2, u'叁' : 3, u'肆' : 4, u'伍' : 5, u'陆' : 6, u'柒' : 7, u'捌' : 8, u'玖' : 9, u'貮' : 2, u'两' : 2,
}
# CN_NUM = {unicode2utf8(k):v for k,v in CN_NUM.items()}

CN_UNIT = {
    u'十' : 10,
    u'拾' : 10,
    u'百' : 100,
    u'佰' : 100,
    u'千' : 1000,
    u'仟' : 1000,
    u'万' : 10000,
    u'萬' : 10000,
    u'亿' : 100000000,
    u'億' : 100000000,
    u'兆' : 1000000000000,
}
# CN_UNIT = {unicode2utf8(k):v for k,v in CN_UNIT.items()}

def chinese_to_arabic(cn):
    unit = 0   # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val


# TODO: make a full unittest
def test():
    test_dig = [u'八',
                u'十一',
                u'一百二十三',
                u'一千二百零三',
                u'一万一千一百零一',
                u'十万零三千六百零九',
                u'一百二十三万四千五百六十七',
                u'一千一百二十三万四千五百六十七',
                u'一亿一千一百二十三万四千五百六十七',
                u'一百零二亿五千零一万零一千零三十八']
    for cn in test_dig:
        x = chinese_to_arabic(cn)
        print(cn, x)
    assert x == 10250011038

if __name__ == '__main__':
    test()