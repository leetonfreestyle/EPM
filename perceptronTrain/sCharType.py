# -*- coding: utf-8 -*-
class sCharType(object):
    def __init__(self):
        self.numSet = set([u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'０',u'１', u'２',
                          u'３', u'４', u'５', u'６', u'７', u'８', u'９', u'.', u'·', u'．', u'%', u'‰'])
        self.chineseNumset = set([u'〇', u'○', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'零', 
            u'壹', u'贰', u'叁', u'肆', u'伍', u'陆', u'柒', u'捌', u'玖', u'拾', u'伯', u'仟', u'百',
            u'俩', u'两', u'兩', u'千', u'萬', u'万', u'亿', u'廿', u'卅', u'億', u'點'])
       
        self.englishCharSet = set([u'Ａ', u'Ｂ', u'Ｃ', u'Ｄ', u'Ｅ', u'Ｆ', u'Ｇ', u'Ｈ', u'Ｉ', u'Ｊ', u'Ｋ', u'Ｌ', u'Ｍ', u'Ｎ', u'Ｏ', u'Ｐ', u'Ｑ', 
            u'Ｒ', u'Ｓ',u'Ｔ', u'Ｕ', u'Ｖ', u'Ｗ', u'Ｘ', u'Ｙ', u'Ｚ', u'ａ', u'ｂ', u'ｃ', u'ｄ', u'ｅ', u'ｆ', u'ｇ', u'ｈ', 
            u'ｉ', u'ｊ', u'ｋ', u'ｌ', u'ｍ', u'ｎ', u'ｏ', u'ｐ', u'ｑ', u'ｒ', u'ｓ', u'ｔ', u'ｕ', u'ｖ', u'ｗ', u'ｘ', u'ｙ', 
            u'ｚ', u'a', u'b', u'c', u'd', u'e', 'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'o', u'p', u'q', u'r', 
            u's', u't', u'u', u'v', u'w', u'x', 'y', u'z', u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K', 
            u'L', u'M', u'N', u'O', u'P', u'Q', 'R', u'S', u'T', u'U', u'V', u'W', u'X', u'Y', u'Z'])
       
        self.puncSet = set([u'!', u'"', u'$', u'\'', u'(', u')', u'*', u',', u'-', u'.', u'/', u':', u';', u'<', u'>', u'?', u'[', u'\\',
            u']', u'`', u'{', u'}', u'~', u'、', u'。', u'·', u'¨',u'—', u'～', u'…', u'‘', u'’', u'“', u'”', u'〔', u'〕', 
            u'〈', u'〉', u'《', u'》', u'「', u'」', u'『', u'』', u'【', u'】', u'±', u'×', u'∶', u'∧', u'∨', u'∥', u'≠', 
            u'′', u'‰', u'★', u'○', u'●', u'□', u'△', 'u▲', u'※', u'→', u'！', u'＂', u'＃',u'％', u'＆', u'＇', u'（', u'）',
            u'＊', u'＋', u'，', u'－', u'．', u'／', u'：', u'；', u'＜', u'＝', u'＞', u'？', u'［', u'］', u'＿', u'｀', u'｛', 
            u'｝', u'︰', u'﹔', u'﹕', u'﹖', u'﹗', u'─', u'━', u'│'])
       
        self.dateSet = set([u'年', u'月', u'日', u'时', u'分', u'秒', u'点',u'天'])

        self.familyNameSet = set([u'李', u'王', u'张', u'刘', u'陈', u'杨', u'黄', u'赵', u'吴', u'周', u'徐', u'孙', u'马', u'朱', u'胡', u'郭', u'何', 
            u'高', u'林', u'罗', u'郑', u'梁', u'谢', u'宋', u'唐', u'许', u'韩', u'冯', u'邓', u'曹', u'彭', u'曾', u'肖', u'田', 
            u'董', u'袁', u'潘', u'于', u'蒋', u'蔡', u'余', u'杜', u'叶', u'程', u'苏', u'魏', u'吕', u'丁', u'任', u'沈', u'姚', 
            u'卢', u'姜', u'崔', u'钟', u'谭', u'陆', u'汪', u'范', u'金', u'石', u'廖', u'贾', u'夏', u'韦', u'傅', u'方', u'白', 
            u'邹', u'孟', u'熊', u'秦', u'邱', u'江', u'尹', u'薛', u'闫', u'段', u'雷', u'侯', u'龙', u'史', u'陶', u'黎', u'贺', 
            u'顾', u'毛', u'郝', u'龚', u'邵', u'万', u'钱', u'严', u'覃', u'武', u'戴', u'莫', u'孔', u'向', u'汤'])

        return

    def isPunc(self,ch):
        return ch in self.puncSet

    def isEnChar(self,ch):
        return ch in self.englishCharSet


    def isChineseNum(self,ch):
        return ch in self.chineseNumset


    def isNum(self,ch):
        return ch in self.numSet


    def isDate(self,ch):
        return ch in self.dateSet


    def isFamilyName(self,ch):
        return ch in self.familyNameSet

    def containsDate(self,word):
        for char in word:
            if self.isDate(char):
                return True
        return False

    def containsPunc(self,word):
        for char in word:
            if self.isPunc(char):
                return True
        return False

    def containsEnChar(self,word):
        for char in word:
            if self.isEnChar(char):
                return True
        return False

    def containsChineseNum(self,word):
        for char in word:
            if self.isChineseNum(char):
                return True
        return False

    def containsNum(self,word):
        for char in word:
            if self.isNum(char):
                return True
        return False

    def containsFamilyName(self,word):
        for char in word:
            if self.isFamilyName(char):
                return True
        return False
    


    
